"""
Exchange authorization code for token
Silver Tier - Desktop OAuth
"""
import json
import sys
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
CREDENTIALS_FILE = 'credentials.json'
TOKEN_FILE = 'token.json'

if len(sys.argv) < 2:
    print("Usage: python exchange_code.py <authorization_code>")
    sys.exit(1)

code = sys.argv[1]

print("Exchanging authorization code for token...")

try:
    flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
    flow.fetch_token(code=code)
    creds = flow.credentials

    token_data = {
        'token': creds.token,
        'refresh_token': creds.refresh_token,
        'token_uri': creds.token_uri,
        'client_id': creds.client_id,
        'client_secret': creds.client_secret,
        'scopes': creds.scopes
    }

    with open(TOKEN_FILE, 'w') as f:
        json.dump(token_data, f, indent=2)

    print("="*70)
    print("✅ Authentication Complete!")
    print("="*70)
    print(f"✅ {TOKEN_FILE} created")

except Exception as e:
    print("="*70)
    print("❌ Token exchange failed")
    print("="*70)
    print(f"Error: {e}")
    sys.exit(1)
