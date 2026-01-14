# Gmail MCP Server Setup Guide

## Gold Tier Requirement: External Action Capability

The Gmail MCP Server allows AI-approved actions to send emails through the Gmail API.

---

## What is an MCP Server?

**MCP (Model Context Protocol)** is a standard protocol that allows AI systems to call external tools and perform actions. This is a **Gold Tier requirement** for the Personal AI Employee Hackathon.

The Gmail MCP Server exposes a `send_email` tool that can be called by:
- Ralph Wiggum autonomous loop
- Manual approval workflows
- Other AI agents

---

## Architecture

```
┌─────────────────────┐
│   Ralph Wiggum      │ (Autonomous Loop)
│   Autonomous Loop   │
└──────────┬──────────┘
           │
           ↓ (calls send_email tool)
┌─────────────────────┐
│  Gmail MCP Server   │
│  (This component)   │
└──────────┬──────────┘
           │
           ↓ (Gmail API)
┌─────────────────────┐
│   Gmail / Google    │
│   (Sent emails)     │
└─────────────────────┘
```

---

## Prerequisites

✅ Gmail OAuth credentials (credentials.json)
✅ Gmail OAuth token with **SEND** scope (token.json)
⚠️ **IMPORTANT:** The existing token.json from gmail_watcher.py has READONLY scope only!

---

## Step 1: Update OAuth Scope to Include Send

The current `token.json` only has readonly access. We need to add send capability.

### Option A: Delete token.json and re-authenticate with new scope

```bash
cd /mnt/d/Irfan/FTE-H/watchers

# Backup current token
cp token.json token_readonly.json.backup

# Delete current token
rm token.json

# Run gmail_watcher with updated scope to re-authenticate
.venv/bin/python gmail_watcher.py
```

**IMPORTANT:** When you see the OAuth consent screen, you'll need to approve **both**:
- Read-only access to Gmail (for monitoring)
- Send emails via Gmail (for MCP server)

### Option B: Create separate token for MCP server

Keep the readonly token for monitoring, create a new token for sending.

---

## Step 2: Test MCP Server

### List Available Tools

```bash
.venv/bin/python gmail_mcp_server.py list
```

Expected output:
```
📧 send_email
   Description: Send an email via Gmail. Requires prior human approval.
   Parameters: to, subject, body
```

### Send Test Email

```bash
.venv/bin/python gmail_mcp_server.py test your-email@example.com "Test Subject" "Test body"
```

Expected output:
```
✅ Email sent successfully!
   Message ID: 18d4a2b3c5f6e789
```

---

## Step 3: Use with Ralph Wiggum Loop

The Ralph Wiggum autonomous loop will automatically discover and use this MCP server.

Example approved plan that triggers email sending:
```markdown
---
status: approved
requires_mcp: gmail
---

# Plan: Reply to Client Email

## Steps:
1. Read client email from Needs_Action/
2. Draft professional response
3. Call send_email MCP tool with:
   - to: client@example.com
   - subject: Re: Your inquiry
   - body: [drafted response]
```

When Ralph Wiggum processes this plan, it will:
1. Read the plan
2. Execute step 1 (read email)
3. Execute step 2 (draft response)
4. Execute step 3 (call MCP server to send)

---

## MCP Server API

### send_email Tool

**Input:**
```json
{
  "to": "recipient@example.com",
  "subject": "Email subject",
  "body": "Email body content",
  "from_email": "optional-sender@example.com"
}
```

**Output (Success):**
```json
{
  "success": true,
  "message_id": "18d4a2b3c5f6e789",
  "to": "recipient@example.com",
  "subject": "Email subject",
  "status": "sent"
}
```

**Output (Failure):**
```json
{
  "success": false,
  "error": "Error message",
  "to": "recipient@example.com",
  "subject": "Email subject",
  "status": "failed"
}
```

---

## Safety & Compliance

### Human-in-the-Loop Governance

⚠️ **CRITICAL:** The MCP server only sends emails when:
1. A plan has been manually approved by moving to Approved/ folder
2. Ralph Wiggum loop reads the approved plan
3. The plan explicitly calls the send_email tool
4. All safety checks pass

### Audit Trail

Every email sent is logged with:
- Timestamp
- Recipient
- Subject
- Message ID (for tracking in Gmail)
- Success/failure status

### Rate Limiting

Gmail API has quotas:
- **Quota:** 100 emails per day (free tier)
- **Limit:** 500 emails per day (with approved quota increase)

The MCP server respects these limits automatically.

---

## Troubleshooting

### Error: "Gmail token not found"

**Fix:** Run gmail_watcher.py first to authenticate:
```bash
.venv/bin/python gmail_watcher.py
```

### Error: "Insufficient Permission"

**Fix:** Your token only has readonly scope. Delete token.json and re-authenticate with send scope.

### Error: "Invalid grant"

**Fix:** Token expired. Delete token.json and re-authenticate.

### Error: "Quota exceeded"

**Fix:** You've hit Gmail's daily sending limit (100 emails/day). Wait 24 hours or request quota increase.

---

## Integration with Claude Desktop (Optional)

To use this MCP server with Claude Desktop:

1. Create config file at `~/.config/claude/config.json`:

```json
{
  "mcp_servers": {
    "gmail": {
      "command": "/mnt/d/Irfan/FTE-H/watchers/.venv/bin/python",
      "args": [
        "/mnt/d/Irfan/FTE-H/watchers/gmail_mcp_server.py"
      ]
    }
  }
}
```

2. Restart Claude Desktop

3. Claude will now have access to `send_email` tool

---

## Gold Tier Checklist

- [x] MCP server implemented (`gmail_mcp_server.py`)
- [x] Exposes external action tool (`send_email`)
- [x] Uses existing OAuth credentials
- [x] Proper error handling
- [ ] OAuth scope updated to include send permission
- [ ] Tested with real email send
- [ ] Integrated with Ralph Wiggum loop
- [ ] Documentation complete

---

**Status:** MCP Server implemented, ready for OAuth scope update and testing

**Next:** Update token.json with send scope, then test sending an email
