# AI Chatbot Setup Guide

## 🤖 Overview

The Campus Resource Hub now includes an **AI-Powered Resource Concierge** chatbot that helps users discover and book resources using natural language.

---

## 📦 Installation

### Step 1: Install OpenAI Package

```bash
pip install openai
```

Or reinstall all dependencies:

```bash
pip install -r requirements.txt
```

---

## 🔑 OpenAI API Setup

### Option A: Using OpenAI GPT (Recommended)

1. **Get an API Key**
   - Go to [OpenAI Platform](https://platform.openai.com/)
   - Sign up or log in
   - Navigate to API Keys section
   - Create a new API key
   - Copy the key (starts with `sk-...`)

2. **Set Environment Variable**

   **Windows (PowerShell):**
   ```powershell
   $env:OPENAI_API_KEY="sk-your-api-key-here"
   ```

   **Windows (Command Prompt):**
   ```cmd
   set OPENAI_API_KEY=sk-your-api-key-here
   ```

   **macOS/Linux:**
   ```bash
   export OPENAI_API_KEY="sk-your-api-key-here"
   ```

3. **Permanent Setup (Optional)**
   
   Create a `.env` file in the project root:
   ```
   OPENAI_API_KEY=sk-your-api-key-here
   OPENAI_MODEL=gpt-3.5-turbo
   ```

---

### Option B: Using Fallback Mode (No API Key Required)

If you don't have an OpenAI API key, the chatbot will automatically use **keyword-based fallback mode**:

- ✅ Works without any API key
- ✅ Free and unlimited
- ✅ Fast responses
- ❌ Less intelligent (keyword matching only)
- ❌ No conversation memory

**To use fallback mode**: Simply don't set the `OPENAI_API_KEY` environment variable.

---

## 🚀 Running the Chatbot

### Start the Application

```bash
python run.py
```

### Access the AI Assistant

1. Open your browser to: http://localhost:5000
2. Click **"AI Assistant"** in the navigation bar
3. Start chatting!

---

## 💬 Example Conversations

### With OpenAI API (Natural Language):

**You**: "I need a quiet place to study for my exam tomorrow afternoon"

**AI**: "I found some great quiet study spaces for you! Here are my top recommendations:

- Study Room 101 (Library Floor 1) - Individual space, rated 4.8⭐
- Silent Study Pod (Library Floor 3) - Perfect for focus, rated 4.9⭐

These rooms are available tomorrow afternoon. Would you like to book one?"

---

### With Fallback Mode (Keyword Matching):

**You**: "study room quiet"

**Fallback**: "I found 5 resources that might help:

• Study Room 101 (Library, Floor 1) - Rating: 4.8⭐
• Study Room 202 (Business Building) - Rating: 4.5⭐
• Silent Study Pod (Library, Floor 3) - Rating: 4.9⭐

Click on any resource to view details and book!"

---

## 🎯 Features

### With OpenAI API Enabled:
✅ Natural language understanding  
✅ Context-aware conversations  
✅ Personalized recommendations  
✅ Conversation memory  
✅ Follow-up questions  
✅ Multi-turn dialogues  

### Fallback Mode:
✅ Keyword-based search  
✅ Category filtering  
✅ Fast responses  
✅ No API costs  
✅ Works offline  

---

## 🔧 Configuration Options

### Environment Variables

```bash
# Required for OpenAI features
OPENAI_API_KEY=sk-your-key-here

# Optional: Choose GPT model (default: gpt-3.5-turbo)
OPENAI_MODEL=gpt-3.5-turbo
# or
OPENAI_MODEL=gpt-4

# Optional: Adjust response length (default: 500)
OPENAI_MAX_TOKENS=500
```

---

## 💰 Cost Information

### OpenAI API Pricing (as of 2024):

- **GPT-3.5-turbo**: ~$0.002 per 1K tokens (~750 words)
- **GPT-4**: ~$0.03 per 1K tokens

**Estimated Costs:**
- Average chatbot query: $0.001 - $0.005
- 100 conversations: ~$0.10 - $0.50
- Monthly (1000 users, 5 queries each): ~$5 - $25

### Free Tier:
- OpenAI offers $5 free credit for new users
- Enough for ~1,000-2,500 conversations

---

## 🧪 Testing the Chatbot

### Manual Testing:

1. Navigate to http://localhost:5000/ai/chat
2. Try these example queries:
   - "Find me a study room"
   - "I need video equipment for tomorrow"
   - "Show me meeting rooms with capacity for 10 people"
   - "What's available in the Library?"

### Check AI Status:

```bash
curl http://localhost:5000/ai/api/chat/status
```

Response:
```json
{
  "enabled": true,
  "model": "OpenAI GPT",
  "features": {
    "natural_language": true,
    "context_aware": true,
    "conversation_memory": true
  }
}
```

---

## 🔒 Security & Privacy

✅ **API Key Security**
- Store in environment variables, never commit to Git
- Use `.env` file (already in `.gitignore`)

✅ **Data Privacy**
- User queries are sent to OpenAI API (see their privacy policy)
- Conversation history stored in session (not permanent)
- No user data stored in database

✅ **Rate Limiting**
- Implement rate limiting in production
- Monitor API usage in OpenAI dashboard

---

## 🐛 Troubleshooting

### Problem: "AI features are not available"

**Solution**: Set your OpenAI API key:
```bash
export OPENAI_API_KEY="sk-your-key-here"
```

### Problem: "openai module not found"

**Solution**: Install the OpenAI package:
```bash
pip install openai
```

### Problem: "API key invalid"

**Solution**: Check your API key at https://platform.openai.com/api-keys

### Problem: Rate limit errors

**Solution**: 
- Wait a few minutes
- Check your OpenAI usage limits
- Upgrade your OpenAI plan if needed

---

## 🎨 Customization

### Change AI Personality

Edit `src/services/ai_concierge.py`, line ~125:

```python
system_prompt = """You are a friendly and enthusiastic campus resource assistant...
Adjust tone, style, and instructions here!
"""
```

### Add More Context

Modify the `_get_resource_context()` method to include:
- User preferences
- Booking history
- Popular resources
- Seasonal recommendations

### Change Model

Use GPT-4 for better responses (costs more):
```bash
export OPENAI_MODEL=gpt-4
```

---

## 📊 Monitoring

### Track Usage:
1. OpenAI Dashboard: https://platform.openai.com/usage
2. View conversation logs in Flask app logs
3. Monitor session storage for chat history

---

## 🚀 Next Steps

### Phase 1 (Current):
✅ Basic chatbot functionality  
✅ Resource recommendations  
✅ Keyword fallback mode  

### Phase 2 (Future):
- Voice input/output
- Booking directly from chat
- Multi-language support
- Integration with calendar
- Proactive suggestions
- Analytics dashboard

---

## 📞 Support

**Issues?**
- Check logs: `python run.py` (look for errors)
- Test API: `curl -X POST http://localhost:5000/ai/api/chat -H "Content-Type: application/json" -d '{"message":"test"}'`
- OpenAI Status: https://status.openai.com/

**Resources:**
- OpenAI API Docs: https://platform.openai.com/docs
- Campus Resource Hub README: [README.md](README.md)

---

**🎉 You're all set! Start chatting with your AI assistant!**

