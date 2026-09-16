import os
import sys
import time
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

def run_test():
    artifacts_dir = r"C:\Users\shiva\.gemini\antigravity\brain\c529db9f-4476-4403-9053-97e2af00d2e5"
    chrome_options = Options()
    chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--window-size=1400,900')
    chrome_options.add_argument('--mute-audio')
    
    driver = webdriver.Chrome(options=chrome_options)
    try:
        print("1. Navigating to http://localhost:3000 ...")
        driver.get('http://localhost:3000')
        time.sleep(2)
        
        # Check category buttons
        all_btn = driver.find_element(By.CSS_SELECTOR, '.cat-btn[data-filter="all"]')
        motion_btn = driver.find_element(By.CSS_SELECTOR, '.cat-btn[data-filter="motion"]')
        print(f"All button text: '{all_btn.text}', Motion button text: '{motion_btn.text}'")
        assert "All (27)" in all_btn.text, f"Expected 'All (27)', got {all_btn.text}"
        assert "Motion (6)" in motion_btn.text, f"Expected 'Motion (6)', got {motion_btn.text}"
        print("[OK] Category counters verified: All (27), Motion (6)")
        
        # 2. Select Preset 27: CapCut Keyframe Editing Hook
        btn27 = driver.find_element(By.CSS_SELECTOR, '[data-style="capcut-keyframe-hook"]')
        assert btn27 is not None, "Preset 27 button not found"
        driver.execute_script("arguments[0].click();", btn27)
        time.sleep(1)
        print("[OK] Clicked Preset 27 button")
        
        # 3. Verify Quick Controls are visible in Presets Tab
        quick_controls = driver.find_element(By.ID, "quickCapCutControls")
        assert quick_controls.is_displayed(), "quickCapCutControls should be visible"
        print("[OK] quickCapCutControls is displayed")
        
        # Verify default duration is 5.0s
        dur_badge = driver.find_element(By.ID, "animDurationBadge")
        print(f"Duration badge: {dur_badge.text}")
        assert "5.0" in dur_badge.text, f"Expected 5.0s duration, got {dur_badge.text}"
        
        # 4. Capture keyframe choreography milestones
        # t = 0.2s (Phase 1: Full-frame Zoom-in on Player Footage)
        driver.execute_script("pause(); seekTo(0.2);")
        time.sleep(0.5)
        path_02 = os.path.join(artifacts_dir, "capcut_01_zoom_player.png")
        driver.save_screenshot(path_02)
        print(f"[OK] Captured {path_02} at t=0.2s")
        
        # t = 1.0s (Phase 1 End: Full CapCut UI Revealed)
        driver.execute_script("pause(); seekTo(1.0);")
        time.sleep(0.5)
        path_10 = os.path.join(artifacts_dir, "capcut_02_full_ui.png")
        driver.save_screenshot(path_10)
        print(f"[OK] Captured {path_10} at t=1.0s")
        
        # t = 2.0s (Phase 2: Timeline Dive into Diamond Keyframes)
        driver.execute_script("pause(); seekTo(2.0);")
        time.sleep(0.5)
        path_20 = os.path.join(artifacts_dir, "capcut_03_timeline_dive.png")
        driver.save_screenshot(path_20)
        print(f"[OK] Captured {path_20} at t=2.0s")
        
        # t = 4.0s (Phase 3: Keyframe Tracking Drift along Track 1)
        driver.execute_script("pause(); seekTo(4.0);")
        time.sleep(0.5)
        path_40 = os.path.join(artifacts_dir, "capcut_04_tracking_drift.png")
        driver.save_screenshot(path_40)
        print(f"[OK] Captured {path_40} at t=4.0s")
        
        # 5. Test Custom Image Upload to Player Screen
        upload_input = driver.find_element(By.ID, "quickCapCutUpload")
        thumb_path = os.path.abspath(r"e:\autoae\test_thumb.png")
        upload_input.send_keys(thumb_path)
        time.sleep(1)
        
        # Verify status text updated
        status_el = driver.find_element(By.ID, "quickCapCutStatus")
        print(f"Upload status: {status_el.text}")
        assert "Footage Loaded" in status_el.text, f"Expected footage loaded, got {status_el.text}"
        
        # Capture screenshot with custom uploaded image at t=0.2s
        driver.execute_script("pause(); seekTo(0.2);")
        time.sleep(0.5)
        path_custom_img = os.path.join(artifacts_dir, "capcut_05_custom_media_zoom.png")
        driver.save_screenshot(path_custom_img)
        print(f"[OK] Captured {path_custom_img} with uploaded media")
        
        # 6. Test Custom Text and Custom Clip Name
        text_input = driver.find_element(By.ID, "quickCapCutText")
        driver.execute_script("arguments[0].value = 'HOW TO EDIT VIRAL HOOKS'; arguments[0].dispatchEvent(new Event('input'));", text_input)
        
        clip_input = driver.find_element(By.ID, "quickCapCutClipName")
        driver.execute_script("arguments[0].value = 'MY_VIRAL_HOOK_V1.mp4'; arguments[0].dispatchEvent(new Event('input'));", clip_input)
        time.sleep(0.5)
        
        # Reset image so stripes and new headline show
        reset_btn = driver.find_element(By.ID, "quickCapCutReset")
        driver.execute_script("arguments[0].click();", reset_btn)
        time.sleep(0.5)
        
        driver.execute_script("pause(); seekTo(0.2);")
        time.sleep(0.5)
        path_custom_text = os.path.join(artifacts_dir, "capcut_06_custom_headline.png")
        driver.save_screenshot(path_custom_text)
        print(f"[OK] Captured {path_custom_text} with custom headline")
        
        # 7. Test 9:16 Vertical Mobile Aspect Ratio
        btn916 = driver.find_element(By.ID, "btnRatio916")
        driver.execute_script("arguments[0].click();", btn916)
        time.sleep(1)
        
        driver.execute_script("pause(); seekTo(0.5);")
        time.sleep(0.5)
        path_vertical_05 = os.path.join(artifacts_dir, "capcut_07_vertical_player.png")
        driver.save_screenshot(path_vertical_05)
        print(f"[OK] Captured {path_vertical_05} in 9:16 vertical mode at t=0.5s")
        
        driver.execute_script("pause(); seekTo(2.2);")
        time.sleep(0.5)
        path_vertical_22 = os.path.join(artifacts_dir, "capcut_08_vertical_dive.png")
        driver.save_screenshot(path_vertical_22)
        print(f"[OK] Captured {path_vertical_22} in 9:16 vertical mode at t=2.2s")
        
        # Switch back to 16:9
        btn169 = driver.find_element(By.ID, "btnRatio169")
        driver.execute_script("arguments[0].click();", btn169)
        time.sleep(0.5)
        
        # 8. Check console errors
        logs = driver.get_log('browser')
        severe_errors = [l for l in logs if l['level'] == 'SEVERE' and 'favicon' not in l['message'].lower()]
        print(f"Browser logs: {len(logs)} entries, {len(severe_errors)} severe errors")
        if severe_errors:
            for err in severe_errors:
                print("SEVERE ERROR:", err)
        assert len(severe_errors) == 0, f"Encountered {len(severe_errors)} severe console errors!"
        print("[SUCCESS] All CapCut Preset 27 Verification Tests Passed with 0 Console Errors!")
        
    finally:
        driver.quit()

if __name__ == '__main__':
    run_test()
