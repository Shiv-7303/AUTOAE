import os
import sys
import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def run_tests():
    print("=== AUTOMATED VERIFICATION OF AUTOAE TEXT PRESETS ===")
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1600,1000")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.set_capability('goog:loggingPrefs', {'browser': 'ALL'})

    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        driver.get("http://localhost:3000")
        time.sleep(2)

        # 1. Check Console Logs
        logs = driver.get_log('browser')
        errors = [l for l in logs if l['level'] == 'SEVERE']
        # Filter out harmless 404 for favicon.ico
        js_errors = [e for e in errors if 'favicon.ico' not in e['message']]
        print(f"Browser logs: {len(logs)} total, {len(js_errors)} JavaScript errors")
        for e in js_errors:
            print("  SEVERE JS ERROR:", e['message'])
        assert len(js_errors) == 0, f"Found JavaScript errors: {js_errors}"

        # 2. Check Category Buttons & Text Presets Count
        style_btns = driver.find_elements(By.CSS_SELECTOR, ".style-btn")
        print(f"Total style buttons in grid: {len(style_btns)} (Expected: 26)")
        assert len(style_btns) == 26, f"Expected 26 total buttons, got {len(style_btns)}"

        text_styles = driver.find_elements(By.CSS_SELECTOR, ".style-btn[data-cat='viral']")
        print(f"Text style buttons (data-cat='viral'): {len(text_styles)} (Expected: 14)")
        assert len(text_styles) == 14, f"Expected 14 text presets, got {len(text_styles)}"

        text_style_ids = [btn.get_attribute("data-style") for btn in text_styles]
        print("Text preset IDs:", text_style_ids)

        expected_ids = [
            'word-by-word',
            'highlight-marker',
            'karaoke-sweep',
            'redaction-classified',
            'smoke-dissolve',
            'glow-neon',
            'glitch-rgb',
            'typewriter',
            'chrome-shimmer',
            'cinema-flare-type',
            'neon-pulse-zoom',
            'volumetric-ray-reveal',
            'shimmer-gold-drift',
            'hyper-focus-blur'
        ]
        assert text_style_ids == expected_ids, f"Text preset IDs do not match expected list: {text_style_ids}"

        # Check that deleted styles do NOT exist
        deleted_ids = ['kinetic-bounce', 'zoom-punch', 'cutout-paper', 'rubber-stamp', 'flip-3d', 'wave-float']
        all_ids = [btn.get_attribute("data-style") for btn in style_btns]
        for did in deleted_ids:
            assert did not in all_ids, f"Deleted style {did} still found in style buttons!"
        print("[OK] All 6 old presets successfully deleted, 9 kept, 5 new added.")

        # 3. Verify all controls exist and are interactive
        text_cam_sel = driver.find_element(By.ID, "textCameraSelect")
        text_cam_slider = driver.find_element(By.ID, "textCamIntensitySlider")
        text_glow_slider = driver.find_element(By.ID, "textGlowSlider")
        text_flare_toggle = driver.find_element(By.ID, "textFlareToggle")
        script_input = driver.find_element(By.ID, "scriptInput")
        target_word = driver.find_element(By.ID, "targetWordInput")

        print("[OK] Camera, Glow, Flare, Script, and Target controls located in DOM.")
        # Test camera switch to subtle
        driver.execute_script("document.getElementById('textCameraSelect').value = 'subtle'; document.getElementById('textCameraSelect').dispatchEvent(new Event('change'));")
        time.sleep(0.2)
        cam_mode = driver.execute_script("return state.textCameraMode;")
        assert cam_mode == 'subtle', f"Camera mode should be 'subtle', got {cam_mode}"

        # Test camera switch back to dynamic
        driver.execute_script("document.getElementById('textCameraSelect').value = 'dynamic'; document.getElementById('textCameraSelect').dispatchEvent(new Event('change'));")
        time.sleep(0.2)
        cam_mode = driver.execute_script("return state.textCameraMode;")
        assert cam_mode == 'dynamic', f"Camera mode should be 'dynamic', got {cam_mode}"

        # Test glow slider sync
        driver.execute_script("document.getElementById('textGlowSlider').value = '55'; document.getElementById('textGlowSlider').dispatchEvent(new Event('input'));")
        time.sleep(0.2)
        glow_val = driver.execute_script("return state.glowIntensity;")
        assert glow_val == 55, f"Glow intensity should be 55, got {glow_val}"
        main_slider_val = driver.execute_script("return document.getElementById('glowIntensitySlider').value;")
        assert main_slider_val == '55', f"Main glow slider should be synced to 55, got {main_slider_val}"

        # 4. Render frames and take snapshots of the 5 new presets
        os.makedirs("C:/Users/shiva/.gemini/antigravity/brain/c529db9f-4476-4403-9053-97e2af00d2e5/text_presets_verify", exist_ok=True)
        out_dir = "C:/Users/shiva/.gemini/antigravity/brain/c529db9f-4476-4403-9053-97e2af00d2e5/text_presets_verify"

        new_presets = [
            'cinema-flare-type',
            'neon-pulse-zoom',
            'volumetric-ray-reveal',
            'shimmer-gold-drift',
            'hyper-focus-blur'
        ]

        for p in new_presets:
            print(f"Testing preset: {p}...")
            btn = driver.find_element(By.CSS_SELECTOR, f".style-btn[data-style='{p}']")
            btn.click()
            time.sleep(0.3)

            # Seek to 1.4s (mid typing / animation)
            driver.execute_script("seekTo(1.4);")
            time.sleep(0.4)
            canvas = driver.find_element(By.ID, "liveCanvas")
            canvas.screenshot(f"{out_dir}/{p}_1.4s.png")

            # Seek to 3.0s (full view + ambient bloom & drift)
            driver.execute_script("seekTo(3.0);")
            time.sleep(0.4)
            canvas.screenshot(f"{out_dir}/{p}_3.0s.png")
            print(f"  [OK] Snapshots saved for {p}")

        # 5. Test Transparent and Green Screen modes
        print("Testing Green Screen and Transparent modes...")
        btn_green = driver.find_element(By.ID, "btnGreenScreen")
        btn_green.click()
        time.sleep(0.3)
        driver.execute_script("seekTo(1.4);")
        time.sleep(0.3)
        driver.find_element(By.ID, "liveCanvas").screenshot(f"{out_dir}/green_screen_flare.png")
        print("  [OK] Green screen snapshot saved")

        btn_trans = driver.find_element(By.ID, "btnTransparentBg")
        btn_trans.click()
        time.sleep(0.3)
        driver.execute_script("seekTo(1.4);")
        time.sleep(0.3)
        driver.find_element(By.ID, "liveCanvas").screenshot(f"{out_dir}/transparent_flare.png")
        print("  [OK] Transparent snapshot saved")

        # Revert transparent
        btn_trans.click()
        time.sleep(0.2)

        # 6. Test camera dynamic zoom in and out
        print("Testing dynamic camera typing zoom on cinema-flare-type...")
        btn = driver.find_element(By.CSS_SELECTOR, ".style-btn[data-style='cinema-flare-type']")
        btn.click()
        time.sleep(0.2)
        # At t=0.2, camera should be zoomed in (> 1.3x)
        # Let's inspect canvas transform or capture at t=0.2 vs t=3.0
        driver.execute_script("seekTo(0.2);")
        time.sleep(0.3)
        driver.find_element(By.ID, "liveCanvas").screenshot(f"{out_dir}/zoom_start_0.2s.png")

        driver.execute_script("seekTo(2.8);")
        time.sleep(0.3)
        driver.find_element(By.ID, "liveCanvas").screenshot(f"{out_dir}/zoom_end_2.8s.png")
        print("  [OK] Zoom in/out snapshots saved")

        print("=== ALL TEST CHECKS PASSED PERFECTLY ===")

    finally:
        driver.quit()

if __name__ == "__main__":
    run_tests()
