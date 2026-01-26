#!/usr/bin/env python3
"""
Odoo MCP Server - Financial Operations via Odoo Community JSON-RPC API

This MCP server provides financial tools for the AI Employee:
- Get invoices and payments
- Create invoices
- Get financial summaries
- Manage customers/partners

Supports two modes:
- sandbox: Simulated data for testing (default)
- production: Real Odoo instance connection

Odoo External API Reference:
https://www.odoo.com/documentation/19.0/developer/reference/external_api.html
"""

import json
import logging
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional
import random

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OdooMCPServer:
    """
    MCP Server for Odoo Community financial operations.

    Uses JSON-RPC 2.0 protocol for Odoo 19+ compatibility.
    """

    def __init__(self, mode: str = "sandbox", config: Optional[Dict] = None):
        """
        Initialize Odoo MCP Server.

        Args:
            mode: 'sandbox' for testing, 'production' for real Odoo
            config: Odoo connection config (url, db, username, password)
        """
        self.mode = mode
        self.config = config or {}

        # Production connection details
        self.url = self.config.get('url', os.getenv('ODOO_URL', 'http://localhost:8069'))
        self.db = self.config.get('db', os.getenv('ODOO_DB', 'odoo'))
        self.username = self.config.get('username', os.getenv('ODOO_USERNAME', 'admin'))
        self.password = self.config.get('password', os.getenv('ODOO_PASSWORD', ''))

        self.uid = None  # User ID after authentication

        # Sandbox data for testing
        if self.mode == "sandbox":
            self._init_sandbox_data()

        logger.info(f"Odoo MCP Server initialized in {mode} mode")

    def _init_sandbox_data(self):
        """Initialize simulated data for sandbox mode."""

        # Simulated customers/partners
        self.partners = [
            {'id': 1, 'name': 'Client Alpha Corp', 'email': 'billing@alphacorp.com', 'phone': '+1-555-0101'},
            {'id': 2, 'name': 'Beta Industries', 'email': 'accounts@beta.io', 'phone': '+1-555-0102'},
            {'id': 3, 'name': 'Gamma Solutions', 'email': 'finance@gamma.com', 'phone': '+1-555-0103'},
            {'id': 4, 'name': 'Delta Services', 'email': 'pay@deltaserv.net', 'phone': '+1-555-0104'},
            {'id': 5, 'name': 'Epsilon Tech', 'email': 'ar@epsilon.tech', 'phone': '+1-555-0105'},
        ]

        # Simulated invoices
        self.invoices = [
            {
                'id': 1001,
                'name': 'INV/2026/0001',
                'partner_id': 1,
                'partner_name': 'Client Alpha Corp',
                'invoice_date': '2026-01-05',
                'due_date': '2026-02-05',
                'amount_total': 2500.00,
                'amount_residual': 0.00,
                'state': 'paid',
                'payment_state': 'paid'
            },
            {
                'id': 1002,
                'name': 'INV/2026/0002',
                'partner_id': 2,
                'partner_name': 'Beta Industries',
                'invoice_date': '2026-01-08',
                'due_date': '2026-02-08',
                'amount_total': 4750.00,
                'amount_residual': 4750.00,
                'state': 'posted',
                'payment_state': 'not_paid'
            },
            {
                'id': 1003,
                'name': 'INV/2026/0003',
                'partner_id': 3,
                'partner_name': 'Gamma Solutions',
                'invoice_date': '2026-01-10',
                'due_date': '2026-02-10',
                'amount_total': 1200.00,
                'amount_residual': 600.00,
                'state': 'posted',
                'payment_state': 'partial'
            },
            {
                'id': 1004,
                'name': 'INV/2026/0004',
                'partner_id': 4,
                'partner_name': 'Delta Services',
                'invoice_date': '2026-01-12',
                'due_date': '2026-02-12',
                'amount_total': 3200.00,
                'amount_residual': 3200.00,
                'state': 'posted',
                'payment_state': 'not_paid'
            },
            {
                'id': 1005,
                'name': 'INV/2026/0005',
                'partner_id': 5,
                'partner_name': 'Epsilon Tech',
                'invoice_date': '2026-01-14',
                'due_date': '2026-02-14',
                'amount_total': 5500.00,
                'amount_residual': 5500.00,
                'state': 'draft',
                'payment_state': 'not_paid'
            },
        ]

        # Simulated payments
        self.payments = [
            {
                'id': 2001,
                'name': 'PAY/2026/0001',
                'partner_id': 1,
                'partner_name': 'Client Alpha Corp',
                'payment_date': '2026-01-10',
                'amount': 2500.00,
                'payment_type': 'inbound',
                'state': 'posted',
                'ref': 'INV/2026/0001'
            },
            {
                'id': 2002,
                'name': 'PAY/2026/0002',
                'partner_id': 3,
                'partner_name': 'Gamma Solutions',
                'payment_date': '2026-01-12',
                'amount': 600.00,
                'payment_type': 'inbound',
                'state': 'posted',
                'ref': 'INV/2026/0003 - Partial'
            },
        ]

        # Simulated expenses (vendor bills)
        self.expenses = [
            {
                'id': 3001,
                'name': 'BILL/2026/0001',
                'partner_name': 'Office Supplies Inc',
                'invoice_date': '2026-01-03',
                'amount_total': 250.00,
                'state': 'paid',
                'category': 'Office Supplies'
            },
            {
                'id': 3002,
                'name': 'BILL/2026/0002',
                'partner_name': 'Cloud Hosting Co',
                'invoice_date': '2026-01-05',
                'amount_total': 150.00,
                'state': 'paid',
                'category': 'Software & Hosting'
            },
            {
                'id': 3003,
                'name': 'BILL/2026/0003',
                'partner_name': 'Marketing Agency',
                'invoice_date': '2026-01-10',
                'amount_total': 800.00,
                'state': 'posted',
                'category': 'Marketing'
            },
        ]

        # Account balances
        self.accounts = [
            {'id': 1, 'name': 'Bank Account', 'code': '1010', 'balance': 18500.00, 'type': 'asset'},
            {'id': 2, 'name': 'Cash', 'code': '1020', 'balance': 1200.00, 'type': 'asset'},
            {'id': 3, 'name': 'Accounts Receivable', 'code': '1200', 'balance': 14050.00, 'type': 'asset'},
            {'id': 4, 'name': 'Accounts Payable', 'code': '2100', 'balance': -800.00, 'type': 'liability'},
        ]

    def _json_rpc_call(self, endpoint: str, method: str, params: List) -> Any:
        """
        Make JSON-RPC 2.0 call to Odoo server.

        For production mode only.
        """
        if self.mode == "sandbox":
            raise RuntimeError("JSON-RPC calls not available in sandbox mode")

        try:
            import requests
        except ImportError:
            raise ImportError("requests library required for production mode: pip install requests")

        url = f"{self.url}{endpoint}"
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": random.randint(1, 1000000)
        }

        response = requests.post(url, json=payload, headers={'Content-Type': 'application/json'})
        response.raise_for_status()

        result = response.json()
        if 'error' in result:
            raise Exception(f"Odoo Error: {result['error']}")

        return result.get('result')

    def authenticate(self) -> Dict[str, Any]:
        """
        Authenticate with Odoo server.

        Returns:
            Authentication result with user ID
        """
        if self.mode == "sandbox":
            self.uid = 1
            return {
                'success': True,
                'uid': 1,
                'username': 'demo_user',
                'message': 'Sandbox authentication successful'
            }

        # Production authentication via common endpoint
        try:
            self.uid = self._json_rpc_call(
                '/jsonrpc',
                'call',
                {
                    'service': 'common',
                    'method': 'authenticate',
                    'args': [self.db, self.username, self.password, {}]
                }
            )

            if self.uid:
                return {
                    'success': True,
                    'uid': self.uid,
                    'username': self.username,
                    'message': 'Authentication successful'
                }
            else:
                return {
                    'success': False,
                    'message': 'Authentication failed - invalid credentials'
                }
        except Exception as e:
            return {
                'success': False,
                'message': f'Authentication error: {str(e)}'
            }

    def get_invoices(self, state: str = None, limit: int = 10) -> Dict[str, Any]:
        """
        Get customer invoices from Odoo.

        Args:
            state: Filter by state ('draft', 'posted', 'paid', 'cancel')
            limit: Maximum number of invoices to return

        Returns:
            List of invoices with details
        """
        if self.mode == "sandbox":
            invoices = self.invoices
            if state:
                if state == 'paid':
                    invoices = [i for i in invoices if i['payment_state'] == 'paid']
                elif state == 'unpaid':
                    invoices = [i for i in invoices if i['payment_state'] in ('not_paid', 'partial')]
                else:
                    invoices = [i for i in invoices if i['state'] == state]

            return {
                'success': True,
                'invoices': invoices[:limit],
                'total_count': len(invoices),
                'mode': 'sandbox'
            }

        # Production: call Odoo API
        try:
            domain = [('move_type', '=', 'out_invoice')]
            if state:
                if state == 'unpaid':
                    domain.append(('payment_state', 'in', ['not_paid', 'partial']))
                elif state == 'paid':
                    domain.append(('payment_state', '=', 'paid'))
                else:
                    domain.append(('state', '=', state))

            result = self._json_rpc_call(
                '/jsonrpc',
                'call',
                {
                    'service': 'object',
                    'method': 'execute_kw',
                    'args': [
                        self.db, self.uid, self.password,
                        'account.move', 'search_read',
                        [domain],
                        {'fields': ['name', 'partner_id', 'invoice_date', 'amount_total',
                                   'amount_residual', 'state', 'payment_state'],
                         'limit': limit}
                    ]
                }
            )

            return {
                'success': True,
                'invoices': result,
                'total_count': len(result),
                'mode': 'production'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def create_invoice(self, partner_id: int, lines: List[Dict],
                       invoice_date: str = None) -> Dict[str, Any]:
        """
        Create a new customer invoice in Odoo.

        Args:
            partner_id: Customer/Partner ID
            lines: List of invoice lines [{'product': str, 'quantity': float, 'price': float}]
            invoice_date: Invoice date (YYYY-MM-DD), defaults to today

        Returns:
            Created invoice details
        """
        if not invoice_date:
            invoice_date = datetime.now().strftime('%Y-%m-%d')

        if self.mode == "sandbox":
            # Generate new invoice in sandbox
            new_id = max(i['id'] for i in self.invoices) + 1
            invoice_num = f"INV/2026/{new_id - 1000:04d}"

            # Find partner
            partner = next((p for p in self.partners if p['id'] == partner_id), None)
            if not partner:
                return {
                    'success': False,
                    'error': f'Partner ID {partner_id} not found'
                }

            # Calculate total
            total = sum(line.get('quantity', 1) * line.get('price', 0) for line in lines)

            # Due date = invoice date + 30 days
            inv_date = datetime.strptime(invoice_date, '%Y-%m-%d')
            due_date = (inv_date + timedelta(days=30)).strftime('%Y-%m-%d')

            new_invoice = {
                'id': new_id,
                'name': invoice_num,
                'partner_id': partner_id,
                'partner_name': partner['name'],
                'invoice_date': invoice_date,
                'due_date': due_date,
                'amount_total': total,
                'amount_residual': total,
                'state': 'draft',
                'payment_state': 'not_paid',
                'lines': lines
            }

            self.invoices.append(new_invoice)

            return {
                'success': True,
                'invoice': new_invoice,
                'message': f'Invoice {invoice_num} created successfully',
                'mode': 'sandbox'
            }

        # Production: create invoice via Odoo API
        try:
            # Prepare invoice lines for Odoo
            invoice_lines = []
            for line in lines:
                invoice_lines.append((0, 0, {
                    'name': line.get('product', 'Service'),
                    'quantity': line.get('quantity', 1),
                    'price_unit': line.get('price', 0),
                }))

            invoice_id = self._json_rpc_call(
                '/jsonrpc',
                'call',
                {
                    'service': 'object',
                    'method': 'execute_kw',
                    'args': [
                        self.db, self.uid, self.password,
                        'account.move', 'create',
                        [{
                            'move_type': 'out_invoice',
                            'partner_id': partner_id,
                            'invoice_date': invoice_date,
                            'invoice_line_ids': invoice_lines,
                        }]
                    ]
                }
            )

            return {
                'success': True,
                'invoice_id': invoice_id,
                'message': f'Invoice created with ID {invoice_id}',
                'mode': 'production'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def get_payments(self, days: int = 30) -> Dict[str, Any]:
        """
        Get recent payments from Odoo.

        Args:
            days: Number of days to look back

        Returns:
            List of payments with details
        """
        if self.mode == "sandbox":
            # Filter payments by date
            cutoff = datetime.now() - timedelta(days=days)
            cutoff_str = cutoff.strftime('%Y-%m-%d')

            recent_payments = [
                p for p in self.payments
                if p['payment_date'] >= cutoff_str
            ]

            total_received = sum(p['amount'] for p in recent_payments if p['payment_type'] == 'inbound')

            return {
                'success': True,
                'payments': recent_payments,
                'total_received': total_received,
                'period_days': days,
                'mode': 'sandbox'
            }

        # Production: query Odoo
        try:
            cutoff = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

            result = self._json_rpc_call(
                '/jsonrpc',
                'call',
                {
                    'service': 'object',
                    'method': 'execute_kw',
                    'args': [
                        self.db, self.uid, self.password,
                        'account.payment', 'search_read',
                        [[('payment_date', '>=', cutoff), ('state', '=', 'posted')]],
                        {'fields': ['name', 'partner_id', 'payment_date', 'amount',
                                   'payment_type', 'state', 'ref']}
                    ]
                }
            )

            total_received = sum(p['amount'] for p in result if p['payment_type'] == 'inbound')

            return {
                'success': True,
                'payments': result,
                'total_received': total_received,
                'period_days': days,
                'mode': 'production'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def get_account_balances(self) -> Dict[str, Any]:
        """
        Get account balances from Odoo.

        Returns:
            Account balances and totals
        """
        if self.mode == "sandbox":
            assets = sum(a['balance'] for a in self.accounts if a['type'] == 'asset')
            liabilities = abs(sum(a['balance'] for a in self.accounts if a['type'] == 'liability'))

            return {
                'success': True,
                'accounts': self.accounts,
                'total_assets': assets,
                'total_liabilities': liabilities,
                'net_position': assets - liabilities,
                'mode': 'sandbox'
            }

        # Production: query Odoo account balances
        try:
            result = self._json_rpc_call(
                '/jsonrpc',
                'call',
                {
                    'service': 'object',
                    'method': 'execute_kw',
                    'args': [
                        self.db, self.uid, self.password,
                        'account.account', 'search_read',
                        [[('account_type', 'in', ['asset_current', 'liability_current'])]],
                        {'fields': ['name', 'code', 'current_balance', 'account_type']}
                    ]
                }
            )

            return {
                'success': True,
                'accounts': result,
                'mode': 'production'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def get_financial_summary(self, period: str = 'month') -> Dict[str, Any]:
        """
        Get comprehensive financial summary.

        Args:
            period: 'week', 'month', or 'quarter'

        Returns:
            Financial summary with key metrics
        """
        days = {'week': 7, 'month': 30, 'quarter': 90}.get(period, 30)

        if self.mode == "sandbox":
            # Calculate metrics from sandbox data
            total_invoiced = sum(i['amount_total'] for i in self.invoices)
            total_paid = sum(i['amount_total'] - i['amount_residual'] for i in self.invoices)
            total_outstanding = sum(i['amount_residual'] for i in self.invoices if i['state'] != 'draft')
            total_draft = sum(i['amount_total'] for i in self.invoices if i['state'] == 'draft')

            total_expenses = sum(e['amount_total'] for e in self.expenses)
            pending_expenses = sum(e['amount_total'] for e in self.expenses if e['state'] == 'posted')

            # Get account balances
            balances = self.get_account_balances()

            revenue = total_paid
            expenses_paid = sum(e['amount_total'] for e in self.expenses if e['state'] == 'paid')
            profit = revenue - expenses_paid
            profit_margin = (profit / revenue * 100) if revenue > 0 else 0

            return {
                'success': True,
                'period': period,
                'generated_at': datetime.now().isoformat(),
                'revenue': {
                    'total_invoiced': total_invoiced,
                    'total_received': total_paid,
                    'outstanding': total_outstanding,
                    'draft_invoices': total_draft
                },
                'expenses': {
                    'total': total_expenses,
                    'paid': expenses_paid,
                    'pending': pending_expenses
                },
                'profitability': {
                    'gross_profit': profit,
                    'profit_margin_percent': round(profit_margin, 1)
                },
                'balances': {
                    'total_assets': balances['total_assets'],
                    'total_liabilities': balances['total_liabilities'],
                    'net_position': balances['net_position']
                },
                'invoices': {
                    'total_count': len(self.invoices),
                    'paid_count': len([i for i in self.invoices if i['payment_state'] == 'paid']),
                    'unpaid_count': len([i for i in self.invoices if i['payment_state'] in ('not_paid', 'partial')])
                },
                'mode': 'sandbox'
            }

        # Production: aggregate data from Odoo
        try:
            invoices = self.get_invoices(limit=100)
            payments = self.get_payments(days=days)
            balances = self.get_account_balances()

            # Calculate summary from real data
            return {
                'success': True,
                'period': period,
                'generated_at': datetime.now().isoformat(),
                'revenue': {
                    'total_received': payments.get('total_received', 0),
                    'invoice_count': invoices.get('total_count', 0)
                },
                'balances': balances,
                'mode': 'production'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def get_partners(self, is_customer: bool = True) -> Dict[str, Any]:
        """
        Get customers/partners from Odoo.

        Args:
            is_customer: Filter for customers only

        Returns:
            List of partners
        """
        if self.mode == "sandbox":
            return {
                'success': True,
                'partners': self.partners,
                'total_count': len(self.partners),
                'mode': 'sandbox'
            }

        try:
            domain = []
            if is_customer:
                domain.append(('customer_rank', '>', 0))

            result = self._json_rpc_call(
                '/jsonrpc',
                'call',
                {
                    'service': 'object',
                    'method': 'execute_kw',
                    'args': [
                        self.db, self.uid, self.password,
                        'res.partner', 'search_read',
                        [domain],
                        {'fields': ['name', 'email', 'phone', 'customer_rank']}
                    ]
                }
            )

            return {
                'success': True,
                'partners': result,
                'total_count': len(result),
                'mode': 'production'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def create_partner(self, name: str, email: str = None, phone: str = None) -> Dict[str, Any]:
        """
        Create a new customer/partner in Odoo.

        Args:
            name: Partner name
            email: Partner email
            phone: Partner phone

        Returns:
            Created partner details
        """
        if self.mode == "sandbox":
            new_id = max(p['id'] for p in self.partners) + 1 if self.partners else 1
            new_partner = {
                'id': new_id,
                'name': name,
                'email': email or f"{name.lower().replace(' ', '_')}@example.com",
                'phone': phone or 'N/A'
            }
            self.partners.append(new_partner)
            return {
                'success': True,
                'partner': new_partner,
                'message': f'Customer {name} created successfully',
                'mode': 'sandbox'
            }

        # Production: create partner via Odoo API
        try:
            partner_id = self._json_rpc_call(
                '/jsonrpc',
                'call',
                {
                    'service': 'object',
                    'method': 'execute_kw',
                    'args': [
                        self.db, self.uid, self.password,
                        'res.partner', 'create',
                        [{
                            'name': name,
                            'email': email,
                            'phone': phone,
                            'customer_rank': 1,
                        }]
                    ]
                }
            )

            return {
                'success': True,
                'partner_id': partner_id,
                'partner': {'id': partner_id, 'name': name, 'email': email, 'phone': phone},
                'message': f'Customer {name} created with ID {partner_id}',
                'mode': 'production'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def get_tools_definition(self) -> List[Dict]:
        """
        Get MCP tools definition for Claude Code integration.

        Returns:
            List of tool definitions in MCP format
        """
        return [
            {
                'name': 'odoo_get_invoices',
                'description': 'Get customer invoices from Odoo. Filter by state: draft, posted, paid, unpaid',
                'input_schema': {
                    'type': 'object',
                    'properties': {
                        'state': {'type': 'string', 'enum': ['draft', 'posted', 'paid', 'unpaid']},
                        'limit': {'type': 'integer', 'default': 10}
                    }
                }
            },
            {
                'name': 'odoo_create_invoice',
                'description': 'Create a new customer invoice in Odoo',
                'input_schema': {
                    'type': 'object',
                    'properties': {
                        'partner_id': {'type': 'integer', 'description': 'Customer ID'},
                        'lines': {
                            'type': 'array',
                            'items': {
                                'type': 'object',
                                'properties': {
                                    'product': {'type': 'string'},
                                    'quantity': {'type': 'number'},
                                    'price': {'type': 'number'}
                                }
                            }
                        },
                        'invoice_date': {'type': 'string', 'format': 'date'}
                    },
                    'required': ['partner_id', 'lines']
                }
            },
            {
                'name': 'odoo_get_payments',
                'description': 'Get recent payments received',
                'input_schema': {
                    'type': 'object',
                    'properties': {
                        'days': {'type': 'integer', 'default': 30}
                    }
                }
            },
            {
                'name': 'odoo_get_balances',
                'description': 'Get account balances and financial position',
                'input_schema': {
                    'type': 'object',
                    'properties': {}
                }
            },
            {
                'name': 'odoo_get_summary',
                'description': 'Get comprehensive financial summary for CEO briefing',
                'input_schema': {
                    'type': 'object',
                    'properties': {
                        'period': {'type': 'string', 'enum': ['week', 'month', 'quarter'], 'default': 'month'}
                    }
                }
            },
            {
                'name': 'odoo_get_partners',
                'description': 'Get list of customers/partners',
                'input_schema': {
                    'type': 'object',
                    'properties': {
                        'is_customer': {'type': 'boolean', 'default': True}
                    }
                }
            }
        ]

    def execute_tool(self, tool_name: str, params: Dict) -> Dict[str, Any]:
        """
        Execute an MCP tool by name.

        Args:
            tool_name: Name of the tool to execute
            params: Tool parameters

        Returns:
            Tool execution result
        """
        tool_map = {
            'odoo_get_invoices': lambda p: self.get_invoices(
                state=p.get('state'),
                limit=p.get('limit', 10)
            ),
            'odoo_create_invoice': lambda p: self.create_invoice(
                partner_id=p['partner_id'],
                lines=p['lines'],
                invoice_date=p.get('invoice_date')
            ),
            'odoo_get_payments': lambda p: self.get_payments(
                days=p.get('days', 30)
            ),
            'odoo_get_balances': lambda p: self.get_account_balances(),
            'odoo_get_summary': lambda p: self.get_financial_summary(
                period=p.get('period', 'month')
            ),
            'odoo_get_partners': lambda p: self.get_partners(
                is_customer=p.get('is_customer', True)
            )
        }

        if tool_name not in tool_map:
            return {
                'success': False,
                'error': f'Unknown tool: {tool_name}'
            }

        return tool_map[tool_name](params)


def main():
    """CLI interface for testing Odoo MCP Server."""
    import sys

    server = OdooMCPServer(mode='sandbox')

    if len(sys.argv) < 2:
        print("Odoo MCP Server - Sandbox Mode")
        print("\nUsage: python odoo_mcp_server.py <command>")
        print("\nCommands:")
        print("  invoices       - List all invoices")
        print("  unpaid         - List unpaid invoices")
        print("  payments       - List recent payments")
        print("  balances       - Show account balances")
        print("  summary        - Financial summary")
        print("  partners       - List customers")
        print("  create         - Create test invoice")
        print("  tools          - Show MCP tools definition")
        return

    command = sys.argv[1].lower()

    if command == 'invoices':
        result = server.get_invoices()
        print("\n📋 Invoices:")
        for inv in result['invoices']:
            status = '✅' if inv['payment_state'] == 'paid' else '⏳'
            print(f"  {status} {inv['name']} | {inv['partner_name']} | ${inv['amount_total']:,.2f} | {inv['state']}")

    elif command == 'unpaid':
        result = server.get_invoices(state='unpaid')
        print("\n⏳ Unpaid Invoices:")
        total = 0
        for inv in result['invoices']:
            print(f"  • {inv['name']} | {inv['partner_name']} | Outstanding: ${inv['amount_residual']:,.2f}")
            total += inv['amount_residual']
        print(f"\n  Total Outstanding: ${total:,.2f}")

    elif command == 'payments':
        result = server.get_payments(days=30)
        print("\n💰 Recent Payments (Last 30 Days):")
        for pay in result['payments']:
            print(f"  • {pay['name']} | {pay['partner_name']} | ${pay['amount']:,.2f} | {pay['payment_date']}")
        print(f"\n  Total Received: ${result['total_received']:,.2f}")

    elif command == 'balances':
        result = server.get_account_balances()
        print("\n🏦 Account Balances:")
        for acc in result['accounts']:
            print(f"  • {acc['code']} {acc['name']}: ${acc['balance']:,.2f}")
        print(f"\n  Total Assets: ${result['total_assets']:,.2f}")
        print(f"  Total Liabilities: ${result['total_liabilities']:,.2f}")
        print(f"  Net Position: ${result['net_position']:,.2f}")

    elif command == 'summary':
        result = server.get_financial_summary(period='month')
        print("\n📊 Financial Summary (Monthly):")
        print(f"\n  Revenue:")
        print(f"    Total Invoiced: ${result['revenue']['total_invoiced']:,.2f}")
        print(f"    Total Received: ${result['revenue']['total_received']:,.2f}")
        print(f"    Outstanding: ${result['revenue']['outstanding']:,.2f}")
        print(f"\n  Expenses:")
        print(f"    Total: ${result['expenses']['total']:,.2f}")
        print(f"    Paid: ${result['expenses']['paid']:,.2f}")
        print(f"\n  Profitability:")
        print(f"    Gross Profit: ${result['profitability']['gross_profit']:,.2f}")
        print(f"    Margin: {result['profitability']['profit_margin_percent']}%")
        print(f"\n  Net Position: ${result['balances']['net_position']:,.2f}")

    elif command == 'partners':
        result = server.get_partners()
        print("\n👥 Customers:")
        for p in result['partners']:
            print(f"  • [{p['id']}] {p['name']} | {p['email']}")

    elif command == 'create':
        result = server.create_invoice(
            partner_id=2,
            lines=[
                {'product': 'Consulting Services', 'quantity': 10, 'price': 150.00},
                {'product': 'Development Work', 'quantity': 20, 'price': 100.00}
            ]
        )
        if result['success']:
            print(f"\n✅ {result['message']}")
            inv = result['invoice']
            print(f"   Invoice: {inv['name']}")
            print(f"   Customer: {inv['partner_name']}")
            print(f"   Total: ${inv['amount_total']:,.2f}")
        else:
            print(f"\n❌ Error: {result['error']}")

    elif command == 'tools':
        tools = server.get_tools_definition()
        print("\n🔧 MCP Tools Definition:")
        for tool in tools:
            print(f"\n  {tool['name']}")
            print(f"    {tool['description']}")

    else:
        print(f"Unknown command: {command}")
        print("Run without arguments to see available commands.")


if __name__ == '__main__':
    main()
