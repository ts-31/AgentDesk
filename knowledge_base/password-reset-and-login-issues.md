# Password Reset and Login Issues

**Summary:**
Step-by-step guidance for resetting your TeamFlow password, resolving common login failures, and recovering access to your workspace.

**Tags:** password, reset, login, authentication, locked out, forgot password, MFA, two-factor, access, credentials

---

## Overview

TeamFlow uses email-based authentication by default. If your workspace has SSO enabled, see the [SSO Setup and Troubleshooting](./sso-setup-and-troubleshooting.md) article instead.

---

## Resetting Your Password

1. Go to the TeamFlow login page at **app.teamflow.io/login**.
2. Click **Forgot your password?** below the sign-in form.
3. Enter your registered email address and click **Send Reset Link**.
4. Check your inbox for an email from **noreply@teamflow.io** — it may take up to 2 minutes to arrive.
5. Click the reset link in the email. The link is valid for **30 minutes**.
6. Enter and confirm your new password, then click **Reset Password**.
7. You will be redirected to the login page. Sign in with your new password.

> If you don't see the email, check your **Spam** or **Junk** folder. Ensure your email provider is not blocking messages from `teamflow.io`.

---

## Password Requirements

TeamFlow enforces the following password policy:

- Minimum **10 characters**
- At least **one uppercase letter**
- At least **one number**
- At least **one special character** (`!`, `@`, `#`, `$`, etc.)
- Cannot be the same as your last **5 passwords**

---

## Common Login Issues

### "Invalid email or password"

- Double-check that you are using the correct email address associated with your TeamFlow account.
- Ensure **Caps Lock** is not enabled.
- If you recently changed your password, try using the new one.
- Use **Forgot your password?** to reset if you are unsure.

### "Your account has been locked"

After **5 consecutive failed login attempts**, your account is temporarily locked for **15 minutes** as a security measure. Wait and try again, or reset your password immediately.

### "This account requires SSO login"

Your workspace Admin has enforced SSO-only login. You must sign in through your company's identity provider (e.g., Okta, Azure AD, Google Workspace). Password-based login is disabled for your account.

### "Account not found"

- Confirm you are using the correct email.
- Your account may have been removed from the workspace. Contact your workspace Admin.
- If you signed up with a different email, try that address.

### "Your session has expired"

TeamFlow sessions expire after **7 days** of inactivity. Simply log in again to start a new session.

---

## Multi-Factor Authentication (MFA)

If MFA is enabled on your account:

1. After entering your email and password, you will be prompted for a 6-digit verification code.
2. Open your authenticator app (e.g., Google Authenticator, Authy) and enter the current code.
3. Codes rotate every **30 seconds**.

**Lost access to your authenticator app?**

1. Click **Use a backup code** on the MFA prompt.
2. Enter one of the 8-digit backup codes saved when you set up MFA.
3. Once logged in, go to **Settings → Security → MFA** to reconfigure your authenticator app.

If you have used all backup codes and lost access to your authenticator, contact **support@teamflow.io** with a government-issued ID and proof of account ownership.

---

## Admin: Resetting a User's Password

Admins can trigger a password reset for any user in the workspace:

1. Go to **Settings → Team → Members**.
2. Find the user and click **Actions → Send Password Reset**.
3. TeamFlow will email a reset link directly to the user.

Admins cannot view or set passwords directly — only the user can set their own password via the reset link.

---

## FAQs

**Q: My reset link says it has expired. What do I do?**
Reset links expire after 30 minutes. Return to the login page and request a new reset link.

**Q: I never received the reset email.**
Check your spam folder first. If it's not there, ensure your email address is correctly registered. Contact support if the issue persists — your domain may be blocking emails from `teamflow.io`.

**Q: Can I log in to multiple devices simultaneously?**
Yes. TeamFlow supports concurrent sessions across multiple devices. You can view and revoke active sessions at **Settings → Security → Active Sessions**.
