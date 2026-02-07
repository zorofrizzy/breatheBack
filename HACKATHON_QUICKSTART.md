# Hack4Hope Quick Start Guide

## 🚀 Get Running in 5 Minutes

### 1. Install Dependencies (1 min)
```bash
pip install -r requirements.txt
```

### 2. Set Up LLM (2 min)

Create a file `.env` in the root directory (same folder as `app.py`):

```bash
OPENROUTER_API_KEY=sk-or-v1-your-key-here
```

Get your key from https://openrouter.ai/ (FREE - no credit card needed!)

### 3. Test LLM (1 min)
```bash
python test_llm.py
```

You should see cancer impact explanations for different zones!

### 4. Start Server (1 min)
```bash
python app.py
```

Open http://localhost:5000

### 5. Load Demo Data
1. Click the points chip (top right)
2. Click "Seed Demo Data"
3. Confirm
4. Switch to Map view

## 🎬 Quick Demo

1. **Tap a yellow zone** → See AI cancer explanation
2. **Tap a green zone** → See different explanation
3. **Tap a blue zone** → See positive message

## 📝 What to Show Judges

### The Winning Feature: AI Cancer Translator
- Tap any zone on the map
- Scroll to "🎗️ Cancer Prevention Impact"
- **This is your differentiator!**
- AI explains cancer risk in real-time
- Personalized to each zone's data

### The Full Flow
1. Report tab → Submit vape/smoke report
2. Get restoration actions
3. Complete an action → Earn points
4. Map tab → See zones change color
5. Tap zones → See AI cancer explanations

## 🎯 Key Talking Points

1. **"We make cancer policy understandable"**
   - AI translates abstract data into cancer risk
   - Youth-focused language
   - Real-time, personalized

2. **"We make it actionable"**
   - Gamified engagement
   - Immediate actions to take
   - See your impact on the map

3. **"We overcome barriers"**
   - Knowledge gap: Youth don't understand cancer risk
   - Engagement gap: Traditional education is boring
   - Action gap: No clear way to help

4. **"We support ACS CAN's mission"**
   - Direct cancer prevention education
   - Youth advocacy development
   - Community health improvement

## 🐛 Troubleshooting

**LLM not working?**
- Check: `.env` file exists in root directory (same folder as `app.py`)
- Format: `OPENROUTER_API_KEY=sk-or-v1-your-key` (no quotes)
- Restart server after creating/updating .env file
- Check server logs for errors

**No zones on map?**
- Click "Seed Demo Data" button
- Allow location access
- Refresh page

**Map not loading?**
- Check internet connection (needs Leaflet CDN)
- Try different browser
- Check browser console for errors

## 📊 Demo Data

After seeding, you'll have:
- 3 recovered zones (blue) - Low cancer risk
- 3 healing zones (green) - Improving
- 4 needs restoration zones (yellow) - High cancer risk

Each shows different AI-generated cancer explanations!

## 🏆 Winning Strategy

1. **Start with the problem**: Youth don't understand cancer risk from vaping/smoking
2. **Show the solution**: AI + gamification = engagement + education
3. **Demo the AI feature**: This is your differentiator
4. **Connect to ACS CAN**: Cancer prevention advocacy
5. **Show scalability**: Works in any community

## 📚 More Resources

- **LLM_SETUP.md** - Detailed LLM setup
- **DEMO_GUIDE.md** - Full demo script
- **README.md** - Complete documentation

## ⏱️ Time Budget

- Setup: 5 minutes
- Practice demo: 10 minutes
- Actual demo: 5 minutes
- Q&A: 5 minutes

**Total prep time: 15 minutes**

---

## 🎉 You're Ready!

Your app is now a cancer prevention education platform powered by AI. Go win this hackathon! 🏆
