#!/usr/bin/env python3
"""
Gmail MCP Server - Model Context Protocol Server for Gmail Actions
Allows AI systems to send emails through approved actions
GOLD TIER REQUIREMENT: External action capability via MCP
"""
import os
import json
import base64
from email.mime.text import MIMEText
from pathlib import Path
from typing import Optional

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class GmailMCPServer:
    """
    MCP Server for Gmail operations
    Implements send_email tool for AI-approved actions
    """

    def __init__(self, token_path: str = 'token.json'):
        """Initialize Gmail MCP Server"""
        self.token_path = token_path
        self.service = None
        self._authenticate()

    def _authenticate(self):
        """Authenticate with Gmail API using existing token"""
        if not os.path.exists(self.token_path):
            raise FileNotFoundError(
                f"Gmail token not found at {self.token_path}. "
                "Please run gmail_watcher.py first to authenticate."
            )

        creds = Credentials.from_authorized_user_file(self.token_path)

        # Refresh if expired
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            # Save refreshed credentials
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())

        self.service = build('gmail', 'v1', credentials=creds)
        print(f"✅ Gmail MCP Server authenticated")

    def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        from_email: Optional[str] = None
    ) -> dict:
        """
        Send an email via Gmail API

        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body (plain text)
            from_email: Sender email (optional, uses authenticated account)

        Returns:
            dict: Result with message_id or error
        """
        try:
            # Create message
            message = MIMEText(body)
            message['to'] = to
            message['subject'] = subject
            if from_email:
                message['from'] = from_email

            # Encode message
            raw_message = base64.urlsafe_b64encode(
                message.as_bytes()
            ).decode('utf-8')

            # Send via Gmail API
            send_message = {
                'raw': raw_message
            }

            result = self.service.users().messages().send(
                userId='me',
                body=send_message
            ).execute()

            message_id = result.get('id')

            return {
                'success': True,
                'message_id': message_id,
                'to': to,
                'subject': subject,
                'status': 'sent'
            }

        except HttpError as error:
            return {
                'success': False,
                'error': str(error),
                'to': to,
                'subject': subject,
                'status': 'failed'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'to': to,
                'subject': subject,
                'status': 'failed'
            }

    def get_tools_definition(self) -> list:
        """
        Return MCP tools definition for this server
        Used by AI systems to understand available capabilities
        """
        return [
            {
                'name': 'send_email',
                'description': 'Send an email via Gmail. Requires prior human approval.',
                'input_schema': {
                    'type': 'object',
                    'properties': {
                        'to': {
                            'type': 'string',
                            'description': 'Recipient email address'
                        },
                        'subject': {
                            'type': 'string',
                            'description': 'Email subject line'
                        },
                        'body': {
                            'type': 'string',
                            'description': 'Email body content (plain text)'
                        },
                        'from_email': {
                            'type': 'string',
                            'description': 'Sender email (optional)'
                        }
                    },
                    'required': ['to', 'subject', 'body']
                }
            }
        ]

    def handle_tool_call(self, tool_name: str, arguments: dict) -> dict:
        """
        Handle MCP tool calls
        Routes to appropriate handler based on tool_name
        """
        if tool_name == 'send_email':
            return self.send_email(**arguments)
        else:
            return {
                'success': False,
                'error': f'Unknown tool: {tool_name}'
            }


# ============================================================================
# MCP Server Interface (Standard Protocol)
# ============================================================================

def create_mcp_server():
    """Factory function to create Gmail MCP Server instance"""
    return GmailMCPServer()


def list_tools():
    """List available tools for this MCP server"""
    server = create_mcp_server()
    return server.get_tools_definition()


def call_tool(name: str, arguments: dict) -> dict:
    """Call a tool by name with given arguments"""
    server = create_mcp_server()
    return server.handle_tool_call(name, arguments)


# ============================================================================
# CLI Interface for Testing
# ============================================================================

if __name__ == '__main__':
    import sys

    print("=" * 70)
    print("Gmail MCP Server - Gold Tier")
    print("=" * 70)
    print()

    # Test mode: list tools
    if len(sys.argv) == 1 or sys.argv[1] == 'list':
        print("Available Tools:")
        print()
        tools = list_tools()
        for tool in tools:
            print(f"📧 {tool['name']}")
            print(f"   Description: {tool['description']}")
            print(f"   Parameters: {', '.join(tool['input_schema']['required'])}")
            print()

    # Test mode: send test email
    elif sys.argv[1] == 'test':
        if len(sys.argv) < 4:
            print("Usage: python gmail_mcp_server.py test <to_email> <subject> [body]")
            sys.exit(1)

        to_email = sys.argv[2]
        subject = sys.argv[3]
        body = sys.argv[4] if len(sys.argv) > 4 else "Test email from Gmail MCP Server"

        print(f"Sending test email to {to_email}...")
        print()

        result = call_tool('send_email', {
            'to': to_email,
            'subject': subject,
            'body': body
        })

        if result['success']:
            print("✅ Email sent successfully!")
            print(f"   Message ID: {result['message_id']}")
        else:
            print("❌ Email failed to send")
            print(f"   Error: {result['error']}")

    else:
        print(f"Unknown command: {sys.argv[1]}")
        print()
        print("Available commands:")
        print("  list - List available tools")
        print("  test <to> <subject> [body] - Send test email")
