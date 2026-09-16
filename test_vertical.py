from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time, os

opts = Options()
opts.add_argument('--headless=new')
opts.add_argument('--window-size=1400,900')
opts.add_argument('--mute-audio')
driver = webdriver.Chrome(options=opts)
try:
    driver.get('http://localhost:3000')
    time.sleep(2)
    btn26 = driver.find_element(By.CSS_SELECTOR, '[data-style="hand-orb-hook"]')
    driver.execute_script('arguments[0].click();', btn26)
    time.sleep(1)

    # Upload both images
    img1 = os.path.abspath(r'C:\Users\shiva\.gemini\antigravity\brain\c529db9f-4476-4403-9053-97e2af00d2e5\.user_uploaded\media_1789535353764.png')
    img2 = os.path.abspath(r'e:\autoae\test_thumb.png')
    driver.find_element(By.ID, 'quickHandOrbUpload1').send_keys(img1)
    driver.find_element(By.ID, 'quickHandOrbUpload2').send_keys(img2)
    time.sleep(1)

    # Switch to 9:16
    driver.find_element(By.ID, 'btnRatio916').click()
    time.sleep(0.5)

    # Seek 2.0s
    driver.execute_script('pause(); seekTo(2.0);')
    time.sleep(0.5)
    driver.save_screenshot(r'C:\Users\shiva\.gemini\antigravity\brain\c529db9f-4476-4403-9053-97e2af00d2e5\preset26_vertical_custom_phase1.png')

    # Seek 4.5s
    driver.execute_script('pause(); seekTo(4.5);')
    time.sleep(0.5)
    driver.save_screenshot(r'C:\Users\shiva\.gemini\antigravity\brain\c529db9f-4476-4403-9053-97e2af00d2e5\preset26_vertical_custom_phase2.png')
    print('Vertical screenshots captured successfully')
finally:
    driver.quit()
