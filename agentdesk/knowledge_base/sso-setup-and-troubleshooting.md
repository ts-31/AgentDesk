# SSO Setup and Troubleshooting

**Summary:**
Instructions for configuring Single Sign-On (SSO) for your AgentDesk workspace using SAML 2.0, along with solutions to common setup and login issues.

**Tags:** SSO, single sign-on, SAML, Okta, Azure AD, identity provider, login, security, authentication, IdP

---

## Overview

AgentDesk supports SAML 2.0 Single Sign-On (SSO) on **Business** and **Enterprise** plans. Configuring SSO allows your team to securely log in using your existing Identity Provider (IdP) credentials and enforces centralized access control.

---

## Supported Identity Providers

AgentDesk officially supports and provides detailed guides for the following IdPs:

- Okta
- Microsoft Entra ID (formerly Azure AD)
- Google Workspace
- OneLogin
- Ping Identity

However, any IdP that supports standard SAML 2.0 can be configured with AgentDesk.

---

## Step 1: Configure Your Identity Provider

First, you need to create a new SAML application in your IdP. Use the following AgentDesk details:

- **Entity ID (Audience URI):** `https://app.agentdesk.io/saml/metadata`
- **Assertion Consumer Service (ACS) URL:** `https://app.agentdesk.io/saml/acs`
- **Name ID Format:** `EmailAddress`

### Attribute Mapping

AgentDesk requires specific attributes to be mapped in the SAML response for successful provisioning:

- `email` (Required): The user's email address. Must map to the `NameID`.
- `firstName` (Optional): The user's given name.
- `lastName` (Optional): The user's family name.

---

## Step 2: Configure AgentDesk

Once the application is created in your IdP, you'll need the metadata details to configure AgentDesk.

1. Log in to AgentDesk as an **Admin**.
2. Navigate to **Settings → Security → Single Sign-On**.
3. Toggle **Enable SAML SSO** to **On**.
4. Enter the details provided by your IdP:
   - **IdP Entity ID / Issuer URL**
   - **IdP SSO URL (Sign-in URL)**
   - **X.509 Certificate** (Paste the full certificate string, including `-----BEGIN CERTIFICATE-----` and `-----END CERTIFICATE-----`)
5. Click **Save Configuration**.

---

## Step 3: Test and Enforce SSO

Before enforcing SSO for all users, it is crucial to test the integration.

1. Keep your current Admin session active in one browser tab.
2. Open a new Incognito/Private window.
3. Go to the AgentDesk login page and click **Log in with SSO**.
4. Enter your email address. You should be redirected to your IdP.
5. Authenticate with your IdP. You should be redirected back to AgentDesk and successfully logged in.

Once testing is successful:

1. Return to **Settings → Security → Single Sign-On**.
2. Toggle **Enforce SSO for all users** to **On**.
3. Click **Save Configuration**.

> **Important:** When SSO enforcement is enabled, users will no longer be able to log in using an email and password combination. They must authenticate via your IdP.

---

## Just-in-Time (JIT) Provisioning

AgentDesk supports JIT provisioning. If a user authenticates via SSO but does not yet have a AgentDesk account, an account will be automatically created for them with the default **Member** role.

To disable JIT provisioning, toggle **Enable JIT Provisioning** to **Off** in the SSO settings.

---

## Troubleshooting Common Issues

### Error: "SAML response signature validation failed"
- **Cause:** The X.509 certificate configured in AgentDesk does not match the certificate used by the IdP to sign the SAML assertion.
- **Solution:** Verify the certificate in AgentDesk matches the one provided by your IdP. Ensure there are no extra spaces or missing lines.

### Error: "Invalid NameID format" or "Email attribute missing"
- **Cause:** The IdP is not sending the user's email address in the expected format.
- **Solution:** Check your IdP attribute mappings. Ensure the `NameID` format is set to `EmailAddress` and maps to the user's email.

### Error: "User not found" (when JIT is disabled)
- **Cause:** The user attempted to log in via SSO, but they do not have a AgentDesk account, and JIT provisioning is disabled.
- **Solution:** Either enable JIT provisioning or manually create the user in AgentDesk before they attempt to log in.

### Admin Locked Out
If SSO is enforced and your IdP experiences an outage or configuration error, Admins can bypass SSO using a recovery URL.

1. Navigate to `https://app.agentdesk.io/login/recovery`.
2. Enter your Admin email and password.
3. You will be prompted to enter a recovery code (provided during initial SSO setup).

Store your recovery codes securely. If you lose them, contact support for assistance.
