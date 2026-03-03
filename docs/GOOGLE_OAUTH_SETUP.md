# Google OAuth Setup

How to enable "Sign in with Google" for BookVibe using django-allauth.

## 1. Create Google Cloud credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select existing)
3. Go to **APIs & Services** > **OAuth consent screen**
   - Select **External**, fill in app name and email
   - Add scopes: `userinfo.email`, `userinfo.profile`, `openid`
4. Go to **APIs & Services** > **Credentials** > **Create Credentials** > **OAuth client ID**
   - Type: **Web application**
   - Authorized JavaScript origins:
     - `http://localhost:8000` (dev)
     - `https://bookvibe.org` (production)
   - Authorized redirect URIs:
     - `http://localhost:8000/accounts/google/login/callback/`
     - `https://bookvibe.org/accounts/google/login/callback/`
5. Copy the **Client ID** and **Client Secret**

## 2. Configure Django

### Option A: Via `.env` file

```bash
ENABLE_GOOGLE_LOGIN=True
GOOGLE_OAUTH_CLIENT_ID=your-client-id
GOOGLE_OAUTH_CLIENT_SECRET=your-client-secret
```

### Option B: Via Django Admin

1. Go to `/donut1024/`
2. Under **Sites**, edit the default site:
   - Domain: `localhost:8000` (dev) or `bookvibe.org` (production)
   - Display name: `BookVibe`
3. Under **Social applications**, add:
   - Provider: **Google**
   - Name: `Google OAuth`
   - Client ID: paste from step 1
   - Secret key: paste from step 1
   - Sites: select your site

## 3. Test

Go to `/users/login/` — you should see "Continue with Google".

## Troubleshooting

**"Error 400: redirect_uri_mismatch"**
- The redirect URI in Google Console must exactly match: `http://localhost:8000/accounts/google/login/callback/` (including the trailing slash)

**"The app is not verified"**
- Normal for development. Click **Advanced** > **Go to BookVibe (unsafe)**
- For production, verify your app in Google Cloud Console

**Google button not showing**
- Check `ENABLE_GOOGLE_LOGIN=True` in `.env`
- Make sure the Social Application exists in Django Admin with the correct site selected

## Settings reference

These are already configured in `settings.py`:

```python
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_EMAIL_VERIFICATION = "optional"
SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_EMAIL_VERIFICATION = "none"
```
