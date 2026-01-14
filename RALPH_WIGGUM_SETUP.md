# Ralph Wiggum Autonomous Loop - Gold Tier

## What is Ralph Wiggum?

**Ralph Wiggum Loop** is the autonomous agent that executes approved multi-step plans. Named after the Simpsons character, it's a simple, continuous loop that keeps working on approved tasks.

**Gold Tier Requirement:** Autonomous multi-step task completion ✅

---

## How It Works

```
┌─────────────────────────────────────────────────────────────┐
│                  RALPH WIGGUM AUTONOMOUS LOOP                │
└─────────────────────────────────────────────────────────────┘

STEP 1: Monitor Approved/ Folder
   ↓
STEP 2: Find approved plans (PLAN_*.md files)
   ↓
STEP 3: Parse steps from each plan
   ↓
STEP 4: Execute steps autonomously:
   ├─ Email steps → Call Gmail MCP Server
   ├─ Generate steps → Use OpenAI
   ├─ Read steps → Acknowledge
   └─ Other steps → Log
   ↓
STEP 5: Log all actions (audit trail)
   ↓
STEP 6: Move completed plans to Done/
   ↓
STEP 7: Wait 60 seconds, repeat
```

---

## Safety Features

### Human-in-the-Loop Governance

Ralph Wiggum **ONLY** executes plans that:
1. ✅ Have been manually moved to Approved/ folder
2. ✅ Follow the expected plan format
3. ✅ Don't require dangerous operations

**No plan is executed without explicit human approval.**

### Audit Trail

Every action is logged to `Logs/ralph_wiggum_execution.jsonl`:

```json
{
  "timestamp": "2026-01-14T10:30:00",
  "plan_file": "PLAN_REPLY_TO_CLIENT.md",
  "step": 1,
  "action": "Send email to client@example.com",
  "result": "{\"success\": true, \"message_id\": \"18d4...\"}",
  "success": true
}
```

### Graceful Error Handling

- If a step fails, logs the error and continues to next step
- Never crashes on unexpected input
- Can be stopped at any time with Ctrl+C

---

## Prerequisites

✅ OpenAI API key set: `export OPENAI_API_KEY='your-key'`
✅ Gmail MCP Server working (test with `gmail_mcp_server.py`)
✅ Approved/ folder exists in vault

---

## Usage

### Start the Loop

```bash
cd /mnt/d/Irfan/FTE-H/watchers
.venv/bin/python ralph_wiggum_loop.py
```

**Output:**
```
======================================================================
🤖 Ralph Wiggum Autonomous Loop - Gold Tier
======================================================================

Ralph Wiggum Loop initialized
Monitoring: ../AI_Employee_Vault/Approved
Check interval: 60 seconds
🤖 Ralph Wiggum Loop started
Press Ctrl+C to stop
```

The loop will now:
- Check Approved/ folder every 60 seconds
- Execute any plans it finds
- Move completed plans to Done/
- Log all actions

### Stop the Loop

Press `Ctrl+C` in the terminal

---

## Plan Format

Ralph Wiggum understands plans with a **Steps** section:

```markdown
---
status: approved
type: email_response
---

# Plan: Reply to Client Email

## Context
Client asked about AI consulting services.

## Steps:
1. Review client email details
2. Generate professional response
3. Send email to client@example.com with subject "Re: AI Consulting Inquiry"

## Expected Outcome
Client receives professional response within 1 hour.
```

The loop will:
- Parse steps 1-3
- Detect step 3 is an email action
- Extract parameters (to, subject, body)
- Call Gmail MCP Server to send
- Log the result

---

## Supported Action Types

### 1. Email Actions

**Triggers:** Words like "send", "email", "reply", "respond"

**Example:**
```
3. Send email to john@example.com with subject "Meeting Follow-up"
```

**Execution:**
- Uses OpenAI to extract email parameters
- Calls Gmail MCP Server
- Returns message ID

---

### 2. Generate Actions

**Triggers:** Words like "generate", "create", "draft", "write"

**Example:**
```
2. Generate a professional LinkedIn post about AI automation
```

**Execution:**
- Uses OpenAI to generate content
- Saves output in execution log
- Can be reviewed in logs

---

### 3. Read Actions

**Triggers:** Words like "read", "review", "analyze", "check"

**Example:**
```
1. Review the client email in Needs_Action/
```

**Execution:**
- Acknowledges the step
- Logs that manual review is needed
- Continues to next step

---

### 4. Other Actions

Any step that doesn't match above categories is logged and acknowledged.

---

## Testing Ralph Wiggum

### Test 1: Create a Test Plan

```bash
cat > ../AI_Employee_Vault/Approved/PLAN_TEST_RALPH.md << 'EOF'
---
status: approved
type: test
---

# Test Plan: Ralph Wiggum Email Test

## Steps:
1. Review this test plan
2. Generate a friendly greeting message
3. Send email to YOUR_EMAIL@gmail.com with subject "Ralph Wiggum Test"

## Expected Outcome
You receive a test email from Ralph Wiggum loop.
EOF
```

**Replace `YOUR_EMAIL@gmail.com` with your actual email!**

### Test 2: Run Ralph Wiggum

```bash
.venv/bin/python ralph_wiggum_loop.py
```

### Test 3: Watch the Execution

You should see:
```
Found 1 approved plan(s)
🤖 Executing plan: PLAN_TEST_RALPH.md
Found 3 steps to execute
Step 1: Review this test plan
  Action type: read
  ✅ Step 1 completed
Step 2: Generate a friendly greeting message
  Action type: generate
  ✅ Step 2 completed
Step 3: Send email to YOUR_EMAIL@gmail.com with subject "Ralph Wiggum Test"
  Action type: email
  ✅ Step 3 completed
✅ Plan moved to Done: PLAN_TEST_RALPH.md
```

### Test 4: Check Your Email

You should receive an email with subject "Ralph Wiggum Test"!

### Test 5: Review Logs

```bash
cat ../AI_Employee_Vault/Logs/ralph_wiggum_execution.jsonl
```

You'll see detailed logs of each step execution.

---

## Integration with Full System

Ralph Wiggum works with the rest of your AI Employee system:

```
1. Gmail Watcher detects important email
   ↓
2. Creates task in Needs_Action/
   ↓
3. Reasoning Loop analyzes task
   ↓
4. Creates strategic plan in Plans/
   ↓
5. HUMAN reviews and moves plan to Approved/
   ↓
6. Ralph Wiggum executes the plan
   ↓
7. Gmail MCP Server sends response
   ↓
8. Plan moved to Done/
```

**Fully autonomous with human governance at key checkpoint!**

---

## Troubleshooting

### No plans being executed

**Check:**
1. Plans are in Approved/ folder (not Plans/)
2. Plan files start with `PLAN_*.md`
3. Plans have a Steps section
4. Ralph Wiggum is running (`.venv/bin/python ralph_wiggum_loop.py`)

### Steps failing

**Check execution log:**
```bash
cat ../AI_Employee_Vault/Logs/ralph_wiggum_execution.jsonl | tail -20
```

Look for `"success": false` entries and check the error messages.

### Email steps failing

**Check:**
1. Gmail MCP Server is authenticated
2. Test MCP server directly: `.venv/bin/python gmail_mcp_server.py test`
3. Check if email parameters can be extracted from step description

---

## Production Deployment

### Run as Background Service

```bash
# Start in background
nohup .venv/bin/python ralph_wiggum_loop.py > ralph_wiggum.log 2>&1 &

# Check if running
ps aux | grep ralph_wiggum

# View logs
tail -f ralph_wiggum.log

# Stop
pkill -f ralph_wiggum_loop.py
```

### Run with Cron (Every 5 Minutes)

```bash
# Edit crontab
crontab -e

# Add this line:
*/5 * * * * cd /mnt/d/Irfan/FTE-H/watchers && .venv/bin/python ralph_wiggum_loop.py --once

# Note: Use a modified version that exits after one check
```

---

## Gold Tier Checklist

- [x] Autonomous loop implemented
- [x] Multi-step plan execution
- [x] MCP server integration (Gmail)
- [x] AI-powered step execution (OpenAI)
- [x] Human-in-the-loop governance (Approved/ folder)
- [x] Audit logging (execution.jsonl)
- [x] Error handling and graceful degradation
- [x] Documentation complete
- [ ] Tested with real plans
- [ ] Integrated with full workflow

---

**Status:** Ralph Wiggum Loop implemented and ready for testing!

**Next:** Create test plan and execute it
