# API Rate Limits and Authentication

**Summary:**
Learn how to authenticate with the AgentDesk API, manage API keys, and understand our rate-limiting policies to ensure reliable integrations.

**Tags:** API, developer, authentication, rate limits, API keys, 429, headers, integration, webhooks

---

## Overview

The AgentDesk REST API allows you to programmatically manage workspaces, users, projects, and billing. Access to the API is available on **Pro**, **Business**, and **Enterprise** plans.

The base URL for all API requests is:
`https://api.agentdesk.io/v1`

---

## Authentication

Authentication is handled via **Bearer Tokens** (API Keys). All requests to the AgentDesk API must include an `Authorization` header containing a valid API key.

### Generating an API Key

1. Log in to AgentDesk as an **Admin**.
2. Navigate to **Settings → Developer → API Keys**.
3. Click **Generate New Key**.
4. Provide a descriptive name for the key (e.g., "Zapier Integration" or "Internal Dashboard").
5. Copy the generated key immediately. **For security reasons, it will never be displayed again.**

### Using the API Key

Include the API key in the `Authorization` header of your HTTP requests:

```http
GET /v1/users HTTP/1.1
Host: api.agentdesk.io
Authorization: Bearer tf_live_xxxxxxxxxxxxxxxxxxxx
Accept: application/json
```

### Revoking Keys

If an API key is compromised, you can revoke it instantly:

1. Go to **Settings → Developer → API Keys**.
2. Find the key in the list and click **Revoke**.
3. Any requests using the revoked key will immediately receive a `401 Unauthorized` response.

---

## Rate Limits

To ensure system stability and fair usage, the AgentDesk API enforces rate limits based on your subscription tier.

### Limits by Plan

| Plan       | Rate Limit                  | Burst Capacity |
|------------|-----------------------------|----------------|
| Free       | API Access Disabled         | N/A            |
| Pro        | 100 requests / minute       | 20 requests    |
| Business   | 500 requests / minute       | 50 requests    |
| Enterprise | Custom (default: 2000/min)  | Custom         |

### Understanding Rate Limit Headers

Every API response includes headers detailing your current rate limit status:

- `X-RateLimit-Limit`: Your maximum requests per minute.
- `X-RateLimit-Remaining`: The number of requests left in the current window.
- `X-RateLimit-Reset`: The Unix timestamp when the current window resets and your remaining requests are replenished.

### Handling Rate Limits (HTTP 429)

If you exceed your rate limit, the API will respond with an **HTTP 429 Too Many Requests** status code. The response body will contain information about when you can retry.

```json
{
  "error": "rate_limit_exceeded",
  "message": "You have exceeded your API rate limit.",
  "retry_after": 45
}
```

The `Retry-After` header will also be present, indicating the number of seconds to wait before making another request.

**Best Practices:**
- Implement exponential backoff in your code to automatically handle 429 responses.
- Cache data where possible to reduce unnecessary API calls.
- Use bulk endpoints (e.g., `POST /v1/users/batch`) instead of individual requests when operating on multiple resources.

---

## Webhooks

If you are polling the API frequently for updates, consider using **Webhooks** instead. Webhooks push data to your servers in real-time when specific events occur (e.g., `user.created`, `invoice.paid`).

Configure webhooks in **Settings → Developer → Webhooks**. Webhooks do not count against your API rate limits.

---

## FAQs

**Q: Do failed requests count against my rate limit?**
Yes. All requests (including 4xx and 5xx errors) count towards your rate limit.

**Q: Can I create a read-only API key?**
Currently, all API keys inherit the permissions of the Admin user who created them. Scoped API keys (e.g., read-only, billing-only) are on our roadmap for late 2026.
