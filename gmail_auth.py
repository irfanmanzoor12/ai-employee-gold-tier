"""
Gmail OAuth Authentication - Silver Tier
Runs once to generate token.json
"""
import json
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
CREDENTIALS_FILE = 'credentials.json'
TOKEN_FILE = 'token.json'

def authenticate():
    """Run OAuth flow and save token"""

    # Check credentials exist
    if not Path(CREDENTIALS_FILE).exists():
        print(f"❌ {CREDENTIALS_FILE} not found")
        print("Follow Google Console steps to download it")
        return False

    print("="*70)
    print("Gmail OAuth Authentication - Silver Tier")
    print("="*70)
    print()
    print("Starting local server on http://localhost:8080")
    print("Your browser will open automatically...")
    print()

    try:
        # Create flow
        flow = InstalledAppFlow.from_client_secrets_file(
            CREDENTIALS_FILE,
            SCOPES
        )

        # Run local server (browser opens automatically)
        creds = flow.run_local_server(port=8080)

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
        print("✅ Authentication Successful!")
        print("="*70)
        print(f"✅ {TOKEN_FILE} created")
        print("✅ Gmail Watcher ready to run")
        print()
        print("Next: Run gmail_watcher.py")
        return True

    except Exception as e:
        print()
        print("="*70)
        print("❌ Authentication Failed")
        print("="*70)
        print(f"Error: {e}")
        print()
        print("Troubleshooting:")
        print("1. Check OAuth client is 'Web application' type")
        print("2. Check redirect URI is http://localhost:8080/")
        print("3. Check your email is added as test user")
        return False

if __name__ == '__main__':
    authenticate()
