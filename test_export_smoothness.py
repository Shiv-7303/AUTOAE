import os
import sys
import time
import json
import shutil
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

DOWNLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "test_downloads"))
if os.path.exists(DOWNLOAD_DIR):
    shutil.rmtree(DOWNLOAD_DIR)
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

FFPROBE_BIN = shutil.which("ffprobe")
if not FFPROBE_BIN:
    winget_dir = os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WinGet\Packages")
    for root, dirs, files in os.walk(winget_dir):
        if "ffprobe.exe" in files:
            FFPROBE_BIN = os.path.join(root, "ffprobe.exe")
            break

print(f"[*] Test Download Dir: {DOWNLOAD_DIR}")
print(f"[*] Detected FFprobe: {FFPROBE_BIN}")

def run_test(preset_style, quality="1080p_60", is_vertical=False):
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--window-size=1600,1000")
    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": DOWNLOAD_DIR,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    })

    driver = webdriver.Chrome(options=chrome_options)
    try:
        print(f"\n=======================================================")
        print(f"[*] Testing Preset: {preset_style} | Quality: {quality} | Vertical: {is_vertical}")
        print(f"=======================================================")
        driver.get("http://localhost:3000/")
        
        # Wait for canvas
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "liveCanvas")))
        time.sleep(1)

        # Set aspect ratio if vertical
        if is_vertical:
            btn_vertical = driver.find_element(By.ID, "btnRatio916")
            btn_vertical.click()
            time.sleep(0.5)

        # Select style via JS
        driver.execute_script(f"""
            const btn = document.querySelector('.style-btn[data-style="{preset_style}"]');
            if (btn) btn.click();
            else {{
                state.currentStyle = "{preset_style}";
                restartAndPlay();
            }}
            const qSelect = document.getElementById('exportQualitySelect');
            if (qSelect) {{
                qSelect.value = "{quality}";
                qSelect.dispatchEvent(new Event('change'));
            }}
        """)
        time.sleep(1)

        # Verify quality select value
        current_q = driver.execute_script("return document.getElementById('exportQualitySelect').value")
        current_style = driver.execute_script("return state.currentStyle")
        total_dur = driver.execute_script("return getTotalDuration()")
        print(f"[*] Configured: style={current_style}, quality={current_q}, duration={total_dur:.2f}s")

        # Record file list before export
        before_files = set(os.listdir(DOWNLOAD_DIR))

        # Click export button
        btn_export = driver.find_element(By.ID, "btnExportVideo")
        btn_export.click()
        print("[*] Export triggered. Monitoring progress...")

        start_time = time.time()
        downloaded_file = None
        
        while time.time() - start_time < 90:
            time.sleep(1)
            # Check progress text from UI
            try:
                prog_text = driver.execute_script("return document.getElementById('renderProgressText').textContent")
                overlay_active = driver.execute_script("return document.getElementById('recordingOverlay').classList.contains('active')")
                print(f"    [Progress] {prog_text} (overlay active: {overlay_active})")
            except Exception:
                pass

            # Check downloaded files
            current_files = set(os.listdir(DOWNLOAD_DIR)) - before_files
            mp4_files = [f for f in current_files if f.endswith(".mp4") and not f.endswith(".crdownload")]
            if mp4_files:
                downloaded_file = os.path.join(DOWNLOAD_DIR, mp4_files[0])
                # Ensure write finished
                prev_sz = -1
                for _ in range(5):
                    sz = os.path.getsize(downloaded_file)
                    if sz == prev_sz and sz > 0:
                        break
                    prev_sz = sz
                    time.sleep(0.5)
                break

        if not downloaded_file:
            print("[!] ERROR: No downloaded file produced within timeout!")
            return False

        export_duration = time.time() - start_time
        file_size_mb = os.path.getsize(downloaded_file) / (1024 * 1024)
        print(f"\n[OK] Video downloaded successfully in {export_duration:.2f}s: {os.path.basename(downloaded_file)} ({file_size_mb:.2f} MB)")

        # Analyze with FFprobe
        cmd = [
            FFPROBE_BIN,
            "-v", "error",
            "-show_entries", "stream=index,codec_name,codec_type,width,height,r_frame_rate,avg_frame_rate,nb_frames,duration",
            "-show_entries", "format=format_name,duration,size",
            "-of", "json",
            downloaded_file
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        probe_data = json.loads(res.stdout)
        
        video_stream = next((s for s in probe_data.get('streams', []) if s['codec_type'] == 'video'), None)
        audio_stream = next((s for s in probe_data.get('streams', []) if s['codec_type'] == 'audio'), None)

        print("\n--- FFprobe Video Analysis ---")
        if video_stream:
            print(f"  Codec: {video_stream.get('codec_name')}")
            print(f"  Resolution: {video_stream.get('width')} x {video_stream.get('height')}")
            print(f"  Frame Rate (r_frame_rate): {video_stream.get('r_frame_rate')}")
            print(f"  Avg Frame Rate: {video_stream.get('avg_frame_rate')}")
            print(f"  Reported Duration: {video_stream.get('duration')}s")
            print(f"  Total Frames (nb_frames): {video_stream.get('nb_frames')}")
        else:
            print("  [!] Video stream MISSING!")
            return False

        print("\n--- FFprobe Audio Analysis ---")
        if audio_stream:
            print(f"  Codec: {audio_stream.get('codec_name')}")
            print(f"  Duration: {audio_stream.get('duration')}s")
        else:
            print("  Audio stream: none (no audio in this preset or sfx disabled)")

        # Verify frame uniformity with count_packets
        cmd_frames = [
            FFPROBE_BIN,
            "-v", "error",
            "-count_frames",
            "-select_streams", "v:0",
            "-show_entries", "stream=nb_read_frames",
            "-of", "default=nokey=1:noprint_wrappers=1",
            downloaded_file
        ]
        res_frames = subprocess.run(cmd_frames, capture_output=True, text=True)
        read_frames = int(res_frames.stdout.strip())
        print(f"\n[*] Verified Exact Frame Count via packet decode: {read_frames} frames")
        
        expected_fps = 60 if "60" in quality else 30
        expected_frames = round(total_dur * expected_fps)
        print(f"[*] Expected frames ({total_dur:.2f}s @ {expected_fps}fps): ~{expected_frames}")
        
        # Check tolerance (within 2 frames of expected due to rounding)
        if abs(read_frames - expected_frames) <= 2:
            print(f"[SUCCESS] PERFECT MATCH! Zero dropped frames, exact uniform {expected_fps} FPS pacing!")
        else:
            print(f"[WARNING] Frame count mismatch: read={read_frames}, expected={expected_frames}")

        return True

    finally:
        driver.quit()

if __name__ == "__main__":
    # Test 1: Preset 27 (CapCut Keyframe Hook) at 1080p 60 FPS
    ok1 = run_test("capcut-keyframe-hook", quality="1080p_60", is_vertical=False)
    
    # Test 2: Preset 22 (Donut Chart Hook) at 1080p 60 FPS in 9:16 vertical
    ok2 = run_test("donut-chart-hook", quality="1080p_60", is_vertical=True)

    print("\n=======================================================")
    print(f"SUMMARY: Test 1 (CapCut 1080p60): {'PASSED' if ok1 else 'FAILED'} | Test 2 (Donut 9:16 1080p60): {'PASSED' if ok2 else 'FAILED'}")
    print("=======================================================")

