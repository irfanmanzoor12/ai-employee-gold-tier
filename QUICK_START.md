# 🚀 Quick Start Guide

Get the Personal AI Employee running in 5 minutes.

## Prerequisites

- Python 3.11+
- Gmail account with OAuth credentials
- Internet connection

## Installation

### 1. Clone Repository
```bash
git clone https://github.com/irfanmanzoor12/ai-employee-gold-tier.git
cd ai-employee-gold-tier
```

### 2. Create Virtual Environment
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
playwright install chromium
```

### 4. Set Up Environment Variables
```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
```env
OPENAI_API_KEY=your_openai_api_key_here
GMAIL_ACCOUNT=your_email@gmail.com
```

### 5. Configure Gmail OAuth (Optional for full features)

**For Demo/Testing**: Skip this step - the system works in sandbox mode.

**For Production**:
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project → Enable Gmail API
3. Create OAuth 2.0 credentials (Desktop app)
4. Download credentials → Save as `credentials.json` in project root
5. Run first-time auth:
```bash
.venv/bin/python gmail_mcp_server.py --setup
```

## Verification

### Test Bronze Tier (File Monitoring)
```bash
# Check vault structure
ls -la ../AI_Employee_Vault/

# Check watchers
ls -1 *_watcher.py
```
**Expected**: 7 watchers, vault with 7 folders

### Test Silver Tier (Complete System)
```bash
.venv/bin/python test_silver_tier_complete.py
```
**Expected**: ✅ 30/30 tests passing

### Test Gold Tier (Advanced Features)
```bash
.venv/bin/python test_gold_tier_complete.py
```
**Expected**: ✅ 18/18 tests passing

## Quick Demos

### Demo 1: Agent Skills Framework
```bash
.venv/bin/python test_skills.py
```
**Expected**: Discovers 2 skills (ReasoningSkill, DraftingSkill)

### Demo 2: QuickBooks MCP Server
```bash
.venv/bin/python quickbooks_mcp_server.py summary
```
**Expected**: Financial summary with $48,920.50 in assets

### Demo 3: Ralph Wiggum Autonomous Loop
```bash
# Create test plan
cat > ../AI_Employee_Vault/Plans/PLAN_TEST_DEMO.md << 'EOF'
# Test Plan

## Steps
1. Check account balances using QuickBooks
2. Get recent transactions from last 7 days
3. Send summary email to team

## Context
Testing Ralph Wiggum integration with QuickBooks MCP.
EOF

# Move to approved folder
mv ../AI_Employee_Vault/Plans/PLAN_TEST_DEMO.md ../AI_Employee_Vault/Plans_Approved/

# Run Ralph Wiggum
.venv/bin/python ralph_wiggum_loop.py
```
**Expected**: Executes all 3 steps autonomously

### Demo 4: Weekly Business Audit
```bash
.venv/bin/python weekly_audit.py
```
**Expected**: Generates comprehensive CEO briefing in Reports/

## ONE-COMMAND DEMO (30 seconds)

Run all tiers in sequence:
```bash
cd /mnt/d/Irfan/FTE-H/watchers && \
echo "=== BRONZE: Vault Structure ===" && ls -la ../AI_Employee_Vault/ && \
echo -e "\n=== SILVER: Complete Test ===" && .venv/bin/python test_silver_tier_complete.py | tail -15 && \
echo -e "\n=== GOLD: Complete Test ===" && .venv/bin/python test_gold_tier_complete.py | tail -20
```

## Troubleshooting

### Import Errors
```bash
# Verify dependencies installed
pip list | grep openai
pip list | grep playwright
```

### OAuth Issues
```bash
# Reset tokens
rm token.json token_readonly.json
python gmail_mcp_server.py --setup
```

### Vault Not Found
```bash
# Create vault structure
mkdir -p ../AI_Employee_Vault/{Needs_Action,In_Progress,Pending_Approval,Plans,Plans_Approved,Done,Logs,Reports}
```

## Next Steps

1. **Read Full Documentation**: See [GOLD_TIER_COMPLETE.md](GOLD_TIER_COMPLETE.md)
2. **Explore Architecture**: See [ARCHITECTURE.md](ARCHITECTURE.md)
3. **Run More Demos**: See [DEMO_GUIDE.md](DEMO_GUIDE.md)
4. **Check Demo Vault**: Browse `demo_vault/` for real system output

## Support

- GitHub Issues: https://github.com/irfanmanzoor12/ai-employee-gold-tier/issues
- Documentation: All `.md` files in project root
- Test Files: `test_*.py` files show usage examples

---

**Estimated Setup Time**: 5-10 minutes (15 minutes with OAuth)
**Estimated Demo Time**: 2-5 minutes per demo
**Total Test Coverage**: 48/48 tests (100%)
