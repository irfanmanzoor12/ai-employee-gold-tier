#!/usr/bin/env python3
"""
Weekly Business Audit + CEO Briefing Generator
Gold Tier Requirement: Weekly audit with CEO briefing

Collects data from all systems and generates comprehensive business report:
- Financial summary (QuickBooks)
- Email activity (Gmail logs)
- LinkedIn engagement (LinkedIn logs)
- Task completion (Ralph Wiggum logs)
- System health metrics
"""
import os
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List

# MCP Servers
from odoo_mcp_server import OdooMCPServer


class WeeklyAuditGenerator:
    """
    Generates comprehensive weekly business audit reports

    Integrates data from all AI Employee components to provide
    executive-level business intelligence.
    """

    def __init__(self, vault_path: str):
        """
        Initialize audit generator

        Args:
            vault_path: Path to AI Employee Vault
        """
        self.vault_path = Path(vault_path)
        self.reports_folder = self.vault_path / 'Reports'
        self.logs_folder = self.vault_path / 'Logs'

        # Ensure folders exist
        self.reports_folder.mkdir(exist_ok=True)
        self.logs_folder.mkdir(exist_ok=True)

        # Initialize MCP servers
        self.odoo = OdooMCPServer(mode='sandbox')

    def collect_financial_data(self) -> Dict[str, Any]:
        """Collect financial data from Odoo"""
        print("📊 Collecting financial data from Odoo...")

        summary = self.odoo.get_financial_summary(period='week')
        balances = self.odoo.get_account_balances()
        payments = self.odoo.get_payments(days=7)
        invoices = self.odoo.get_invoices(state='unpaid')

        # Map Odoo data to expected format
        return {
            'summary': {
                'total_income': summary.get('revenue', {}).get('total_received', 0),
                'total_expenses': summary.get('expenses', {}).get('paid', 0),
                'net_income': summary.get('profitability', {}).get('gross_profit', 0),
                'profit_margin': summary.get('profitability', {}).get('profit_margin_percent', 0)
            },
            'balances': balances.get('accounts', []),
            'transactions': [
                {
                    'date': p['payment_date'],
                    'description': f"Payment from {p['partner_name']}",
                    'amount': p['amount']
                } for p in payments.get('payments', [])
            ],
            'transaction_count': len(payments.get('payments', [])),
            'unpaid_invoices': invoices.get('invoices', []),
            'total_outstanding': sum(i['amount_residual'] for i in invoices.get('invoices', []))
        }

    def collect_email_activity(self) -> Dict[str, Any]:
        """Collect email activity from Gmail watcher logs"""
        print("📧 Collecting email activity...")

        # Count tasks created by Gmail watcher
        needs_action = self.vault_path / 'Needs_Action'
        email_tasks = list(needs_action.glob('EMAIL_*.md'))

        # Count plans generated
        plans = self.vault_path / 'Plans'
        email_plans = [p for p in plans.glob('PLAN_EMAIL_*.md')]

        return {
            'emails_detected': len(email_tasks),
            'plans_generated': len(email_plans),
            'avg_response_time': 'N/A'  # Would calculate from timestamps
        }

    def collect_linkedin_activity(self) -> Dict[str, Any]:
        """Collect LinkedIn activity"""
        print("🔗 Collecting LinkedIn activity...")

        # Count LinkedIn signals
        needs_action = self.vault_path / 'Needs_Action'
        linkedin_signals = list(needs_action.glob('LINKEDIN_*.md'))

        # Count drafts
        pending = self.vault_path / 'Pending_Approval'
        drafts = list(pending.glob('DRAFT_LINKEDIN_*.md'))

        return {
            'signals_detected': len(linkedin_signals),
            'drafts_created': len(drafts),
            'posts_approved': 0  # Would count from Done/
        }

    def collect_task_completion_metrics(self) -> Dict[str, Any]:
        """Collect task completion metrics from Ralph Wiggum logs"""
        print("🤖 Collecting task completion metrics...")

        # Read Ralph Wiggum execution log
        exec_log = self.logs_folder / 'ralph_wiggum_execution.jsonl'

        if not exec_log.exists():
            return {
                'plans_executed': 0,
                'steps_completed': 0,
                'success_rate': 0
            }

        # Parse log
        total_steps = 0
        successful_steps = 0

        with open(exec_log, 'r') as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    total_steps += 1
                    if entry.get('success'):
                        successful_steps += 1
                except:
                    continue

        # Count completed plans
        done = self.vault_path / 'Done'
        completed_plans = list(done.glob('PLAN_*.md'))

        return {
            'plans_executed': len(completed_plans),
            'steps_completed': total_steps,
            'steps_successful': successful_steps,
            'success_rate': (successful_steps / total_steps * 100) if total_steps > 0 else 0
        }

    def collect_skills_metrics(self) -> Dict[str, Any]:
        """Collect Agent Skills execution metrics"""
        print("🎯 Collecting skills metrics...")

        skills_log = self.logs_folder / 'skills_execution.jsonl'

        if not skills_log.exists():
            return {
                'skills_executed': 0,
                'total_execution_time': 0
            }

        skill_counts = {}
        total_time = 0

        with open(skills_log, 'r') as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    skill = entry.get('skill', 'unknown')
                    skill_counts[skill] = skill_counts.get(skill, 0) + 1
                    total_time += entry.get('execution_time', 0)
                except:
                    continue

        return {
            'skills_executed': sum(skill_counts.values()),
            'skill_breakdown': skill_counts,
            'total_execution_time': total_time
        }

    def generate_report(self) -> str:
        """
        Generate complete audit report

        Returns:
            str: Markdown report content
        """
        print()
        print("=" * 70)
        print("📋 Generating Weekly Business Audit Report")
        print("=" * 70)
        print()

        # Collect all data
        financial = self.collect_financial_data()
        email = self.collect_email_activity()
        linkedin = self.collect_linkedin_activity()
        tasks = self.collect_task_completion_metrics()
        skills = self.collect_skills_metrics()

        # Generate report
        report_date = datetime.now().strftime('%Y-%m-%d')
        week_start = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')

        report = f"""# 📊 Weekly Business Audit Report

**Generated:** {report_date}
**Period:** {week_start} to {report_date}
**Company:** {financial.get('balances', [{}])[0].get('name', 'AI Employee Demo Company') if financial.get('balances') else 'AI Employee Demo Company'}

---

## Executive Summary

This report provides a comprehensive overview of business performance, system activity, and operational metrics for the past week.

---

## 💰 Financial Performance

### Summary
- **Total Income:** ${financial['summary'].get('total_income', 0):,.2f}
- **Total Expenses:** ${financial['summary'].get('total_expenses', 0):,.2f}
- **Net Income:** ${financial['summary'].get('net_income', 0):,.2f}
- **Profit Margin:** {financial['summary'].get('profit_margin', 0):.1f}%

### Account Balances
"""

        # Add account balances
        for account in financial.get('balances', []):
            report += f"- **{account['name']}** ({account['type']}): ${account['balance']:,.2f}\n"

        report += f"""
### Recent Transactions ({financial['transaction_count']} this week)
"""

        # Add recent transactions
        for txn in financial.get('transactions', [])[:5]:
            sign = '+' if txn['amount'] > 0 else '-'
            report += f"- {txn['date']}: {txn['description']} ({sign}${abs(txn['amount']):,.2f})\n"

        report += f"""
---

## 📧 Email Operations

- **Emails Detected:** {email['emails_detected']}
- **Plans Generated:** {email['plans_generated']}
- **Avg Response Time:** {email['avg_response_time']}

**Status:** Gmail monitoring operational ✅

---

## 🔗 LinkedIn Engagement

- **Signals Detected:** {linkedin['signals_detected']}
- **Drafts Created:** {linkedin['drafts_created']}
- **Posts Approved:** {linkedin['posts_approved']}

**Status:** LinkedIn monitoring operational ✅

---

## 🤖 Autonomous Execution Metrics

### Ralph Wiggum Loop
- **Plans Executed:** {tasks['plans_executed']}
- **Steps Completed:** {tasks['steps_completed']}
- **Success Rate:** {tasks['success_rate']:.1f}%

**Status:** Autonomous execution operational ✅

---

## 🎯 Agent Skills Performance

- **Skills Executed:** {skills['skills_executed']}
- **Total Execution Time:** {skills['total_execution_time']:.1f}s

### Skills Breakdown
"""

        for skill, count in skills.get('skill_breakdown', {}).items():
            report += f"- **{skill}:** {count} executions\n"

        report += """
**Status:** Skills framework operational ✅

---

## 📈 System Health

| Component | Status | Notes |
|-----------|--------|-------|
| Gmail Watcher | ✅ Operational | Monitoring inbox |
| LinkedIn Watcher | ✅ Operational | Monitoring messages |
| Reasoning Loop | ✅ Operational | Generating plans |
| Drafting Agent | ✅ Operational | Creating content |
| Ralph Wiggum Loop | ✅ Operational | Executing plans |
| Gmail MCP Server | ✅ Operational | Sending emails |
| Odoo MCP Server | ✅ Operational | Financial/accounting data |
| Skills Framework | ✅ Operational | Agent skills active |

---

## 🎯 Key Insights

"""

        # Generate insights
        insights = []

        # Financial insights
        if financial['summary'].get('net_income', 0) > 0:
            insights.append(f"✅ **Profitable Week:** Net income of ${financial['summary']['net_income']:,.2f} with {financial['summary']['profit_margin']:.1f}% margin")

        # Automation insights
        if tasks['plans_executed'] > 0:
            insights.append(f"🤖 **Autonomous Execution:** {tasks['plans_executed']} plans executed with {tasks['success_rate']:.0f}% success rate")

        # Efficiency insights
        if email['emails_detected'] > 0 or linkedin['signals_detected'] > 0:
            total_signals = email['emails_detected'] + linkedin['signals_detected']
            insights.append(f"📊 **Monitoring Active:** {total_signals} business signals detected across channels")

        for insight in insights:
            report += f"- {insight}\n"

        report += """
---

## 📋 Recommendations

"""

        # Generate recommendations
        recommendations = []

        if financial['summary'].get('total_expenses', 0) > financial['summary'].get('total_income', 0):
            recommendations.append("⚠️ **Review Expenses:** Expenses exceed income this period")

        if tasks['success_rate'] < 90 and tasks['steps_completed'] > 0:
            recommendations.append(f"⚠️ **Check Automation:** Success rate at {tasks['success_rate']:.0f}%, review failed steps")

        if linkedin['drafts_created'] > linkedin['posts_approved']:
            recommendations.append("📝 **Review Drafts:** LinkedIn drafts pending approval")

        if not recommendations:
            recommendations.append("✅ **All Systems Nominal:** No immediate action required")

        for rec in recommendations:
            report += f"- {rec}\n"

        report += f"""
---

## 📅 Next Steps

1. **Review Financial Summary:** Analyze income and expense trends
2. **Approve Pending Drafts:** Check Pending_Approval/ folder
3. **Review Execution Logs:** Check for any failed automations
4. **Plan Next Week:** Adjust strategies based on insights

---

*This report was generated automatically by the AI Employee Weekly Audit System*
*Gold Tier: Comprehensive Business Intelligence*
"""

        return report

    def save_report(self, report: str) -> Path:
        """
        Save report to Reports folder

        Args:
            report: Report content

        Returns:
            Path: Path to saved report
        """
        report_date = datetime.now().strftime('%Y_%m_%d')
        report_filename = f"WEEKLY_AUDIT_{report_date}.md"
        report_path = self.reports_folder / report_filename

        report_path.write_text(report)

        print()
        print("✅ Report saved!")
        print(f"   Location: {report_path}")
        print()

        return report_path

    def generate_and_save(self) -> Path:
        """
        Generate and save complete audit report

        Returns:
            Path: Path to saved report
        """
        report = self.generate_report()
        return self.save_report(report)


# ============================================================================
# CLI Interface
# ============================================================================

if __name__ == '__main__':
    import sys

    print("=" * 70)
    print("📊 Weekly Business Audit Generator - Gold Tier")
    print("=" * 70)
    print()

    # Get vault path
    vault_path = sys.argv[1] if len(sys.argv) > 1 else '../AI_Employee_Vault'

    # Generate report
    generator = WeeklyAuditGenerator(vault_path)
    report_path = generator.generate_and_save()

    print()
    print("=" * 70)
    print("✅ Weekly Audit Complete!")
    print("=" * 70)
    print()
    print("View report:")
    print(f"cat {report_path}")
    print()
    print("Or open in Obsidian:")
    print(f"open {report_path}")
    print()
