# 🤖 Google Gemini AI Setup Guide

## Quick Setup for Gemini API

### Step 1: Install Gemini Package

```bash
pip install google-generativeai
```

### Step 2: Get Your Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click **"Get API Key"** or **"Create API Key"**
4. Copy your API key (it will look like: `AIzaSy...`)

### Step 3: Set Environment Variable

**Windows PowerShell:**
```powershell
$env:GEMINI_API_KEY="AIzaSy-your-api-key-here"
```

**Windows Command Prompt:**
```cmd
set GEMINI_API_KEY=AIzaSy-your-api-key-here
```

**macOS/Linux:**
```bash
export GEMINI_API_KEY="AIzaSy-your-api-key-here"
```

**Or create a `.env` file:**
```env
GEMINI_API_KEY=AIzaSy-your-api-key-here
GEMINI_MODEL=gemini-pro
```

### Step 4: Run the Application

```bash
python run.py
```

Then visit: **http://localhost:5000** and click **"AI Assistant"**!

---

## 🎯 Why Gemini?

### Advantages:
✅ **FREE Tier** - 60 requests per minute for free!  
✅ **High Quality** - Comparable to GPT-3.5/GPT-4  
✅ **Fast** - Quick response times  
✅ **Large Context** - Handles long conversations  
✅ **Multimodal** - Can process images (future feature)  

### Pricing (if you exceed free tier):
- **Gemini Pro**: FREE for up to 60 requests/minute
- **Gemini Pro Vision**: FREE for up to 60 requests/minute
- Very affordable paid tiers if needed

---

## 🧪 Test Your Setup

### Quick Test:

```bash
python -c "import google.generativeai as genai; genai.configure(api_key='YOUR_KEY'); model = genai.GenerativeModel('gemini-pro'); print(model.generate_content('Hello!').text)"
```

### Check if Working:

1. Start your app: `python run.py`
2. Go to: http://localhost:5000/ai/api/chat/status
3. Should show: `"model": "Google Gemini"`

---

## 💬 Example Queries

Try these in the chat:

```
"I need a quiet study room for tomorrow"
"Find me video equipment"
"Show me meeting rooms for 10 people"
"What resources are in the Library?"
```

---

## 🔧 Configuration Options

### Available Models:

```bash
# Default (recommended)
GEMINI_MODEL=gemini-pro

# For image understanding (future)
GEMINI_MODEL=gemini-pro-vision
```

### Alternative Environment Variable Names:

The code supports both:
- `GEMINI_API_KEY` (recommended)
- `GOOGLE_API_KEY` (also works)

---

## 🆓 Free Tier Limits

**Gemini Pro (Free):**
- 60 requests per minute
- 1,500 requests per day
- No credit card required!

**This is MORE than enough for:**
- Small to medium deployments
- Testing and development
- Class projects
- Personal use

---

## 🐛 Troubleshooting

### "No module named 'google.generativeai'"

```bash
pip install google-generativeai
```

### "AI features are not available"

```bash
# Set your API key
$env:GEMINI_API_KEY="AIzaSy-your-key"

# Verify it's set
echo $env:GEMINI_API_KEY
```

### "Invalid API key"

- Check your key at: https://makersuite.google.com/app/apikey
- Make sure it starts with `AIzaSy`
- No extra spaces or quotes

### Rate limit errors (rare with free tier)

- Free tier: 60 requests/minute is very generous
- If exceeded, wait 60 seconds
- Consider implementing caching for repeated queries

---

## 🎨 Customize AI Behavior

Edit `src/services/ai_concierge.py`:

```python
def _build_system_prompt(self, context):
    return f"""You are a [CUSTOMIZE PERSONALITY]...
    
    [Adjust tone, style, and instructions here]
    """
```

---

## 📊 Gemini vs OpenAI Comparison

| Feature | Gemini Pro (Free) | GPT-3.5-turbo |
|---------|-------------------|---------------|
| **Cost** | FREE | ~$0.002/query |
| **Rate Limit** | 60/min | Varies by plan |
| **Quality** | Excellent | Excellent |
| **Context** | Large | Large |
| **Setup** | Easy | Easy |

---

## 🚀 Advanced Features (Future)

Gemini supports:
- **Image understanding** - Upload resource photos
- **Long context** - Handle complex queries
- **Multimodal** - Mix text and images
- **Fast streaming** - Real-time responses

---

## 📱 API Endpoint Examples

### Send a message:

```bash
curl -X POST http://localhost:5000/ai/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Find study rooms"}'
```

### Check status:

```bash
curl http://localhost:5000/ai/api/chat/status
```

---

## 🎓 Resources

- **Gemini API Docs**: https://ai.google.dev/docs
- **Get API Key**: https://makersuite.google.com/app/apikey
- **Python SDK**: https://github.com/google/generative-ai-python
- **Pricing**: https://ai.google.dev/pricing

---

## ✅ You're Ready!

Your Campus Resource Hub now has **FREE AI-powered chat** using Google Gemini! 🎉

**Test it now:** http://localhost:5000/ai/chat

**Enjoy unlimited conversations with the free tier!** 🚀

