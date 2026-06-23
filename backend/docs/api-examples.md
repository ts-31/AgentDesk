# TeamFlow API Examples

This document provides `curl` examples for interacting with the TeamFlow backend APIs. All examples assume the server is running locally on `http://127.0.0.1:8000`.

---

## 🔐 Authentication & Access Token

All resources (except `/auth/*` endpoints and `/health`) now require authentication. You must obtain a JSON Web Token (JWT) by calling the login endpoint and supply it in the `Authorization` header as a Bearer token:
`-H "Authorization: Bearer <access_token>"`

### 1. Authenticate / Login
Retrieve access and refresh tokens.

**Request:**
```bash
curl -X POST "http://127.0.0.1:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "lisa30@example.com",
    "password": "changeme123"
  }'
```

**Success Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### 2. Refresh Token
Exchange a refresh token for a fresh access token.

**Request:**
```bash
curl -X POST "http://127.0.0.1:8000/auth/refresh" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "<refresh_token>"
  }'
```

---

## 🏢 Customers API

### 1. List All Customers
Fetch a paginated list of customers.

**Request:**
```bash
curl -X GET "http://127.0.0.1:8000/customers?skip=0&limit=5" \
  -H "Authorization: Bearer <access_token>"
```

**Success Response (200 OK):**
```json
[
  {
    "company_name": "Gibbs-Hopkins",
    "plan_type": "Free",
    "customer_id": "b61e957b-e0f8-4bc2-941a-31a737b4c1c3",
    "created_at": "2025-08-02T15:52:22"
  }
]
```

### 2. Get Customer Details
Fetch details for a specific customer by UUID.

**Request:**
```bash
curl -X GET "http://127.0.0.1:8000/customers/b61e957b-e0f8-4bc2-941a-31a737b4c1c3" \
  -H "Authorization: Bearer <access_token>"
```

**Error Response (404 Not Found):**
```json
{
  "detail": "Customer not found"
}
```

### 3. Get Customer Relations
You can fetch related entities for a specific customer using nested routes:

**List Users for a Customer:**
```bash
curl -X GET "http://127.0.0.1:8000/customers/b61e957b-e0f8-4bc2-941a-31a737b4c1c3/users" \
  -H "Authorization: Bearer <access_token>"
```

**Get Subscriptions for a Customer:**
```bash
curl -X GET "http://127.0.0.1:8000/customers/b61e957b-e0f8-4bc2-941a-31a737b4c1c3/subscription" \
  -H "Authorization: Bearer <access_token>"
```

**List Invoices for a Customer:**
```bash
curl -X GET "http://127.0.0.1:8000/customers/b61e957b-e0f8-4bc2-941a-31a737b4c1c3/invoices" \
  -H "Authorization: Bearer <access_token>"
```

**List Tickets for a Customer:**
```bash
curl -X GET "http://127.0.0.1:8000/customers/b61e957b-e0f8-4bc2-941a-31a737b4c1c3/tickets" \
  -H "Authorization: Bearer <access_token>"
```

---

## 👤 Users API

### 1. List All Users
Fetch a paginated list of users.

**Request:**
```bash
curl -X GET "http://127.0.0.1:8000/users?limit=5" \
  -H "Authorization: Bearer <access_token>"
```

**Success Response (200 OK):**
```json
[
  {
    "customer_id": "8267285f-0c85-43d3-98cb-d2bc67bf8ddc",
    "email": "lindsey99@example.net",
    "role": "Admin",
    "sso_enabled": true,
    "user_id": "1f66c75f-4ea6-4e05-82c6-8c83b1578cd5"
  }
]
```

### 2. Get User Details
Fetch a single user by UUID.

**Request:**
```bash
curl -X GET "http://127.0.0.1:8000/users/1f66c75f-4ea6-4e05-82c6-8c83b1578cd5" \
  -H "Authorization: Bearer <access_token>"
```

---

## 📦 Subscriptions API

### 1. List All Subscriptions
Fetch a paginated list of subscriptions.

**Request:**
```bash
curl -X GET "http://127.0.0.1:8000/subscriptions?limit=5" \
  -H "Authorization: Bearer <access_token>"
```

### 2. Get Subscription Details
Fetch a specific subscription by UUID.

**Request:**
```bash
curl -X GET "http://127.0.0.1:8000/subscriptions/c3975ff1-f1e3-42b7-ac8a-fa97f9a87d47" \
  -H "Authorization: Bearer <access_token>"
```

**Success Response (200 OK):**
```json
{
  "customer_id": "b61e957b-e0f8-4bc2-941a-31a737b4c1c3",
  "plan_tier": "Free",
  "billing_cycle": "Annual",
  "status": "Active",
  "start_date": "2025-09-22T23:34:29",
  "end_date": "2025-10-22T23:34:29",
  "canceled_at": null,
  "auto_renew": true,
  "subscription_id": "c3975ff1-f1e3-42b7-ac8a-fa97f9a87d47"
}
```

---

## 💳 Invoices API

### 1. List All Invoices
Fetch a paginated list of invoices.

**Request:**
```bash
curl -X GET "http://127.0.0.1:8000/invoices?limit=5" \
  -H "Authorization: Bearer <access_token>"
```

### 2. Get Invoice Details
Fetch a specific invoice by UUID.

**Request:**
```bash
curl -X GET "http://127.0.0.1:8000/invoices/704cd756-a62a-4e0b-b11d-7c6aecdfe1c8" \
  -H "Authorization: Bearer <access_token>"
```

**Success Response (200 OK):**
```json
{
  "customer_id": "5a470a06-a900-4747-814e-117033e5215f",
  "amount": "3405.94",
  "status": "Unpaid",
  "created_at": "2025-08-28T12:09:03",
  "due_date": "2025-09-27T12:09:03",
  "paid_at": null,
  "billing_period_start": "2025-07-29T12:09:03",
  "billing_period_end": "2025-08-28T12:09:03",
  "invoice_id": "704cd756-a62a-4e0b-b11d-7c6aecdfe1c8"
}
```

---

## 🎫 Tickets API

### 1. List All Tickets
Fetch a paginated list of support tickets.

**Request:**
```bash
curl -X GET "http://127.0.0.1:8000/tickets?limit=5" \
  -H "Authorization: Bearer <access_token>"
```

### 2. Get Ticket Details
Fetch a specific ticket by UUID.

**Request:**
```bash
curl -X GET "http://127.0.0.1:8000/tickets/1559c33a-a7b9-459d-a4c9-0d7e73459481" \
  -H "Authorization: Bearer <access_token>"
```

**Success Response (200 OK):**
```json
{
  "customer_id": "1b25274e-ac91-4f88-adc3-07cd1407e159",
  "user_id": "9ccd70fe-b06d-4d19-9b15-969433f91cc2",
  "category": "Login",
  "status": "Open",
  "priority": "Medium",
  "created_at": "2026-06-16T13:52:27",
  "ticket_id": "1559c33a-a7b9-459d-a4c9-0d7e73459481"
}
```

### 3. Create a Ticket
Create a new support ticket. Validates that the `customer_id` and `user_id` exist.

**Request:**
```bash
curl -X POST "http://127.0.0.1:8000/tickets" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "8267285f-0c85-43d3-98cb-d2bc67bf8ddc",
    "user_id": "1f66c75f-4ea6-4e05-82c6-8c83b1578cd5",
    "category": "technical",
    "subject": "Cannot access dashboard",
    "description": "I get a 403 error when trying to view my team dashboard.",
    "status": "open",
    "priority": "high"
  }'
```

**Success Response (201 Created):**
```json
{
  "customer_id": "8267285f-0c85-43d3-98cb-d2bc67bf8ddc",
  "user_id": "1f66c75f-4ea6-4e05-82c6-8c83b1578cd5",
  "category": "technical",
  "status": "open",
  "priority": "high",
  "created_at": "2026-06-16T08:42:22.027105",
  "ticket_id": "41bdd3d5-cf16-4591-8a28-3cba87b0706b"
}
```

---

## 🧠 Knowledge Base Search API

### 1. Semantic Search
Perform a semantic search against the knowledge base.

**Request:**
```bash
curl -X GET "http://127.0.0.1:8000/knowledge-base/search?q=how%20do%20I%20reset%20my%20password&limit=3" \
  -H "Authorization: Bearer <access_token>"
```

**Success Response (200 OK):**
```json
{
  "query": "how do I reset my password",
  "results": [
    {
      "article_title": "Password Reset and Login Issues",
      "article_slug": "password-reset-and-login-issues",
      "chunk_text": "Password Requirements",
      "similarity_score": 0.7947
    }
  ]
}
```

---

## 🤖 Agent API

### 1. Ask a Question (RAG Pipeline)
Submit a question to the agent. Requires `Authorization` header.

**Request:**
```bash
curl -X POST "http://127.0.0.1:8000/agent/ask" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How do I reset my password?"
  }'
```

---

## 🏥 Health Check

### 1. Check Service Health
Unprotected diagnostics route.

**Request:**
```bash
curl -X GET "http://127.0.0.1:8000/health"
```
