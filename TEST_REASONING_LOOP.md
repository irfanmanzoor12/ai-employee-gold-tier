# Test Reasoning Loop - Quick Start

## ✅ What's Ready

1. ✅ `reasoning_loop.py` - Fully implemented with OpenAI
2. ✅ Test task created in `Needs_Action/TEST_TASK_20260113.md`
3. ✅ Plans folder ready

## 🚀 Quick Test (5 minutes)

### Step 1: Set Your OpenAI API Key

```bash
export OPENAI_API_KEY='your-openai-key-here'
```

### Step 2: Install OpenAI SDK (if needed)

```bash
pip3 install openai --user
# or
pip install openai --user
```

### Step 3: Run One-Time Test

```bash
cd /mnt/d/Irfan/FTE-H/watchers

python3 -c "
from reasoning_loop import ReasoningLoop
import os

# Test API key
if not os.getenv('OPENAI_API_KEY'):
    print('❌ Set OPENAI_API_KEY first!')
    exit(1)

print('🧠 Testing Reasoning Loop...')
print('='*70)

loop = ReasoningLoop('../AI_Employee_Vault')
loop.process_tasks()

print()
print('✅ Processing complete!')
print()
print('Check results:')
print('ls ../AI_Employee_Vault/Plans/PLAN_TEST_TASK_*.md')
"
```

### Step 4: Verify Plan Was Created

```bash
# Check if plan exists
ls ../AI_Employee_Vault/Plans/PLAN_TEST_TASK_*.md

# View the plan
cat ../AI_Employee_Vault/Plans/PLAN_TEST_TASK_*.md
```

---

## Expected Output

**If successful:**
```
🧠 Testing Reasoning Loop...
======================================================================
2026-01-13 17:45:00 - ReasoningLoop - INFO - Found 1 tasks that need planning
2026-01-13 17:45:00 - ReasoningLoop - INFO - Processing task: TEST_TASK_20260113.md
2026-01-13 17:45:00 - ReasoningLoop - INFO - Calling OpenAI API to analyze: TEST_TASK_20260113.md
2026-01-13 17:45:02 - ReasoningLoop - INFO - Plan generated for: TEST_TASK_20260113.md
2026-01-13 17:45:02 - ReasoningLoop - INFO - Created plan: PLAN_TEST_TASK_20260113.md
2026-01-13 17:45:02 - ReasoningLoop - INFO - ✅ Plan created: PLAN_TEST_TASK_20260113.md

✅ Processing complete!

Check results:
ls ../AI_Employee_Vault/Plans/PLAN_TEST_TASK_*.md
```

**Plan file will contain:**
- Objective
- Analysis
- Step-by-step approach
- Required resources
- Risks & considerations
- Success criteria

---

## 🔄 Run Continuously (Optional)

To monitor Needs_Action/ folder every 5 minutes:

```bash
python3 reasoning_loop.py
```

Press Ctrl+C to stop.

---

## Troubleshooting

### "No module named 'openai'"
```bash
pip3 install openai --user
# or create fresh venv:
python3 -m venv ~/reasoning_venv
source ~/reasoning_venv/bin/activate
pip install openai
python reasoning_loop.py
```

### "OPENAI_API_KEY not set"
```bash
export OPENAI_API_KEY='sk-proj-...'

# Make permanent:
echo 'export OPENAI_API_KEY="sk-proj-..."' >> ~/.bashrc
source ~/.bashrc
```

### "Authentication failed"
- Check API key is correct
- Check you have credits/free tier access
- Try: `curl https://api.openai.com/v1/models -H "Authorization: Bearer $OPENAI_API_KEY"`

---

## What's Next?

After successful test:
1. ✅ Reasoning Loop works!
2. ⏭️ Move to: WhatsApp Watcher or LinkedIn Auto-Posting
3. 🔄 Let watchers create tasks → Reasoning Loop generates plans automatically

---

*Silver Tier - Personal AI Employee Hackathon 0*
