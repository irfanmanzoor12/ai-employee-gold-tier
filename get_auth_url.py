"""Generate Gmail OAuth authentication URL"""
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# Create flow
flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)

# Generate auth URL
auth_url, _ = flow.authorization_url(
    access_type='offline',
    include_granted_scopes='true'
)

print("\n" + "="*70)
print("GMAIL AUTHENTICATION URL")
print("="*70)
print("\n1. Copy the URL below")
print("2. Paste it in your Windows browser (Chrome, Edge, Firefox)")
print("3. Sign in with your Gmail account")
print("4. Click 'Allow' when asked for permissions")
print("5. You'll see a code - copy it")
print("6. Come back here and paste the code\n")
print("="*70)
print("\nAUTHENTICATION URL:")
print(auth_url)
print("\n" + "="*70)
print("\nAfter you authorize, enter the code you receive:")
code = input("Paste the authorization code here: ").strip()

# Exchange code for credentials
flow.fetch_token(code=code)
creds = flow.credentials

# Save credentials
import json
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

print("\n✅ Authentication successful!")
print("✅ token.json has been created")
print("\nYou can now run: .venv/bin/python gmail_watcher.py")
