# Gmail OAuth Verification Checklist - Silver Tier

## Pre-Authentication Checks

### Google Console Configuration
- [ ] OAuth client type: **Web application** (not Desktop)
- [ ] Authorized redirect URI: `http://localhost:8080/`
- [ ] Gmail API enabled
- [ ] OAuth consent screen configured:
  - [ ] User type: Testing
  - [ ] Your email added as test user
  - [ ] Scope added: `https://www.googleapis.com/auth/gmail.readonly`

### Local Files
- [ ] `credentials.json` exists in `/mnt/d/Irfan/FTE-H/watchers/`
- [ ] Virtual environment active or using `.venv/bin/python`
- [ ] Dependencies installed: `google-auth-oauthlib google-api-python-client`

---

## Run Authentication

```bash
cd /mnt/d/Irfan/FTE-H/watchers
.venv/bin/python gmail_auth.py
```

**Expected behavior:**
1. Script prints "Starting local server on http://localhost:8080"
2. Browser opens automatically to Google sign-in
3. You sign in with your Gmail account
4. You click "Allow" for Gmail read access
5. Browser shows "The authentication flow has completed"
6. Script prints "✅ Authentication Successful!"
7. `token.json` file created

---

## Post-Authentication Verification

### Check token.json exists
```bash
ls -lh token.json
# Should show a file with ~500 bytes
```

### Test Gmail Watcher
```bash
.venv/bin/python gmail_watcher.py
```

**Expected output:**
```
📧 Gmail Watcher for AI Employee
============================================================

Starting Gmail Watcher...
Vault: ../AI_Employee_Vault
Check interval: 5 minutes

✅ Gmail API connected successfully
✅ Gmail Watcher started successfully!

Monitoring your inbox for important emails...
Press Ctrl+C to stop
```

---

## Troubleshooting

### "Authorization Error" or "invalid_client"
→ OAuth client not configured as Web application
→ Fix: Recreate OAuth client as Web application type

### "Missing required parameter: redirect_uri"
→ Redirect URI not set to `http://localhost:8080/`
→ Fix: Add exact URI in Google Console

### "Access blocked: This app's request is invalid"
→ Email not added as test user
→ Fix: Add your email in OAuth consent screen → Audience → Test users

### Browser doesn't open automatically
→ Copy the URL shown in terminal and open manually
→ URL will look like: `http://localhost:8080/?state=...&code=...`

---

## Security Notes

✅ `token.json` stored locally (not in Obsidian vault)
✅ Read-only scope (cannot send/delete emails)
✅ Token auto-refreshes (doesn't expire unless revoked)
✅ Human-in-the-loop via approval system

---

*Silver Tier - Personal AI Employee Hackathon 0*
