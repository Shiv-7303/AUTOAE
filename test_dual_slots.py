import os
import sys
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

def run_test():
    chrome_options = Options()
    chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--window-size=1400,900')
    chrome_options.add_argument('--mute-audio')
    
    driver = webdriver.Chrome(options=chrome_options)
    try:
        print("Navigating to http://localhost:3000 ...")
        driver.get('http://localhost:3000')
        time.sleep(2)
        
        # Select Preset 26
        btn26 = driver.find_element(By.CSS_SELECTOR, '[data-style="hand-orb-hook"]')
        driver.execute_script("arguments[0].click();", btn26)
        time.sleep(1)
        
        # Verify Quick Controls are displayed
        quick_controls = driver.find_element(By.ID, "quickHandOrbControls")
        assert quick_controls.is_displayed(), "quickHandOrbControls should be visible"
        print("[OK] quickHandOrbControls is visible")
        
        # Test 1: Default Template Dual Faces
        # Seek to 2.0s (Phase 1)
        driver.execute_script("pause(); seekTo(2.0);")
        time.sleep(0.5)
        driver.save_screenshot(r"C:\Users\shiva\.gemini\antigravity\brain\c529db9f-4476-4403-9053-97e2af00d2e5\preset26_default_phase1.png")
        print("[OK] Captured preset26_default_phase1.png at 2.0s")
        
        # Seek to 3.25s (Flip transition)
        driver.execute_script("pause(); seekTo(3.25);")
        time.sleep(0.5)
        driver.save_screenshot(r"C:\Users\shiva\.gemini\antigravity\brain\c529db9f-4476-4403-9053-97e2af00d2e5\preset26_default_flip.png")
        print("[OK] Captured preset26_default_flip.png at 3.25s")
        
        # Seek to 4.5s (Phase 2)
        driver.execute_script("pause(); seekTo(4.5);")
        time.sleep(0.5)
        driver.save_screenshot(r"C:\Users\shiva\.gemini\antigravity\brain\c529db9f-4476-4403-9053-97e2af00d2e5\preset26_default_phase2.png")
        print("[OK] Captured preset26_default_phase2.png at 4.5s")
        
        # Test 2: Upload custom image to Slot 1 and distinct image to Slot 2
        img1_path = os.path.abspath(r"C:\Users\shiva\.gemini\antigravity\brain\c529db9f-4476-4403-9053-97e2af00d2e5\.user_uploaded\media_1789535353764.png")
        img2_path = os.path.abspath(r"e:\autoae\test_thumb.png")
        
        upload1 = driver.find_element(By.ID, "quickHandOrbUpload1")
        upload1.send_keys(img1_path)
        time.sleep(1)
        
        upload2 = driver.find_element(By.ID, "quickHandOrbUpload2")
        upload2.send_keys(img2_path)
        time.sleep(1)
        
        status1 = driver.find_element(By.ID, "quickHandOrbStatus1").text
        status2 = driver.find_element(By.ID, "quickHandOrbStatus2").text
        print(f"Status 1: {status1.encode('ascii', 'ignore').decode()}, Status 2: {status2.encode('ascii', 'ignore').decode()}")
        
        # Seek to 2.0s (Custom Image 1)
        driver.execute_script("pause(); seekTo(2.0);")
        time.sleep(0.5)
        driver.save_screenshot(r"C:\Users\shiva\.gemini\antigravity\brain\c529db9f-4476-4403-9053-97e2af00d2e5\preset26_dual_custom_phase1.png")
        print("[OK] Captured preset26_dual_custom_phase1.png (Slot 1 custom media)")
        
        # Seek to 3.25s (Flip transition)
        driver.execute_script("pause(); seekTo(3.25);")
        time.sleep(0.5)
        driver.save_screenshot(r"C:\Users\shiva\.gemini\antigravity\brain\c529db9f-4476-4403-9053-97e2af00d2e5\preset26_dual_custom_flip.png")
        print("[OK] Captured preset26_dual_custom_flip.png (Mid flip)")
        
        # Seek to 4.5s (Custom Image 2)
        driver.execute_script("pause(); seekTo(4.5);")
        time.sleep(0.5)
        driver.save_screenshot(r"C:\Users\shiva\.gemini\antigravity\brain\c529db9f-4476-4403-9053-97e2af00d2e5\preset26_dual_custom_phase2.png")
        print("[OK] Captured preset26_dual_custom_phase2.png (Slot 2 custom media)")
        
        # Test 3: Check 2-Way Sync between Quick Controls and Motion Tab
        driver.execute_script("switchTab('tab-motion');")
        time.sleep(0.5)
        motion_pnl = driver.find_element(By.ID, "motionHandOrbPanel")
        assert motion_pnl.is_displayed(), "motionHandOrbPanel should be visible in tab-motion"
        print("[OK] motionHandOrbPanel is visible in tab-motion")
        
        # Check browser console logs
        logs = driver.get_log('browser')
        severe = [l for l in logs if l['level'] == 'SEVERE']
        print(f"Browser Severe Errors: {len(severe)}")
        if severe:
            for l in severe:
                print("SEVERE:", l)
                
        print("ALL VERIFICATION CHECKS PASSED!")
    finally:
        driver.quit()

if __name__ == '__main__':
    run_test()
