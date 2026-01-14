# LinkedIn Drafting Agent Setup - Silver Tier

## 🚨 CRITICAL SAFETY NOTICE

**This agent is DRAFT-ONLY:**
- ❌ **NO automatic posting** to LinkedIn
- ❌ **NO LinkedIn API integration**
- ❌ **NO browser automation for posting**
- ✅ **ONLY generates draft content**
- ✅ **ALL drafts require human approval**
- ✅ **Manual posting only**

**Perfect for hackathon judging:** Safe, inspectable, human-governed.

---

## Prerequisites

### 1. OpenAI API Key

Already set from Reasoning Loop:
```bash
echo $OPENAI_API_KEY
```

If not set:
```bash
export OPENAI_API_KEY='your-key-here'
```

### 2. Verify Environment

```bash
cd /mnt/d/Irfan/FTE-H/watchers
.venv/bin/python -c "import openai; print('✅ OpenAI ready')"
```

---

## How It Works

```
┌──────────────────────────────────────────────────┐
│  LinkedIn Watcher                                 │
│  Detects: Messages, Requests, Keyword Signals    │
└──────────────────────────────────────────────────┘
                    ↓
        Creates task in Needs_Action/
                    ↓
┌──────────────────────────────────────────────────┐
│  LinkedIn Drafting Agent (YOU ARE HERE)          │
│  Reads signals → Generates drafts                │
└──────────────────────────────────────────────────┘
                    ↓
        Saves draft to Pending_Approval/
                    ↓
┌──────────────────────────────────────────────────┐
│  Human Review                                     │
│  Review → Edit → Approve/Reject                   │
└──────────────────────────────────────────────────┘
                    ↓
        Manual posting on LinkedIn
                    ↓
        Move to Done/ folder
```

---

## Running the Agent

### Continuous Mode (Recommended)

```bash
cd /mnt/d/Irfan/FTE-H/watchers
.venv/bin/python linkedin_drafting_agent.py
```

**Behavior:**
- Runs every 30 minutes
- Checks Needs_Action/ for LinkedIn signals
- Generates drafts for unprocessed signals
- Saves to Pending_Approval/
- Press Ctrl+C to stop

### One-Time Processing

```bash
.venv/bin/python -c "
from linkedin_drafting_agent import LinkedInDraftingAgent
agent = LinkedInDraftingAgent('../AI_Employee_Vault')
agent.process_signals()
print('✅ Processing complete')
"
```

---

## Configuration

Edit `linkedin_drafting_agent.py` top section:

```python
# Drafting preferences
DEFAULT_TONE = "professional, helpful, non-spammy"
DEFAULT_AUDIENCE = "founders, business owners, tech leaders"
MAX_DRAFT_LENGTH = 1500  # characters

# Check interval (minutes)
POLL_INTERVAL_MINUTES = 30
```

**Customization:**
- **Tone:** Adjust based on your brand voice
- **Audience:** Target specific professional groups
- **Length:** Shorter for mobile, longer for thought leadership
- **Interval:** How often to check for new signals

---

## Business Context

The agent loads business context from your vault:

**Files it reads:**
1. `AI_Employee_Vault/Company_Handbook.md`
2. `AI_Employee_Vault/Business_Goals.md`

**What to include:**
- Your business offering
- Target market
- Unique value proposition
- Tone/voice guidelines
- Topics you want to discuss

**Example Company_Handbook.md:**
```markdown
# Company Handbook

## About Us
We help businesses implement AI and automation solutions.

## Target Audience
- Founders looking to scale
- Business owners reducing operational costs
- Tech leaders exploring AI adoption

## Our Approach
- No buzzwords or hype
- Practical, implementable solutions
- Focus on ROI and real results

## Tone
- Professional but approachable
- Educational, not sales-y
- Experience-based insights
```

---

## Output Format

Every draft is saved as a Markdown file in `Pending_Approval/` with this structure:

```markdown
---
type: linkedin_draft
status: draft_only
approval_required: true
generated_at: 2026-01-13T19:00:00
source_signal: LINKEDIN_MESSAGE_20260113_184500_Alex_Chen.md
audience: founders, business owners, tech leaders
tone: professional, helpful, non-spammy
risk_level: low
---

# LinkedIn Draft (NOT POSTED)

⚠️ **THIS IS A DRAFT ONLY - NOT POSTED TO LINKEDIN**
⚠️ **HUMAN APPROVAL REQUIRED BEFORE POSTING**

---

## Draft Text

[Generated LinkedIn post content here]

---

## Why This Works

- [Explanation of strategy]
- [Why this resonates with audience]
- [What makes it credible]

---

## Optional Variations

**Variation A (shorter):**
[Condensed version]

**Variation B (more conversational):**
[Relaxed tone version]

---

## Compliance Check

- [x] Draft only - NOT posted
- [x] No auto-posting capability
- [x] Human approval required
- [x] Manual posting only

---

## Next Steps for Human

1. **Review** this draft carefully
2. **Edit** as needed for your voice
3. **Decide**: Approve, Reject, or Request Revision
4. **Post Manually** on LinkedIn if approved
5. **Move to Done/** after posting (or Rejected/ if declined)

---

*Generated by LinkedIn Drafting Agent - Silver Tier*
```

---

## Workflow Example

### Step 1: LinkedIn Watcher Detects Signal

File created: `Needs_Action/LINKEDIN_MESSAGE_20260113_184500_Alex_Chen.md`

Signal contains: Consulting project inquiry with "AI" and "automation" keywords.

### Step 2: Drafting Agent Processes Signal

Runs automatically (or manually triggered):
```bash
.venv/bin/python linkedin_drafting_agent.py
```

Reads the signal, generates a professional draft post.

### Step 3: Draft Saved for Review

File created: `Pending_Approval/DRAFT_LINKEDIN_MESSAGE_20260113_184500_Alex_Chen.md`

Contains:
- Main draft text
- Why it works
- Optional variations
- Compliance checklist

### Step 4: Human Reviews Draft

Open the draft file in Obsidian or text editor.

**Options:**
- ✅ **Approve:** Copy text, post manually on LinkedIn
- ✏️ **Edit:** Modify draft, then post
- ❌ **Reject:** Move to Rejected/ folder
- 🔄 **Revise:** Add feedback, regenerate

### Step 5: Manual Posting

1. Copy approved draft text
2. Open LinkedIn in browser
3. Create new post
4. Paste and format
5. Review one more time
6. Click "Post" **manually**

### Step 6: Archive

Move draft to `Done/` folder for record-keeping.

---

## Testing

### Test with Existing LinkedIn Signals

```bash
# Check if there are LinkedIn signals
ls ../AI_Employee_Vault/Needs_Action/LINKEDIN_*.md

# Run agent once
.venv/bin/python -c "
from linkedin_drafting_agent import LinkedInDraftingAgent
agent = LinkedInDraftingAgent('../AI_Employee_Vault')
agent.process_signals()
"

# Check drafts created
ls ../AI_Employee_Vault/Pending_Approval/DRAFT_LINKEDIN_*.md
```

### Create Test Signal

```bash
# Create a test signal manually
cat > ../AI_Employee_Vault/Needs_Action/LINKEDIN_TEST_SIGNAL.md << 'EOF'
---
source: linkedin
type: message
detected_at: 2026-01-13T19:00:00
priority: high
status: pending
---

# LinkedIn Message

## Summary
New message from potential client interested in AI automation.

## Details
- **From:** Test Contact
- **Preview:** "Hi, I saw your work with AI. We're looking for someone to help automate our sales process. Can we discuss?"

## Keywords Detected
ai, automation
EOF

# Run drafting agent
.venv/bin/python -c "
from linkedin_drafting_agent import LinkedInDraftingAgent
agent = LinkedInDraftingAgent('../AI_Employee_Vault')
agent.process_signals()
print('✅ Test complete')
"

# View generated draft
cat ../AI_Employee_Vault/Pending_Approval/DRAFT_LINKEDIN_TEST_SIGNAL.md
```

---

## Deduplication

The agent tracks processed signals in:
```
.linkedin_drafts/processed_signals.json
```

**To regenerate drafts (reset tracking):**
```bash
rm .linkedin_drafts/processed_signals.json
```

---

## Troubleshooting

### "OPENAI_API_KEY not set"
```bash
export OPENAI_API_KEY='your-key-here'
# Make permanent:
echo 'export OPENAI_API_KEY="your-key"' >> ~/.bashrc
source ~/.bashrc
```

### "No signals found"
Check if LinkedIn Watcher has created any signal files:
```bash
ls ../AI_Employee_Vault/Needs_Action/LINKEDIN_*.md
```

If empty, LinkedIn Watcher hasn't detected anything yet.

### Drafts too generic
Update your business context:
- Edit `Company_Handbook.md`
- Add more specific details about your offering
- Include examples of topics you discuss
- Clarify your unique positioning

### Draft quality issues
Adjust configuration in `linkedin_drafting_agent.py`:
- Change `DEFAULT_TONE`
- Modify `MAX_DRAFT_LENGTH`
- Update prompt template for more specific instructions

---

## Safety & Compliance

### What This Agent Does
- ✅ Reads LinkedIn signals from Needs_Action/
- ✅ Generates draft content using AI
- ✅ Saves drafts for human review
- ✅ Tracks processed signals

### What This Agent DOES NOT Do
- ❌ Post to LinkedIn
- ❌ Comment on posts
- ❌ Send messages
- ❌ Accept connections
- ❌ Use LinkedIn API
- ❌ Automate any LinkedIn actions

### Human Approval Required For
- **Every single post** before it goes live
- **All edits** to generated content
- **Final decision** to post or reject

---

## Silver Tier Integration

Complete workflow:
1. **LinkedIn Watcher** → Detects signals (read-only)
2. **Reasoning Loop** → Creates Plan.md for strategy
3. **Drafting Agent** → Generates post drafts
4. **Human** → Reviews, approves, posts manually
5. **Done/** → Archives completed posts

---

## Next Steps

After drafting agent is running:
1. ✅ Generate drafts from LinkedIn signals
2. ✅ Review and refine business context
3. ✅ Test with real signals from LinkedIn Watcher
4. 🔜 Set up approval workflow (move files between folders)
5. 🔜 Track posted content for performance analysis

---

*LinkedIn Drafting Agent - Silver Tier*
*Draft-only, human-governed content generation*
*Personal AI Employee Hackathon 0*
