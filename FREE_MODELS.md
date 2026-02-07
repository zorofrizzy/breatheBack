# Free OpenRouter Models

BreatheBack uses **100% FREE** models from OpenRouter. No credit card required!

## Current Model

**Google Gemini Flash 1.5**
- Model ID: `google/gemini-flash-1.5`
- Cost: FREE
- Speed: Fast (1-2 seconds)
- Quality: Excellent for cancer prevention explanations
- Context: 1M tokens

## Alternative Free Models

If you want to try different models, edit `backend/services/llm_service.py` and change the `self.model` line:

### Option 1: Gemini Flash 8B (Faster)
```python
self.model = 'google/gemini-flash-1.5-8b'
```
- Faster responses
- Smaller model
- Still high quality

### Option 2: Llama 3.2 (Good Quality)
```python
self.model = 'meta-llama/llama-3.2-3b-instruct:free'
```
- Meta's open source model
- Good quality
- Reliable

### Option 3: Phi-3 Mini (Compact)
```python
self.model = 'microsoft/phi-3-mini-128k-instruct:free'
```
- Microsoft's compact model
- Fast
- Good for short explanations

## How to Change Models

1. Open `backend/services/llm_service.py`
2. Find line ~18: `self.model = 'google/gemini-flash-1.5'`
3. Replace with your chosen model ID
4. Save and restart server: `python app.py`
5. Test: `python test_llm.py`

## Finding More Free Models

Visit OpenRouter's model list:
https://openrouter.ai/models

Filter by:
- **Price**: $0.00 per 1M tokens
- Look for models with `:free` suffix

## Why Free Models?

- ✅ No cost for hackathon demo
- ✅ No credit card required
- ✅ Unlimited usage for demos
- ✅ High quality results
- ✅ Fast enough for real-time

## Recommended: Stick with Gemini Flash 1.5

For the hackathon, we recommend keeping the default:
- Proven to work well
- Fast responses
- High quality explanations
- Reliable uptime

## Troubleshooting

**"Model not found" error:**
- Check model ID is correct
- Some free models may have rate limits
- Try alternative free model

**Slow responses:**
- Normal for free models (1-3 seconds)
- Gemini Flash is one of the fastest
- Consider Gemini Flash 8B for speed

**Quality issues:**
- Gemini Flash 1.5 has best quality
- Adjust prompts in `llm_service.py` if needed
- Free models are optimized for our use case

---

**Bottom Line**: You're using 100% free AI with no hidden costs! 🎉
