# LLM Cancer Impact Feature Setup

## Overview
This feature uses OpenRouter to generate personalized cancer prevention explanations that make the app's impact understandable and compelling for Hack4Hope judges.

## Setup Steps

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Get OpenRouter API Key
1. Go to https://openrouter.ai/
2. Sign up for an account
3. Navigate to Keys section
4. Create a new API key
5. Copy the key (starts with `sk-or-...`)

### 3. Create .env File

Create a file named `.env` in the **root directory** (same folder as `app.py`):

```bash
OPENROUTER_API_KEY=your-key-here
```

**Important**: Replace `your-key-here` with your actual API key!

### 4. Start the Server
```bash
python app.py
```

The app will automatically load the API key from the `.env` file.

## How It Works

### Zone Inspector
When users tap a zone on the heatmap, they see:
1. Zone state (Needs Restoration / Healing / Recovered)
2. **NEW: Cancer Prevention Impact** - LLM-generated explanation of how this zone's air quality affects cancer risk
3. Progress information (points needed)
4. Activity level

### API Endpoint
```
POST /api/explain
{
  "context": "zone",
  "zone_data": {
    "vape_debt": 100,
    "vape_restore": 20,
    "smoke_debt": 80,
    "smoke_restore": 10
  },
  "map_type": "vape"
}
```

Returns:
```json
{
  "explanation": "This zone has high exposure to vaping aerosols, which contain carcinogens linked to lung and throat cancer. Your restoration actions can help reduce cancer risk for everyone here.",
  "context": "zone"
}
```

## Demo Script for Judges

1. **Open the app** - Show the heatmap with colored zones
2. **Tap a yellow zone** (needs restoration)
   - Point out: "See this Cancer Prevention Impact section?"
   - Read the LLM explanation
   - Emphasize: "This is AI translating abstract 'vape debt' into real cancer risk"
3. **Tap a green zone** (healing)
   - Show how the explanation changes based on zone state
4. **Tap a blue zone** (recovered)
   - Show the positive, empowering message

**Key talking points:**
- "We're not just gamifying air quality—we're teaching youth WHY it matters for cancer prevention"
- "The AI personalizes the message based on actual zone data"
- "This makes cancer policy understandable and actionable for young people"

## Fallback Behavior
If the LLM API fails or the key is not set, the app shows static fallback messages. The app never breaks.

## Cost
OpenRouter provides free models! BreatheBack uses:
- **Model**: Google Gemini Flash 1.5
- **Cost**: FREE (no charges)
- **Speed**: Fast responses (1-2 seconds)
- **Quality**: High-quality cancer prevention explanations

No credit card required for the free tier!

## Troubleshooting

**"OPENROUTER_API_KEY not set" error:**
- Make sure you created the `.env` file in the **root directory** (same folder as `app.py`)
- Check that the file contains: `OPENROUTER_API_KEY=your-actual-key`
- No quotes needed around the key in the .env file
- Restart the server after creating/updating the .env file

**Slow responses:**
- Normal! LLM calls take 1-3 seconds
- The UI shows "Analyzing cancer risk..." while loading

**No explanation appears:**
- Check browser console for errors
- Check server logs for API errors
- Fallback message should still appear

## Future Enhancements
- Cache common explanations to reduce API calls
- Add action completion explanations
- Add total impact summary in points panel
- Multi-language support
