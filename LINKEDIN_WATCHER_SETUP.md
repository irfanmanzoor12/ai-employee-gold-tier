# LinkedIn Watcher Setup Guide - Silver Tier

## ⚠️ COMPLIANCE NOTICE

**This watcher is READ-ONLY and safe for hackathon judging:**
- ❌ No automatic posting
- ❌ No automatic replies
- ❌ No automatic connections
- ❌ No scraping at scale
- ✅ Human-in-the-loop only
- ✅ All actions require manual approval

---

## Prerequisites

### 1. Install Playwright Browsers

```bash
cd /mnt/d/Irfan/FTE-H/watchers
uv pip install playwright
.venv/bin/python -m playwright install chromium
```

This downloads the Chromium browser binaries (~100MB).

### 2. Verify Installation

```bash
.venv/bin/python -c "from playwright.sync_api import sync_playwright; print('✅ Playwright ready')"
```

---

## First-Time Setup (5 minutes)

### Step 1: Initial Login

Run the watcher for the first time:

```bash
cd /mnt/d/Irfan/FTE-H/watchers
.venv/bin/python linkedin_watcher.py
```

**What happens:**
1. Browser window opens (non-headless)
2. LinkedIn login page appears
3. **You manually log in with your credentials**
4. After successful login, session cookies are saved
5. Browser can run headless on future runs

**Session saved to:** `.linkedin_session/cookies.json`

### Step 2: Verify Session Saved

```bash
ls .linkedin_session/cookies.json
```

If this file exists, you're ready! Future runs won't require manual login.

---

## How It Works

```
┌─────────────────────────────────────────────────┐
│  LinkedIn Watcher (Every 15 minutes)            │
└─────────────────────────────────────────────────┘
                    ↓
        ┌───────────────────────┐
        │  Check LinkedIn:      │
        │  - New messages       │
        │  - Connection requests│
        │  - Keyword signals    │
        └───────────────────────┘
                    ↓
        ┌───────────────────────┐
        │  Create task files    │
        │  in Needs_Action/     │
        └───────────────────────┘
                    ↓
        ┌───────────────────────┐
        │  Reasoning Loop picks │
        │  up tasks → Creates   │
        │  Plan.md files        │
        └───────────────────────┘
                    ↓
        ┌───────────────────────┐
        │  Human reviews and    │
        │  takes manual action  │
        └───────────────────────┘
```

---

## Configuration

Edit `linkedin_watcher.py` top section:

```python
# Keywords to monitor in messages and profiles
KEYWORDS = ["hire", "project", "consulting", "ai", "automation", "freelance", "opportunity"]

# Polling interval in minutes
POLL_INTERVAL_MINUTES = 15
```

**Keyword Monitoring:**
- Messages containing these keywords are marked **high priority**
- Connection requests from profiles with these keywords are flagged
- Customize based on your business focus

---

## Running the Watcher

### Continuous Mode (Recommended)

```bash
cd /mnt/d/Irfan/FTE-H/watchers
.venv/bin/python linkedin_watcher.py
```

Runs every 15 minutes. Press Ctrl+C to stop.

### One-Time Check

```bash
.venv/bin/python -c "
from linkedin_watcher import LinkedInWatcher
watcher = LinkedInWatcher('../AI_Employee_Vault', check_interval=0)
watcher._init_browser()
watcher._ensure_logged_in()
items = watcher.check_for_updates()
print(f'Found {len(items)} items')
for item in items:
    watcher.create_action_file(item)
watcher.cleanup()
"
```

---

## Output Examples

### Example 1: LinkedIn Message Detected

**File:** `AI_Employee_Vault/Needs_Action/LINKEDIN_MESSAGE_20260113_1845_John_Smith.md`

```markdown
---
source: linkedin
type: message
detected_at: 2026-01-13T18:45:00
priority: high
status: pending
---

# LinkedIn Message

## Summary
New unread message from **John Smith** on LinkedIn
⚠️ **Contains monitored keywords**

## Details
- **From:** John Smith
- **Preview:** Hi! I saw your profile and have a consulting project...
- **LinkedIn URL:** https://www.linkedin.com/messaging/

## Message Preview
```
Hi! I saw your profile and have a consulting project
that might interest you. Are you available for a call?
```

## Suggested Next Action
1. Open LinkedIn and read the full message
2. Assess if this is a business opportunity, spam, or personal connection
3. If relevant, draft a response for approval
4. If spam/irrelevant, archive or ignore

## Keywords Detected
consulting, project

---
*Detected by LinkedIn Watcher: 20260113_184500*
*Human review required before any action*
```

### Example 2: Connection Request

**File:** `AI_Employee_Vault/Needs_Action/LINKEDIN_CONNECTION_REQUEST_20260113_1850_Sarah_Johnson.md`

```markdown
---
source: linkedin
type: connection_request
detected_at: 2026-01-13T18:50:00
priority: high
status: pending
---

# LinkedIn Connection Request

## Summary
New connection request from **Sarah Johnson**
⚠️ **Profile contains monitored keywords**

## Details
- **Name:** Sarah Johnson
- **Headline/Role:** AI Solutions Architect | Helping businesses automate
- **LinkedIn URL:** https://www.linkedin.com/mynetwork/invitation-manager/

## Suggested Next Action
1. Open LinkedIn and view the requester's full profile
2. Check mutual connections and background
3. Assess if this connection aligns with business goals
4. Decide: Accept, Ignore, or Reply with message

## Keywords Detected
ai, automate

---
*Detected by LinkedIn Watcher: 20260113_185000*
*Manual review and action required*
```

---

## Deduplication

The watcher tracks processed items in:
```
.linkedin_session/processed_ids.json
```

**To reset (reprocess all items):**
```bash
rm .linkedin_session/processed_ids.json
```

---

## Troubleshooting

### "Playwright not installed"
```bash
uv pip install playwright
.venv/bin/python -m playwright install chromium
```

### "Login page appears every time"
- Session cookies may have expired
- Delete `.linkedin_session/cookies.json` and log in again
- LinkedIn may have logged you out remotely

### "Browser doesn't open"
```bash
# Check if Chromium is installed
.venv/bin/python -m playwright install --help
```

### "No items detected"
- LinkedIn DOM selectors may have changed
- Check browser console for errors
- Verify you're logged in: open LinkedIn manually and check

### LinkedIn Rate Limiting
- Default: 15-minute intervals (safe)
- Don't reduce below 10 minutes
- LinkedIn may detect automation if too frequent

---

## Safety & Ethics

**This watcher is designed for personal use only:**
- Monitors YOUR OWN LinkedIn activity
- No scraping of other profiles
- No mass connection requests
- No spam or automated outreach
- Complies with LinkedIn Terms of Service for personal monitoring

**For Business Use:**
- Consult LinkedIn's Commercial Use Terms
- Consider LinkedIn API for official integrations
- Always maintain human oversight

---

## Integration with Silver Tier Workflow

1. **LinkedIn Watcher** → Detects activity → Creates tasks
2. **Reasoning Loop** → Reads tasks → Generates Plan.md
3. **Human** → Reviews plan → Takes manual action on LinkedIn
4. **Approval System** → Optional: Add approval workflow for sensitive responses

---

## Next Steps

After LinkedIn Watcher is running:
1. ✅ Monitor Needs_Action/ folder for new LinkedIn tasks
2. ✅ Review generated Plan.md files
3. ✅ Take manual action on LinkedIn based on plans
4. 🔜 Add LinkedIn posting capability (with approval)
5. 🔜 Integrate with MCP server for notifications

---

*LinkedIn Watcher - Silver Tier*
*Personal AI Employee Hackathon 0*
*Compliance-first, human-in-the-loop design*
