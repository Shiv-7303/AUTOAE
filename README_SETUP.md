# AutoAE Motion Studio - Setup Guide

## 📋 Requirements (Dusre PC pe run karne ke liye)

### 1. Python 3.11+ Install karo
- Download: https://www.python.org/downloads/
- Install karte waqt **"Add Python to PATH"** checkbox zaroor tick karo ✅
- Verify: Terminal me type karo:
  ```
  python --version
  ```

### 2. FFmpeg Install karo (Video export ke liye zaroori hai)
- **Windows pe install karne ka tarika:**
  ```
  winget install ffmpeg
  ```
  **Ya manually:**
  - Download: https://ffmpeg.org/download.html (Windows build)
  - Extract karo aur `bin` folder ko System PATH me add karo
- Verify:
  ```
  ffmpeg -version
  ```

### 3. Internet Connection
- Google Fonts aur Lucide Icons CDN se load hote hain, isliye first time chalane pe internet chahiye

---

## 🚀 Project Kaise Run Kare

### Step 1: ZIP Extract karo
Koi bhi folder me extract karo, jaise `C:\autoae` ya `D:\autoae`

### Step 2: Terminal (Command Prompt ya PowerShell) khoolo
Uss folder me jao jahan extract kiya:
```
cd C:\autoae
```

### Step 3: Server start karo
```
python server.py
```

### Step 4: Browser me khoolo
```
http://localhost:3000
```

---

## 📁 Project Structure (Important Files)

```
autoae/
├── index.html          ← Main UI (single-page app, sab kuch isme hai)
├── server.py           ← Python HTTP server + FFmpeg video export API
├── Dockerfile          ← Docker deployment ke liye
├── render.yaml         ← Render.com cloud deployment config
├── requirements.txt    ← Python dependencies (sirf standard library)
├── template/           ← Template videos aur preview assets
├── hand_hook.png       ← UI asset
├── hand_bg.png         ← UI asset
├── businessman_*.png   ← UI assets
└── extracted_preset28_good.js ← Preset configuration
```

---

## ⚠️ Important Notes

1. **Koi extra Python package install nahi karna** - Ye sirf Python standard library use karta hai (`http.server`, `subprocess`, etc.)
2. **FFmpeg zaroor install karo** - Bina FFmpeg ke video export kaam nahi karega
3. **Port 3000** - Agar port 3000 busy hai to environment variable set karo:
   ```
   set PORT=8080
   python server.py
   ```
4. **Test files zaroori nahi hain** - `test_*.py` aur `comparisons_*` folders dev/testing ke liye hain, run karne ke liye zaroorat nahi

---

## 🐳 Docker se chalana hai? (Optional)

```bash
docker build -t autoae .
docker run -p 3000:3000 autoae
```
Phir browser me: `http://localhost:3000`

