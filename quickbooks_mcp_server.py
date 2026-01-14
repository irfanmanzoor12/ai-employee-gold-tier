#!/usr/bin/env python3
"""
QuickBooks MCP Server - Model Context Protocol Server for QuickBooks
Gold Tier Requirement: Accounting integration with MCP server

Provides financial data access and basic accounting operations.
Uses QuickBooks Online Sandbox (FREE) for development/demo.
"""
import os
import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta


class QuickBooksMCPServer:
    """
    MCP Server for QuickBooks operations

    For demo purposes, this uses simulated data.
    In production, this would connect to QuickBooks Online API.

    To connect to real QuickBooks Online API:
    1. Create app at https://developer.intuit.com/
    2. Get OAuth credentials
    3. Use intuit-oauth library for authentication
    4. Replace simulate_* methods with real API calls
    """

    def __init__(self, mode: str = "sandbox"):
        """
        Initialize QuickBooks MCP Server

        Args:
            mode: "sandbox" (simulated data) or "production" (real API)
        """
        self.mode = mode
        self.connected = False

        if mode == "sandbox":
            self._init_sandbox()
        else:
            self._init_production()

    def _init_sandbox(self):
        """Initialize sandbox mode with simulated data"""
        print("✅ QuickBooks MCP Server (Sandbox Mode)")
        print("   Using simulated financial data for demo")

        # Simulated company data
        self.company_info = {
            'company_name': 'AI Employee Demo Company',
            'currency': 'USD',
            'fiscal_year_start': 'January'
        }

        # Simulated accounts
        self.accounts = [
            {'id': '1', 'name': 'Business Checking', 'type': 'Bank', 'balance': 15420.50},
            {'id': '2', 'name': 'Savings', 'type': 'Bank', 'balance': 25000.00},
            {'id': '3', 'name': 'Accounts Receivable', 'type': 'Accounts Receivable', 'balance': 8500.00},
            {'id': '4', 'name': 'Revenue', 'type': 'Income', 'balance': 45000.00},
            {'id': '5', 'name': 'Operating Expenses', 'type': 'Expense', 'balance': 12340.75},
        ]

        # Simulated transactions (last 30 days)
        self.transactions = [
            {
                'id': 'txn_001',
                'date': (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d'),
                'description': 'Client Payment - ABC Corp',
                'amount': 2500.00,
                'type': 'Income',
                'category': 'Revenue'
            },
            {
                'id': 'txn_002',
                'date': (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d'),
                'description': 'Office Supplies - Staples',
                'amount': -145.30,
                'type': 'Expense',
                'category': 'Operating Expenses'
            },
            {
                'id': 'txn_003',
                'date': (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
                'description': 'Software Subscription - OpenAI',
                'amount': -20.00,
                'type': 'Expense',
                'category': 'Operating Expenses'
            },
            {
                'id': 'txn_004',
                'date': (datetime.now() - timedelta(days=10)).strftime('%Y-%m-%d'),
                'description': 'Client Payment - XYZ Inc',
                'amount': 3500.00,
                'type': 'Income',
                'category': 'Revenue'
            },
        ]

        self.connected = True

    def _init_production(self):
        """Initialize production mode with real QuickBooks API"""
        # This would use intuit-oauth library
        # For now, raise error since we're using sandbox
        raise NotImplementedError(
            "Production mode requires QuickBooks Online API credentials. "
            "Use mode='sandbox' for demo purposes."
        )

    def get_account_balances(self) -> Dict[str, Any]:
        """
        Get current account balances

        Returns:
            dict: Account balances with success status
        """
        if not self.connected:
            return {'success': False, 'error': 'Not connected to QuickBooks'}

        return {
            'success': True,
            'company': self.company_info['company_name'],
            'as_of': datetime.now().strftime('%Y-%m-%d'),
            'accounts': self.accounts,
            'total_assets': sum(a['balance'] for a in self.accounts if a['type'] in ['Bank', 'Accounts Receivable']),
            'total_revenue': sum(a['balance'] for a in self.accounts if a['type'] == 'Income'),
            'total_expenses': sum(a['balance'] for a in self.accounts if a['type'] == 'Expense')
        }

    def get_recent_transactions(self, days: int = 30, limit: int = 50) -> Dict[str, Any]:
        """
        Get recent transactions

        Args:
            days: Number of days to look back
            limit: Maximum number of transactions

        Returns:
            dict: Transactions with success status
        """
        if not self.connected:
            return {'success': False, 'error': 'Not connected to QuickBooks'}

        # In sandbox mode, return simulated transactions
        return {
            'success': True,
            'period': f'Last {days} days',
            'count': len(self.transactions),
            'transactions': self.transactions[:limit]
        }

    def create_expense(self, description: str, amount: float,
                      category: str = 'Operating Expenses') -> Dict[str, Any]:
        """
        Create an expense entry

        Args:
            description: Expense description
            amount: Expense amount (positive number)
            category: Expense category

        Returns:
            dict: Created expense with success status
        """
        if not self.connected:
            return {'success': False, 'error': 'Not connected to QuickBooks'}

        # In sandbox mode, simulate expense creation
        expense = {
            'id': f'txn_{len(self.transactions) + 1:03d}',
            'date': datetime.now().strftime('%Y-%m-%d'),
            'description': description,
            'amount': -abs(amount),  # Expenses are negative
            'type': 'Expense',
            'category': category
        }

        self.transactions.insert(0, expense)

        return {
            'success': True,
            'expense': expense,
            'message': f'Expense created: {description} for ${amount:.2f}'
        }

    def get_financial_summary(self, period: str = 'month') -> Dict[str, Any]:
        """
        Get financial summary for a period

        Args:
            period: 'week', 'month', or 'year'

        Returns:
            dict: Financial summary with success status
        """
        if not self.connected:
            return {'success': False, 'error': 'Not connected to QuickBooks'}

        # Calculate totals from transactions
        income = sum(t['amount'] for t in self.transactions if t['amount'] > 0)
        expenses = sum(abs(t['amount']) for t in self.transactions if t['amount'] < 0)
        net_income = income - expenses

        return {
            'success': True,
            'period': period,
            'as_of': datetime.now().strftime('%Y-%m-%d'),
            'summary': {
                'total_income': income,
                'total_expenses': expenses,
                'net_income': net_income,
                'profit_margin': (net_income / income * 100) if income > 0 else 0
            },
            'accounts': self.get_account_balances()['accounts']
        }

    def get_tools_definition(self) -> List[Dict]:
        """
        Return MCP tools definition for this server
        Used by AI systems to understand available capabilities
        """
        return [
            {
                'name': 'get_account_balances',
                'description': 'Get current balances for all accounts',
                'input_schema': {
                    'type': 'object',
                    'properties': {},
                    'required': []
                }
            },
            {
                'name': 'get_recent_transactions',
                'description': 'Get recent transactions from QuickBooks',
                'input_schema': {
                    'type': 'object',
                    'properties': {
                        'days': {
                            'type': 'number',
                            'description': 'Number of days to look back (default: 30)'
                        },
                        'limit': {
                            'type': 'number',
                            'description': 'Maximum transactions to return (default: 50)'
                        }
                    },
                    'required': []
                }
            },
            {
                'name': 'create_expense',
                'description': 'Create a new expense entry in QuickBooks',
                'input_schema': {
                    'type': 'object',
                    'properties': {
                        'description': {
                            'type': 'string',
                            'description': 'Expense description'
                        },
                        'amount': {
                            'type': 'number',
                            'description': 'Expense amount (positive number)'
                        },
                        'category': {
                            'type': 'string',
                            'description': 'Expense category (default: Operating Expenses)'
                        }
                    },
                    'required': ['description', 'amount']
                }
            },
            {
                'name': 'get_financial_summary',
                'description': 'Get financial summary for a period',
                'input_schema': {
                    'type': 'object',
                    'properties': {
                        'period': {
                            'type': 'string',
                            'description': 'Period: week, month, or year (default: month)'
                        }
                    },
                    'required': []
                }
            }
        ]

    def handle_tool_call(self, tool_name: str, arguments: Dict) -> Dict:
        """
        Handle MCP tool calls
        Routes to appropriate handler based on tool_name
        """
        if tool_name == 'get_account_balances':
            return self.get_account_balances()
        elif tool_name == 'get_recent_transactions':
            return self.get_recent_transactions(**arguments)
        elif tool_name == 'create_expense':
            return self.create_expense(**arguments)
        elif tool_name == 'get_financial_summary':
            return self.get_financial_summary(**arguments)
        else:
            return {
                'success': False,
                'error': f'Unknown tool: {tool_name}'
            }


# ============================================================================
# MCP Server Interface (Standard Protocol)
# ============================================================================

def create_mcp_server():
    """Factory function to create QuickBooks MCP Server instance"""
    return QuickBooksMCPServer(mode='sandbox')


def list_tools():
    """List available tools for this MCP server"""
    server = create_mcp_server()
    return server.get_tools_definition()


def call_tool(name: str, arguments: Dict) -> Dict:
    """Call a tool by name with given arguments"""
    server = create_mcp_server()
    return server.handle_tool_call(name, arguments)


# ============================================================================
# CLI Interface for Testing
# ============================================================================

if __name__ == '__main__':
    import sys

    print("=" * 70)
    print("QuickBooks MCP Server - Gold Tier")
    print("=" * 70)
    print()

    # Test mode: list tools
    if len(sys.argv) == 1 or sys.argv[1] == 'list':
        print("Available Tools:")
        print()
        tools = list_tools()
        for tool in tools:
            print(f"💰 {tool['name']}")
            print(f"   Description: {tool['description']}")
            print()

    # Test mode: get balances
    elif sys.argv[1] == 'balances':
        print("Fetching account balances...")
        print()

        result = call_tool('get_account_balances', {})

        if result['success']:
            print(f"Company: {result['company']}")
            print(f"As of: {result['as_of']}")
            print()
            print("Accounts:")
            for account in result['accounts']:
                print(f"  {account['name']} ({account['type']}): ${account['balance']:,.2f}")
            print()
            print(f"Total Assets: ${result['total_assets']:,.2f}")
            print(f"Total Revenue: ${result['total_revenue']:,.2f}")
            print(f"Total Expenses: ${result['total_expenses']:,.2f}")
        else:
            print(f"❌ Error: {result['error']}")

    # Test mode: get transactions
    elif sys.argv[1] == 'transactions':
        print("Fetching recent transactions...")
        print()

        result = call_tool('get_recent_transactions', {'days': 30})

        if result['success']:
            print(f"Period: {result['period']}")
            print(f"Count: {result['count']}")
            print()
            print("Recent Transactions:")
            for txn in result['transactions']:
                amt_str = f"${abs(txn['amount']):,.2f}"
                if txn['amount'] > 0:
                    amt_str = "+" + amt_str
                else:
                    amt_str = "-" + amt_str
                print(f"  {txn['date']}: {txn['description']:<40} {amt_str:>12}")
        else:
            print(f"❌ Error: {result['error']}")

    # Test mode: financial summary
    elif sys.argv[1] == 'summary':
        print("Generating financial summary...")
        print()

        result = call_tool('get_financial_summary', {'period': 'month'})

        if result['success']:
            summary = result['summary']
            print(f"Period: {result['period']}")
            print(f"As of: {result['as_of']}")
            print()
            print("Financial Summary:")
            print(f"  Total Income:    ${summary['total_income']:>12,.2f}")
            print(f"  Total Expenses:  ${summary['total_expenses']:>12,.2f}")
            print(f"  ────────────────────────────────")
            print(f"  Net Income:      ${summary['net_income']:>12,.2f}")
            print(f"  Profit Margin:   {summary['profit_margin']:>11.1f}%")
        else:
            print(f"❌ Error: {result['error']}")

    else:
        print(f"Unknown command: {sys.argv[1]}")
        print()
        print("Available commands:")
        print("  list         - List available tools")
        print("  balances     - Get account balances")
        print("  transactions - Get recent transactions")
        print("  summary      - Get financial summary")
