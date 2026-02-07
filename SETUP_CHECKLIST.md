# Setup Checklist ✅

## Before You Start

- [ ] Python 3.8+ installed
- [ ] Git repository cloned/downloaded
- [ ] Terminal/command prompt open in project directory

## Installation (5 minutes)

### 1. Install Python Dependencies
```bash
pip install -r requirements.txt
```
**Expected output**: Successfully installed Flask, Flask-CORS, requests, python-dotenv

### 2. Create .env File
```bash
# Create the file in root directory (same folder as app.py)
# Windows: type nul > .env
# Mac/Linux: touch .env
```

Then edit `.env` and add:
```
OPENROUTER_API_KEY=your-actual-key-here
```

**Get your key**: https://openrouter.ai/
- Sign up (free)
- Go to "Keys" section
- Create new key
- Copy the key (starts with `sk-or-v1-...`)
- **Note**: We use Google Gemini Flash 1.5 (100% FREE, no credit card needed)

### 3. Test LLM Setup
```bash
python test_llm.py
```

**Expected output**:
```
✅ API key found
Testing LLM Cancer Impact Explanations
...
✅ All tests complete!
```

**If you see errors**:
- Check `backend/.env` file exists
- Check API key is correct (no quotes, no spaces)
- Check internet connection

### 4. Start the Server
```bash
python app.py
```

**Expected output**:
```
* Running on http://127.0.0.1:5000
```

### 5. Open the App
Open browser to: http://localhost:5000

### 6. Load Demo Data
1. Click points chip (top right corner)
2. Click "Seed Demo Data" button
3. Confirm
4. Switch to "Map" tab

**Expected result**: Map shows colored zones (yellow, green, blue)

### 7. Test LLM Feature
1. Tap any zone on the map
2. Bottom sheet opens with zone details
3. Look for "🎗️ Cancer Prevention Impact" section
4. Should show "Analyzing cancer risk..." then display explanation

**Expected result**: AI-generated cancer risk explanation appears

## Troubleshooting

### ❌ "OPENROUTER_API_KEY not set"
- **Fix**: Check `.env` file exists in root directory (same folder as `app.py`)
- **Format**: `OPENROUTER_API_KEY=sk-or-v1-...` (no quotes)
- **Restart**: Stop server (Ctrl+C) and run `python app.py` again

### ❌ "Module not found" errors
- **Fix**: Run `pip install -r requirements.txt` again
- **Check**: Make sure you're in the project directory

### ❌ "Port 5000 already in use"
- **Fix**: Stop other Flask apps or change port in `app.py`
- **Windows**: `netstat -ano | findstr :5000` then `taskkill /PID <pid> /F`

### ❌ Map not loading
- **Fix**: Check internet connection (needs Leaflet CDN)
- **Fix**: Try different browser
- **Fix**: Check browser console (F12) for errors

### ❌ No zones on map
- **Fix**: Click "Seed Demo Data" button
- **Fix**: Allow location access when prompted
- **Fix**: Refresh page

### ❌ LLM explanation not appearing
- **Check**: Browser console (F12) for errors
- **Check**: Server terminal for API errors
- **Expected**: Should show fallback message if LLM fails
- **Note**: First call may take 2-3 seconds

## Verification Checklist

Before demo/judging, verify:

- [ ] Server starts without errors
- [ ] App loads in browser
- [ ] Demo data loads (10 zones on map)
- [ ] Can tap zones and see details
- [ ] Cancer impact section appears
- [ ] LLM explanations load (or fallback shows)
- [ ] Can switch between light/dark theme
- [ ] Can submit reports
- [ ] Can complete actions

## Quick Commands Reference

```bash
# Install dependencies
pip install -r requirements.txt

# Test LLM
python test_llm.py

# Start server
python app.py

# Stop server
Ctrl+C

# Check Python version
python --version

# Check if .env exists
# Windows: dir backend\.env
# Mac/Linux: ls backend/.env
```

## File Structure Check

Your project should have:
```
breatheback-community-app/
├── .env                        ← Your API key here (root directory)
├── backend/
│   ├── services/
│   │   └── llm_service.py      ← LLM code
│   └── ...
├── frontend/
│   └── zoneInspector.js        ← Shows LLM results
├── app.py                      ← Main server
├── test_llm.py                 ← Test script
├── requirements.txt            ← Dependencies
└── README.md
```

## Success Indicators

✅ **Setup Complete** when:
1. `python test_llm.py` shows 4 successful explanations
2. Server starts without errors
3. App loads in browser
4. Zones appear on map
5. Tapping zone shows cancer impact explanation

## Next Steps

Once setup is complete:
1. Read `DEMO_GUIDE.md` for presentation tips
2. Practice the demo flow
3. Prepare talking points
4. Win the hackathon! 🏆

---

**Need Help?**
- Check `LLM_SETUP.md` for detailed instructions
- Check `HACKATHON_QUICKSTART.md` for quick reference
- Check server terminal for error messages
- Check browser console (F12) for frontend errors
