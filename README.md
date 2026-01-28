# AI Employee - Personal Digital FTE

> An autonomous business assistant that monitors emails, processes files, manages invoices/customers via AI chat, and provides human-in-the-loop governance.

**Hackathon Submission: Gold Tier Complete**

---

## What It Does

```
+------------------+     +------------------+     +------------------+
|   DATA SOURCES   |     |   AI EMPLOYEE    |     |     OUTPUTS      |
+------------------+     +------------------+     +------------------+
|                  |     |                  |     |                  |
| Gmail Watcher ---|---->| Task Processing  |---->| Odoo Invoices    |
| File Watcher  ---|---->| AI Reasoning     |---->| Customer Records |
| Manual Input  ---|---->| Human Approval   |---->| Action Reports   |
|                  |     |                  |     |                  |
+------------------+     +------------------+     +------------------+
                               |
                    +----------+----------+
                    |                     |
              Streamlit UI          Vault System
              (Dashboard +          (Approval
               AI Chat)              Workflow)
```

---

## Features

| Feature | Description |
|---------|-------------|
| **AI Chat** | Natural language interface to create invoices, customers, view financials |
| **Gmail Watcher** | Monitors important/starred emails, creates action items |
| **File Watcher** | Drop files in folder, auto-creates tasks |
| **Odoo Integration** | Full ERP connection - invoices, customers, products |
| **Human-in-the-Loop** | Approval workflow via vault folders |
| **Dashboard** | Real-time metrics, charts, data tables |

---

## Quick Start

### 1. Prerequisites

```bash
# Python 3.12
python3 --version

# uv package manager
curl -LsSf https://astral.sh/uv/install.sh | sh

# PostgreSQL (for local Odoo)
sudo apt install postgresql
```

### 2. Setup

```bash
cd watchers

# Install dependencies
uv sync

# Configure environment
cp .env.example .env
# Edit .env with your credentials:
# - OPENAI_API_KEY
# - ODOO_URL, ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD
```

### 3. Run

```bash
# Start Odoo (if using local)
cd ~/odoo && .venv/bin/python odoo19/odoo-bin --addons-path=odoo19/addons -d odoo_local --http-port=8069

# Start Dashboard (new terminal)
cd /mnt/d/Irfan/FTE-H/watchers
uv run streamlit run frontend_app.py

# Start Gmail Watcher (optional, new terminal)
uv run python gmail_watcher.py

# Start File Watcher (optional, new terminal)
uv run python file_watcher.py
```

### 4. Access

- **Dashboard:** http://localhost:8501
- **Odoo:** http://localhost:8069

---

## Project Structure

```
watchers/
├── frontend_app.py      # Streamlit dashboard + AI chat
├── odoo_mcp_server.py   # Odoo ERP integration
├── gmail_watcher.py     # Email monitoring
├── file_watcher.py      # File drop monitoring
├── scheduler.py         # Task scheduling
├── approval_system.py   # Human approval workflow
├── planning_system.py   # AI task planning
├── reasoning_loop.py    # AI reasoning engine
├── credentials.json     # Gmail OAuth (gitignored)
├── token.json           # Gmail token (gitignored)
└── .env                 # Environment vars (gitignored)

AI_Employee_Vault/
├── Needs_Action/        # New tasks from watchers
├── Pending_Approval/    # AI drafts awaiting human review
├── Approved/            # Human-approved actions
├── Rejected/            # Rejected actions
├── Done/                # Completed tasks
├── Logs/                # Audit trail
└── Drop_Folder/         # File watcher input
```

---

## AI Chat Commands

Talk to your AI Employee naturally:

```
"Create a customer named Acme Corp with email acme@example.com"

"Create an invoice for Acme Corp for $2500 for consulting services"

"Show me all unpaid invoices"

"Give me a financial summary"

"List all customers"
```

---

## Approval Workflow

```
1. Watcher detects event (email/file)
         |
         v
2. Task created in Needs_Action/
         |
         v
3. AI processes and creates draft in Pending_Approval/
         |
         v
4. Human reviews:
   ├── Approve --> Move to Approved/ --> Execute
   └── Reject  --> Move to Rejected/ --> Log
         |
         v
5. Completed tasks archived in Done/
```

---

## Technology Stack

| Component | Technology |
|-----------|------------|
| Frontend | Streamlit |
| AI | OpenAI GPT-4 (Function Calling) |
| ERP | Odoo 19 Community Edition |
| Database | PostgreSQL |
| Email | Gmail API (OAuth 2.0) |
| Language | Python 3.12 |

---

## Security

- OAuth 2.0 for Gmail (read-only scope)
- Credentials stored in `.env` (gitignored)
- Human approval required for all actions
- Complete audit trail in Logs/
- No sensitive data in repository

---

## Demo Checklist

- [ ] Odoo running on port 8069
- [ ] Streamlit running on port 8501
- [ ] OpenAI API key configured
- [ ] Sample customers/invoices created
- [ ] Gmail watcher demonstrated
- [ ] File drop demonstrated
- [ ] Approval workflow shown

---

## License

MIT License - Built for Personal AI Employee Hackathon
