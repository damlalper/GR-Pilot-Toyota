# Groq API Key Setup Guide

## Problem Identified
The current API key in `.streamlit/secrets.toml` is **invalid or expired** (Error 401).

## How to Get a New Groq API Key

### Step 1: Visit Groq Console
Go to: https://console.groq.com/keys

### Step 2: Sign In or Create Account
- Sign in with your existing account
- Or create a new account if you don't have one

### Step 3: Create New API Key
1. Click on "Create API Key" button
2. Give it a name (e.g., "GR-Pilot-Toyota")
3. Click "Create"
4. **IMPORTANT**: Copy the key immediately (it starts with `gsk_`)
5. The key should be approximately 50-60 characters long

### Step 4: Update secrets.toml
1. Open: `.streamlit/secrets.toml`
2. Replace the current key with your new key:
   ```toml
   GROQ_API_KEY = "gsk_YOUR_NEW_KEY_HERE"
   ```
3. Save the file

### Step 5: Test the Connection
Run the test script:
```bash
python test_groq_api.py
```

You should see:
```
[OK] API Key loaded successfully
[CONNECTING] to Groq API...
[SENDING] test request...
[SUCCESS] Groq API is working correctly!
    Response: Hello
```

## Common Issues and Solutions

### Issue 1: Key has spaces or hidden characters
**Solution**: Make sure to copy the ENTIRE key without any extra spaces
- Check length with the test script
- Should be 50-60 characters

### Issue 2: Using wrong environment variable name
**Solution**: The file uses `GROQ_API_KEY` (not `GROQ_KEY` or `API_KEY`)

### Issue 3: Key is deactivated
**Solution**: Go to Groq Console → API Keys → Check if status is "Active"
- If "Inactive", create a new key

### Issue 4: Account has no credits
**Solution**: Groq provides free tier credits
- Check your account dashboard for credit balance
- Free tier: https://console.groq.com/settings/limits

## After Updating the Key

1. Restart your Streamlit app:
   ```bash
   streamlit run app.py
   ```

2. Test the AI assistant in the app by asking a question

## Security Note
**NEVER commit secrets.toml to Git!**
- The file `.streamlit/secrets.toml` should be in `.gitignore`
- Never share your API key publicly
