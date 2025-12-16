# Security Guidelines - Campus Resource Hub

## 🔒 Protecting Your API Keys

### Never Commit API Keys to Git!

Your `.env` file contains sensitive information and should **NEVER** be committed to GitHub.

### What's Protected

✅ **Already in `.gitignore`:**
- `.env` - Your environment variables (including API keys)
- `*.db` - Database files
- `__pycache__/` - Python cache
- `.vscode/`, `.idea/` - IDE settings

### Setup for New Users

1. **Copy the example file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` and add your real API key:**
   ```env
   GEMINI_API_KEY=your-actual-api-key-here
   ```

3. **Never commit `.env`:**
   ```bash
   # This is already in .gitignore, but double-check:
   git check-ignore .env
   # Should output: .env
   ```

---

## ✅ Before Pushing to GitHub

### Step 1: Check What Will Be Committed

```bash
# See which files will be committed
git status

# Make sure .env is NOT listed!
```

### Step 2: Verify .env is Ignored

```bash
# This should return ".env"
git check-ignore .env

# If it returns nothing, add it to .gitignore:
echo ".env" >> .gitignore
```

### Step 3: Check for Hardcoded Keys

```bash
# Search for API keys in your code (returns nothing if safe)
git grep -i "AIzaSy"
git grep -i "api.key"
git grep -i "secret"
```

---

## 🚨 If You Already Committed Your API Key

### Option 1: Regenerate Your API Key (Recommended)

1. Go to https://makersuite.google.com/app/apikey
2. Delete the old API key
3. Generate a new one
4. Update your `.env` file

### Option 2: Remove from Git History (Advanced)

```bash
# WARNING: This rewrites history!
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all

# Force push (be careful!)
git push origin --force --all
```

**Then regenerate your API key anyway!**

---

## 📋 Pre-Push Checklist

Before running `git push`, verify:

- [ ] `.env` is in `.gitignore`
- [ ] No API keys in your code
- [ ] No hardcoded passwords
- [ ] Database files not included (*.db)
- [ ] No sensitive data in commit messages
- [ ] `.env.example` has placeholder values only

---

## 🔐 Best Practices

### DO ✅

- Use environment variables for all secrets
- Keep `.env` in `.gitignore`
- Share `.env.example` with placeholder values
- Use different API keys for dev/prod
- Rotate API keys periodically
- Add `.env` to `.gitignore` immediately

### DON'T ❌

- Never commit `.env` file
- Never hardcode API keys in source code
- Never share API keys in chat/email
- Never commit database files with user data
- Never put keys in commit messages
- Never push secret keys to public repos

---

## 📚 Environment Variable Loading

The app uses `python-dotenv` to automatically load `.env`:

```python
# In src/services/ai_concierge.py
self.api_key = os.environ.get('GEMINI_API_KEY')
```

This safely loads from:
1. Environment variables (set in terminal)
2. `.env` file (if exists)
3. System environment variables

---

## 🔍 Verify Your Security

### Check Current Status:

```bash
# Should show .env is ignored
git status --ignored

# Should return .env
git check-ignore .env

# Should return nothing (no keys in code)
git grep "AIzaSy"
```

### Test Without Real Keys:

```bash
# Temporarily rename .env
mv .env .env.backup

# Run app - should use fallback mode
python run.py

# Restore .env
mv .env.backup .env
```

---

## 🆘 Emergency: Key Exposed

If you accidentally exposed your API key:

1. **Immediately revoke it:**
   - Gemini: https://makersuite.google.com/app/apikey
   
2. **Generate new key**

3. **Update `.env` file**

4. **Restart application**

5. **Check GitHub for exposed keys:**
   - Review recent commits
   - Check pull requests
   - Search repo for key patterns

---

## 📖 Additional Resources

- **Git Secrets Scanner**: https://github.com/awslabs/git-secrets
- **GitHub Secret Scanning**: Automatically enabled for public repos
- **Environment Variables Guide**: See README.md

---

## ✅ You're Secure When...

- `.env` is in `.gitignore` ✅
- No API keys in source code ✅
- `.env.example` has placeholders only ✅
- API key works but isn't in Git ✅

**Stay safe! 🔒**

