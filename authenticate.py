"""Manual Gmail Authentication"""
from google_auth_oauthlib.flow import InstalledAppFlow
import json

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

print("="*70)
print("GMAIL AUTHENTICATION")
print("="*70)

# Create flow
flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)

# Start local server and get credentials
print("\nStarting local authentication server on port 8080...")
print("\nOPEN THIS URL IN YOUR BROWSER:")
print("-"*70)

# Run with specific port and don't auto-open browser
try:
    creds = flow.run_local_server(port=8080, open_browser=False)

    # Save token
    token_data = {
        'token': creds.token,
        'refresh_token': creds.refresh_token,
        'token_uri': creds.token_uri,
        'client_id': creds.client_id,
        'client_secret': creds.client_secret,
        'scopes': creds.scopes
    }

    with open('token.json', 'w') as f:
        json.dump(token_data, f)

    print("\n" + "="*70)
    print("✅ AUTHENTICATION SUCCESSFUL!")
    print("="*70)
    print("✅ token.json has been created")
    print("\nYou can now run: .venv/bin/python gmail_watcher.py")

except Exception as e:
    print(f"\n❌ Error: {e}")
