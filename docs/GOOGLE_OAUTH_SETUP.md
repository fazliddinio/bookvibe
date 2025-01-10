# Google OAuth Setup Guide for BookVibe

This guide will help you set up Google authentication for your BookVibe application.

## Prerequisites

✅ Google Account
✅ Django Allauth already installed (already configured in your project)
✅ Access to Django Admin panel

---

## Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click **"Select a project"** → **"New Project"**
3. Enter project name: `BookVibe` (or any name you prefer)
4. Click **"Create"**

---

## Step 2: Configure OAuth Consent Screen

1. In the Google Cloud Console, go to **"APIs & Services"** → **"OAuth consent screen"**
2. Select **"External"** user type → Click **"Create"**
3. Fill in the required information:
   - **App name:** BookVibe
   - **User support email:** Your email
   - **Developer contact information:** Your email
4. Click **"Save and Continue"**
5. On "Scopes" page → Click **"Add or Remove Scopes"**
6. Select these scopes:
   - `userinfo.email`
   - `userinfo.profile`
   - `openid`
7. Click **"Update"** → **"Save and Continue"**
8. On "Test users" page (for development):
   - Click **"Add Users"**
   - Add your test email addresses
   - Click **"Save and Continue"**
9. Click **"Back to Dashboard"**

---

## Step 3: Create OAuth 2.0 Credentials

1. Go to **"APIs & Services"** → **"Credentials"**
2. Click **"Create Credentials"** → **"OAuth client ID"**
3. Select **"Web application"**
4. Fill in the details:
   - **Name:** BookVibe Web Client
   - **Authorized JavaScript origins:**
     - `http://localhost:8000`
     - `http://127.0.0.1:8000`
     - (Add your production domain when deploying: `https://yourdomain.com`)
   
   - **Authorized redirect URIs:**
     - `http://localhost:8000/accounts/google/login/callback/`
     - `http://127.0.0.1:8000/accounts/google/login/callback/`
     - (Add your production URI when deploying: `https://yourdomain.com/accounts/google/login/callback/`)

5. Click **"Create"**
6. **IMPORTANT:** Copy and save:
   - **Client ID** (looks like: `123456789-abc...xyz.apps.googleusercontent.com`)
   - **Client Secret** (looks like: `GOCSPX-...`)

---

## Step 4: Configure Django Admin

1. Start your Django development server:
   ```bash
   python3 manage.py runserver
   ```

2. Go to Django Admin: `http://localhost:8000/admin/`

3. Log in with your superuser account (create one if you don't have):
   ```bash
   python3 manage.py createsuperuser
   ```

4. In Django Admin, navigate to:
   **Sites** → Click on **example.com** → Edit:
   - **Domain name:** `localhost:8000`
   - **Display name:** `BookVibe`
   - Click **"Save"**

5. Navigate to **Social applications** → Click **"Add Social Application"**
   - **Provider:** Google
   - **Name:** Google OAuth
   - **Client id:** (Paste your Google Client ID from Step 3)
   - **Secret key:** (Paste your Google Client Secret from Step 3)
   - **Sites:** Select `localhost:8000` and move it to "Chosen sites" using the arrow
   - Click **"Save"**

---

## Step 5: Update Environment Variables (Optional but Recommended)

For production, add these to your `.env` file:

```env
# Google OAuth (Optional - can be managed via Django Admin)
GOOGLE_OAUTH_CLIENT_ID=your-client-id-here
GOOGLE_OAUTH_CLIENT_SECRET=your-client-secret-here
```

---

## Step 6: Test Google Authentication

1. Go to your login page: `http://localhost:8000/users/login/`
2. You should now see a **"Continue with Google"** button
3. Click the button to test the Google OAuth flow
4. Sign in with your Google account
5. After successful authentication, you'll be redirected to the homepage

---

## Troubleshooting

### Issue: "Error 400: redirect_uri_mismatch"
**Solution:** 
- Make sure your redirect URI in Google Cloud Console exactly matches:
  `http://localhost:8000/accounts/google/login/callback/`
- Check that there are no trailing slashes issues
- Verify the domain in Django Admin Sites matches your current domain

### Issue: "The app is not verified"
**Solution:** 
- This is normal for development
- Click **"Advanced"** → **"Go to BookVibe (unsafe)"**
- For production, you'll need to verify your app with Google

### Issue: Google button not showing
**Solution:**
- Make sure you've collected static files: `python3 manage.py collectstatic`
- Clear browser cache and hard refresh (Ctrl+Shift+R / Cmd+Shift+R)
- Check Django admin to ensure Social Application is created

### Issue: "Social account not found"
**Solution:**
- The email from Google must match an existing user, or
- A new user will be created automatically with the Google email
- Make sure `ACCOUNT_EMAIL_VERIFICATION = "mandatory"` is set correctly in settings

---

## Production Deployment

When deploying to production:

1. Update Google Cloud Console:
   - Add production domain to "Authorized JavaScript origins"
   - Add production callback URL to "Authorized redirect URIs"
   - Example: `https://yourdomain.com/accounts/google/login/callback/`

2. Update Django Admin:
   - Change Site domain from `localhost:8000` to your production domain
   - Update the Social Application if needed

3. Update `.env`:
   - Set `SITE_URL=https://yourdomain.com`

4. Verify your app in Google Cloud Console (optional but recommended)

---

## Security Notes

⚠️ **NEVER commit your Client Secret to version control**
⚠️ Keep your `.env` file in `.gitignore`
⚠️ Use environment variables for production credentials
⚠️ Regularly rotate your OAuth credentials

---

## Support

If you encounter any issues:
1. Check Django logs: `logs/django.log`
2. Check browser console for JavaScript errors
3. Verify all URLs match exactly in Google Cloud Console
4. Ensure HTTPS is used in production

---

## What's Already Configured

✅ Django Allauth installed
✅ Google provider configured in settings.py
✅ Google sign-in buttons added to login and register pages
✅ Beautiful UI with Google branding
✅ Proper OAuth scopes configured
✅ Redirect URLs configured

All you need to do is complete Steps 1-4 above! 🎉

