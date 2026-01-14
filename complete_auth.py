"""
Complete Gmail OAuth by manually providing redirect URL
Silver Tier - Manual code exchange
"""
import json
import sys
from urllib.parse import urlparse, parse_qs
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
CREDENTIALS_FILE = 'credentials.json'
TOKEN_FILE = 'token.json'

def complete_auth(redirect_url):
    """Exchange authorization code for tokens"""

    # Parse URL to extract code and state
    parsed = urlparse(redirect_url)
    params = parse_qs(parsed.query)

    if 'code' not in params:
        print("❌ No authorization code found in URL")
        return False

    code = params['code'][0]
    state = params.get('state', [None])[0]

    print("✅ Authorization code extracted")
    print(f"   Code: {code[:20]}...")
    print(f"   State: {state}")
    print()

    try:
        # Create flow
        flow = InstalledAppFlow.from_client_secrets_file(
            CREDENTIALS_FILE,
            SCOPES,
            redirect_uri='http://localhost:8080/'
        )

        # Set state
        if state:
            flow.oauth2session.state = state

        # Exchange code for credentials
        print("Exchanging code for tokens...")
        flow.fetch_token(code=code)
        creds = flow.credentials

        # Save token
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

        print()
        print("="*70)
        print("✅ Authentication Complete!")
        print("="*70)
        print(f"✅ {TOKEN_FILE} created")
        print("✅ Refresh token saved")
        print()
        return True

    except Exception as e:
        print()
        print("="*70)
        print("❌ Token exchange failed")
        print("="*70)
        print(f"Error: {e}")
        return False

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python complete_auth.py 'http://localhost:8080/?state=...&code=...'")
        sys.exit(1)

    redirect_url = sys.argv[1]
    success = complete_auth(redirect_url)
    sys.exit(0 if success else 1)
