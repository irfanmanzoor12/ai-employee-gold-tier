from google_auth_oauthlib.flow import InstalledAppFlow
import sys

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# Step 1: Generate URL
flow = InstalledAppFlow.from_client_secrets_file(
    'credentials.json',
    SCOPES,
    redirect_uri='urn:ietf:wg:oauth:2.0:oob'
)

auth_url, _ = flow.authorization_url(prompt='consent')

print("="*70)
print("STEP 1: Open this URL in your browser:")
print("="*70)
print(auth_url)
print("="*70)
print()
print("STEP 2: After clicking 'Allow', copy the authorization code")
print("STEP 3: Run: .venv/bin/python complete_oauth.py <paste_code_here>")
print()

if len(sys.argv) < 2:
    sys.exit(0)

# Step 2: Exchange code
code = sys.argv[1]
print(f"Exchanging code: {code[:20]}...")

flow.fetch_token(code=code)

with open('token.json', 'w') as f:
    f.write(flow.credentials.to_json())

print()
print("="*70)
print("✅ token.json created")
print("="*70)
