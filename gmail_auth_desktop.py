from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

flow = InstalledAppFlow.from_client_secrets_file(
    'credentials.json',
    SCOPES,
    redirect_uri='urn:ietf:wg:oauth:2.0:oob'
)

auth_url, _ = flow.authorization_url(prompt='consent')

print("Open this URL in your browser:")
print(auth_url)

code = input("Paste the authorization code here: ").strip()

flow.fetch_token(code=code)

with open('token.json', 'w') as f:
    f.write(flow.credentials.to_json())

print("✅ token.json created")
