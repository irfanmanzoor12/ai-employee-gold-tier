# AI Employee - Hackathon Demo Script

**Duration:** 5-7 minutes
**Presenter:** Irfan Manzoor

---

## Pre-Demo Setup (Do Before Presentation)

```bash
# Terminal 1: Start Odoo
cd ~/odoo && .venv/bin/python odoo19/odoo-bin --addons-path=odoo19/addons -d odoo_local --http-port=8069

# Terminal 2: Start Dashboard
cd /mnt/d/Irfan/FTE-H/watchers && uv run streamlit run frontend_app.py

# Open browser tabs:
# Tab 1: http://localhost:8501 (Dashboard)
# Tab 2: http://localhost:8069 (Odoo - optional)
```

---

## Demo Script

### INTRO (30 seconds)

> "Hi, I'm Irfan. I've built an AI Employee - a personal digital assistant that can manage invoices, customers, and monitor emails autonomously.
>
> Let me show you how it works."

---

### PART 1: Dashboard Overview (1 minute)

**[Show Streamlit Dashboard - http://localhost:8501]**

> "This is the AI Employee dashboard. It shows:
> - Real-time metrics from our Odoo ERP
> - Number of invoices and their total value
> - Customer count
> - Recent activity"

**[Click through tabs: Invoices, Customers, Reports]**

> "We can see all invoices, customers, and financial reports in one place."

---

### PART 2: AI Chat - Create Customer (1 minute)

**[Scroll to Chat section]**

> "But the real power is this AI chat. Watch this."

**Type:**
```
Create a customer named TechStart Inc with email hello@techstart.io and phone 555-0100
```

**[Wait for response]**

> "The AI understood my request and created the customer directly in Odoo. No forms, no clicking around."

**[Refresh Customers tab to show new customer]**

---

### PART 3: AI Chat - Create Invoice (1 minute)

> "Now let's create an invoice."

**Type:**
```
Create an invoice for TechStart Inc for $5000 for AI Consulting Services
```

**[Wait for response]**

> "Done. The AI created a professional invoice in seconds."

**[Refresh Invoices tab to show new invoice]**

---

### PART 4: AI Chat - Query Data (1 minute)

> "I can also ask questions about my business."

**Type:**
```
Give me a financial summary
```

**[Wait for response]**

> "The AI analyzes all my invoices and gives me insights - total revenue, paid vs unpaid, top customers."

**Type:**
```
Show me all unpaid invoices
```

> "Perfect for tracking what's outstanding."

---

### PART 5: Gmail Watcher (1 minute)

**[Show AI_Employee_Vault/Needs_Action folder]**

> "The system also monitors my email automatically."

```bash
ls /mnt/d/Irfan/FTE-H/AI_Employee_Vault/Needs_Action/
```

> "When important emails arrive, the Gmail Watcher creates task files here. Each one contains:
> - Email summary
> - Suggested actions
> - Priority level"

**[Open one EMAIL_*.md file to show contents]**

---

### PART 6: Human-in-the-Loop (30 seconds)

> "Importantly, the AI never acts without approval. Here's the workflow:"

```
Email arrives → Watcher creates task → AI suggests action → HUMAN APPROVES → Action executes
```

> "Files move through folders: Needs_Action → Pending_Approval → Approved → Done"

> "This ensures human oversight while still automating the tedious work."

---

### CONCLUSION (30 seconds)

> "To summarize, my AI Employee:
>
> 1. **Automates** - Creates invoices and customers via natural language
> 2. **Monitors** - Watches email for important items
> 3. **Integrates** - Connects to real Odoo ERP
> 4. **Governs** - Human approval for all actions
>
> It's like having a digital assistant that handles the boring stuff so you can focus on what matters.
>
> Thank you!"

---

## Backup Demo Commands

If something goes wrong, use these proven commands:

```
Create a customer named Demo Corp with email demo@corp.com

Create an invoice for Demo Corp for $1500 for Website Development

List all customers

Show me all invoices

Give me a financial summary

How many unpaid invoices do I have?
```

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Chat not responding | Check OPENAI_API_KEY in .env |
| No Odoo connection | Restart Odoo server |
| Dashboard error | Check .env has correct ODOO credentials |
| Gmail tasks empty | Run `uv run python gmail_watcher.py` |

---

## Key Talking Points for Judges

1. **Real Integration** - Not a mockup, actually creates records in Odoo
2. **OpenAI Function Calling** - AI decides which API to call based on natural language
3. **Production Ready** - Uses OAuth for Gmail, proper error handling
4. **Extensible** - Easy to add more tools/integrations
5. **Human-in-the-Loop** - Safety through approval workflow
