#!/usr/bin/env python3
"""
Gmail MCP Server Authentication
Re-authenticates Gmail with SEND permissions (required for MCP server)
"""
import os
from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# Gmail API scopes - BOTH read and send
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',  # For monitoring
    'https://www.googleapis.com/auth/gmail.send'       # For MCP server ✅
]

print("=" * 70)
print("Gmail MCP Server - OAuth Authentication")
print("=" * 70)
print()
print("This will authenticate Gmail with SEND permissions.")
print("Required for the Gmail MCP Server (Gold Tier).")
print()

# Check for credentials.json
credentials_path = Path('credentials.json')
if not credentials_path.exists():
    print("❌ credentials.json not found!")
    print()
    print("Please download credentials.json from Google Cloud Console:")
    print("https://console.cloud.google.com/apis/credentials")
    exit(1)

print("✅ Found credentials.json")
print()

# Backup existing token if it exists
token_path = Path('token.json')
if token_path.exists():
    print("⚠️  Existing token.json found (readonly scope)")
    print("   Creating backup: token_readonly.json.backup")
    token_path.rename('token_readonly.json.backup')
    print("✅ Backup created")
    print()

print("Starting OAuth flow...")
print()
print("SCOPES REQUESTED:")
print("  ✅ gmail.readonly (for monitoring)")
print("  ✅ gmail.send (for MCP server)")
print()

try:
    # Create flow
    flow = InstalledAppFlow.from_client_secrets_file(
        str(credentials_path),
        scopes=SCOPES
    )

    # Get authorization URL
    auth_url, _ = flow.authorization_url(prompt='consent')

    print("=" * 70)
    print("STEP 1: AUTHORIZE IN BROWSER")
    print("=" * 70)
    print()
    print("Open this URL in your browser:")
    print()
    print(auth_url)
    print()
    print("⚠️  IMPORTANT: You will see TWO permission requests:")
    print("   1. Read-only access to Gmail (for monitoring)")
    print("   2. Send emails via Gmail (for MCP server)")
    print()
    print("   Approve BOTH permissions!")
    print()

    # Wait for user to authorize and paste code
    print("=" * 70)
    print("STEP 2: ENTER AUTHORIZATION CODE")
    print("=" * 70)
    print()
    print("After authorizing, you'll see an authorization code.")
    print("Copy it and paste it here:")
    print()

    code = input("Enter authorization code: ").strip()

    # Exchange code for token
    flow.fetch_token(code=code)
    creds = flow.credentials

    # Save token
    with open('token.json', 'w') as token:
        token.write(creds.to_json())

    print()
    print("=" * 70)
    print("✅ SUCCESS!")
    print("=" * 70)
    print()
    print("Gmail authenticated with SEND permissions!")
    print(f"Token saved to: {token_path.absolute()}")
    print()
    print("Next steps:")
    print("1. Test MCP server:")
    print("   .venv/bin/python gmail_mcp_server.py list")
    print()
    print("2. Send test email:")
    print("   .venv/bin/python gmail_mcp_server.py test your-email@example.com \"Test\"")
    print()

except Exception as e:
    print()
    print("=" * 70)
    print("❌ AUTHENTICATION FAILED")
    print("=" * 70)
    print()
    print(f"Error: {e}")
    print()
    print("Common issues:")
    print("- Wrong authorization code")
    print("- Expired authorization URL (get a fresh one)")
    print("- OAuth client not configured correctly")
    print()
    print("Try running this script again.")
    exit(1)
