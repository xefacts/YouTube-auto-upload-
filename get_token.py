from google_auth_oauthlib.flow import InstalledAppFlow

# Aapki Client ID aur Client Secret yahan pehle se added hain
CLIENT_ID = "19391264544-qnok75j2tnmutjhoqcm7fvsgif4c73c.apps.googleusercontent.com"
CLIENT_SECRET = "GOCSPX-qWL30N27UHP4OBv6UQC9SuHvMiC"

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def get_refresh_token():
    client_config = {
        "installed": {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://localhost"]
        }
    }
    
    flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
    credentials = flow.run_local_server(port=0)
    
    print("\n================================")
    print("Aapka Refresh Token yeh raha:")
    print(credentials.refresh_token)
    print("================================")

if __name__ == "__main__":
    get_refresh_token()
￼Enter
