# TeamFlow API Examples

This document provides `curl` examples for interacting with the TeamFlow backend APIs. All examples assume the server is running locally on `http://127.0.0.1:8000`.

---

## 🏢 Customers API

### 1. List All Customers
Fetch a paginated list of customers.

**Request:**
```bash
curl -X GET "http://127.0.0.1:8000/customers?skip=0&limit=5"
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
curl -X GET "http://127.0.0.1:8000/customers/b61e957b-e0f8-4bc2-941a-31a737b4c1c3"
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
curl -X GET "http://127.0.0.1:8000/customers/b61e957b-e0f8-4bc2-941a-31a737b4c1c3/users"
```

**Get Subscriptions for a Customer:**
```bash
curl -X GET "http://127.0.0.1:8000/customers/b61e957b-e0f8-4bc2-941a-31a737b4c1c3/subscription"
```

**List Invoices for a Customer:**
```bash
curl -X GET "http://127.0.0.1:8000/customers/b61e957b-e0f8-4bc2-941a-31a737b4c1c3/invoices"
```

**List Tickets for a Customer:**
```bash
curl -X GET "http://127.0.0.1:8000/customers/b61e957b-e0f8-4bc2-941a-31a737b4c1c3/tickets"
```

---

## 👤 Users API

### 1. List All Users
Fetch a paginated list of users.

**Request:**
```bash
curl -X GET "http://127.0.0.1:8000/users?limit=5"
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
curl -X GET "http://127.0.0.1:8000/users/1f66c75f-4ea6-4e05-82c6-8c83b1578cd5"
```

---

## 📦 Subscriptions API

### 1. List All Subscriptions
Fetch a paginated list of subscriptions.

**Request:**
```bash
curl -X GET "http://127.0.0.1:8000/subscriptions?limit=5"
```

### 2. Get Subscription Details
Fetch a specific subscription by UUID.

**Request:**
```bash
curl -X GET "http://127.0.0.1:8000/subscriptions/c3975ff1-f1e3-42b7-ac8a-fa97f9a87d47"
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
curl -X GET "http://127.0.0.1:8000/invoices?limit=5"
```

### 2. Get Invoice Details
Fetch a specific invoice by UUID.

**Request:**
```bash
curl -X GET "http://127.0.0.1:8000/invoices/704cd756-a62a-4e0b-b11d-7c6aecdfe1c8"
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
curl -X GET "http://127.0.0.1:8000/tickets?limit=5"
```

### 2. Get Ticket Details
Fetch a specific ticket by UUID.

**Request:**
```bash
curl -X GET "http://127.0.0.1:8000/tickets/1559c33a-a7b9-459d-a4c9-0d7e73459481"
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

**Error Response (404 Not Found - Invalid Customer/User):**
```json
{
  "detail": "Customer not found"
}
```

---

## 🧠 Knowledge Base Search API

### 1. Semantic Search
Perform a semantic search against the knowledge base.

**Request:**
```bash
curl -X GET "http://127.0.0.1:8000/knowledge-base/search?q=how%20do%20I%20reset%20my%20password&limit=3"
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
    },
    {
      "article_title": "Password Reset and Login Issues",
      "article_slug": "password-reset-and-login-issues",
      "chunk_text": "Admin: Resetting a User's Password\n\nAdmins can trigger a password reset for any user in the workspace:\n\n1. Go to Settings → Team → Members.\n2. Find the user and click Actions → Send Password Reset.\n3. TeamFlow will email a reset link directly to the user.\n\nAdmins cannot view or set passwords directly — only the user can set their own password via the reset link.",
      "similarity_score": 0.7897
    }
  ]
}
```

**Error Response (400 Bad Request - Empty Query):**
```json
{
  "detail": "Query parameter 'q' must not be empty or whitespace."
}
```

**Error Response (422 Unprocessable Entity - Invalid Limit):**
```json
{
  "detail": [
    {
      "loc": ["query", "limit"],
      "msg": "ensure this value is less than or equal to 20",
      "type": "value_error.number.not_le",
      "ctx": { "limit_value": 20 }
    }
  ]
}
```

---

## 🤖 Agent API

### 1. Ask a Question (RAG Pipeline)
Submit a natural language question to be processed by the RAG (Retrieval-Augmented Generation) pipeline. The system queries the knowledge base using semantic search, filters results using the similarity threshold, constructs a prompt grounded in the relevant context, and calls Grok to generate an answer.

**Request:**
```bash
curl -X POST "http://127.0.0.1:8000/agent/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How do I reset my password?"
  }'
```

**Success Response (200 OK - Answer Found):**
```json
{
  "answer": "To reset your password:\n\n1. Go to the TeamFlow login page at app.teamflow.io/login.\n2. Click **Forgot your password?** below the sign-in form.\n3. Enter your registered email address and click **Send Reset Link**.\n4. Check your inbox for an email from noreply@teamflow.io (it may take up to 2 minutes).\n5. Click the reset link in the email (valid for 30 minutes).\n6. Enter and confirm your new password, then click **Reset Password**.\n7. Sign in with your new password on the login page.\n\nIf you don't see the email, check your Spam/Junk folder. Expired links can be replaced by requesting a new one.",
  "sources": [
    "password-reset-and-login-issues",
    "api-rate-limits-and-authentication"
  ]
}
```

**Success Response (200 OK - Fallback Answer / Below Threshold):**
If no knowledge base chunks meet the similarity threshold configured via `RAG_SIMILARITY_THRESHOLD` (e.g. 0.75), the agent will return the configured fallback answer.

**Request:**
```bash
curl -X POST "http://127.0.0.1:8000/agent/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the capital of France?"
  }'
```

**Response:**
```json
{
  "answer": "I'm sorry, I couldn't find relevant information in the knowledge base to answer your question. You may need to submit a support ticket for further assistance.",
  "sources": []
}
```

**Error Response (422 Unprocessable Entity - Empty or Whitespace-only Question):**
The request body is validated to ensure that the question is neither empty nor consists solely of whitespace.

**Request:**
```bash
curl -X POST "http://127.0.0.1:8000/agent/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "   "
  }'
```

**Response:**
```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": [
        "body",
        "question"
      ],
      "msg": "Value error, Question cannot be empty or consist only of whitespace.",
      "input": "   "
    }
  ]
}
```

### 2. Stateful Conversation (Memory & Persistence)
To maintain conversation history across multiple requests, include a `thread_id` in your request body. The agent will use this to recall prior context, and the history is safely persisted in the PostgreSQL database so it survives server restarts.

**Request (First Turn):**
```bash
curl -X POST "http://127.0.0.1:8000/agent/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the refund policy?",
    "thread_id": "user-session-123"
  }'
```

**Request (Follow-up Turn):**
```bash
curl -X POST "http://127.0.0.1:8000/agent/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Could you explain that shorter?",
    "thread_id": "user-session-123"
  }'
```
*(The agent will automatically rewrite the follow-up question into a standalone query—e.g., "Could you explain the refund policy shorter?"—using the conversation history before retrieving context, ensuring highly accurate answers.)*

