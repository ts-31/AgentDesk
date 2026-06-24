"""
cli_chat.py — AgentDesk CLI chatbot with JWT authentication.

Flow:
  1. Prompt for email and password on startup.
  2. POST /auth/login — store access_token + refresh_token in memory.
  3. Each /agent/ask request sends Authorization: Bearer <access_token>.
  4. On 401 response — automatically attempt POST /auth/refresh once.
     If refresh succeeds, retry the original request with the new token.
     If refresh also fails, prompt the user to log in again.
  5. On exit/quit — call POST /auth/logout (best-effort) and exit.

Tokens are stored only in memory (session-scoped variables).
Nothing is written to disk, no keychain, no .env.
"""

import getpass
import sys
import uuid

import requests

BASE_URL = "http://localhost:8000"
LOGIN_URL  = f"{BASE_URL}/auth/login"
REFRESH_URL = f"{BASE_URL}/auth/refresh"
LOGOUT_URL  = f"{BASE_URL}/auth/logout"
ASK_URL    = f"{BASE_URL}/agent/ask"

# In-memory token store — lives only for this process.
_session: dict[str, str | None] = {
    "access_token": None,
    "refresh_token": None,
}


# ---------------------------------------------------------------------------
# Auth helpers
# ---------------------------------------------------------------------------

def _login(email: str, password: str) -> bool:
    """
    Call POST /auth/login.  Stores tokens in _session on success.
    Returns True on success, False on failure.
    """
    try:
        resp = requests.post(LOGIN_URL, json={"email": email, "password": password}, timeout=10)
    except requests.exceptions.ConnectionError:
        print("\n❌ [Error] Could not connect to the server. Make sure your FastAPI backend is running on http://localhost:8000")
        return False

    if resp.status_code == 200:
        data = resp.json()
        _session["access_token"]  = data["access_token"]
        _session["refresh_token"] = data["refresh_token"]
        return True
    elif resp.status_code == 401:
        print("\n❌ Incorrect email or password. Please try again.")
        return False
    else:
        print(f"\n❌ [Error] Login failed with status {resp.status_code}: {resp.text}")
        return False


def _refresh_access_token() -> bool:
    """
    Call POST /auth/refresh with the stored refresh token.
    Updates _session["access_token"] on success.
    Returns True on success, False if the refresh token is also expired/invalid.
    """
    refresh_token = _session.get("refresh_token")
    if not refresh_token:
        return False

    try:
        resp = requests.post(REFRESH_URL, json={"refresh_token": refresh_token}, timeout=10)
    except requests.exceptions.ConnectionError:
        return False

    if resp.status_code == 200:
        _session["access_token"] = resp.json()["access_token"]
        return True
    return False


def _logout() -> None:
    """Call POST /auth/logout (best-effort — ignore failures)."""
    try:
        requests.post(
            LOGOUT_URL,
            headers={"Authorization": f"Bearer {_session['access_token']}"},
            timeout=5,
        )
    except Exception:
        pass
    _session["access_token"]  = None
    _session["refresh_token"] = None


# ---------------------------------------------------------------------------
# Agent communication
# ---------------------------------------------------------------------------

def _ask_agent(question: str, thread_id: str) -> dict | None:
    """
    POST /agent/ask with the current access token.
    Automatically attempts one token refresh on 401.

    Returns the parsed JSON dict on success, or None on failure.
    """
    headers = {"Authorization": f"Bearer {_session['access_token']}"}
    payload = {"question": question, "thread_id": thread_id}

    try:
        resp = requests.post(ASK_URL, json=payload, headers=headers, timeout=60)
    except requests.exceptions.ConnectionError:
        print("\n❌ [Error] Could not connect to the server.")
        return None

    # Token expired — try a silent refresh then retry once.
    if resp.status_code == 401:
        print("\n🔄 Session expired. Refreshing token...")
        if _refresh_access_token():
            headers["Authorization"] = f"Bearer {_session['access_token']}"
            try:
                resp = requests.post(ASK_URL, json=payload, headers=headers, timeout=60)
            except requests.exceptions.ConnectionError:
                print("\n❌ [Error] Could not connect to the server after token refresh.")
                return None
        else:
            print("\n❌ Session could not be refreshed. Please restart and log in again.")
            return None

    if resp.status_code == 200:
        return resp.json()

    print(f"\n❌ [Error] The server returned an error: {resp.status_code} {resp.text}")
    return None


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def main() -> None:
    print("=========================================")
    print("🤖 Welcome to the AgentDesk CLI Chatbot!")
    print("=========================================")
    print("Connecting to backend on http://localhost:8000...\n")

    # --- Login loop ---
    while True:
        try:
            email    = input("Email:    ").strip()
            password = getpass.getpass("Password: ")
        except (KeyboardInterrupt, EOFError):
            print("\nExiting...")
            sys.exit(0)

        if _login(email, password):
            print(f"\n✅ Logged in as {email}")
            break
        # _login() already printed the error; loop to retry.

    # Unique thread ID scopes conversation memory for this CLI session.
    thread_id = str(uuid.uuid4())
    print(f"[Session Thread ID: {thread_id}]")
    print("Type 'exit' or 'quit' to stop.\n")

    # --- Chat loop ---
    while True:
        try:
            question = input("You: ")
        except (KeyboardInterrupt, EOFError):
            print("\nLogging out...")
            _logout()
            break

        if question.lower().strip() in ("exit", "quit"):
            print("Logging out...")
            _logout()
            break

        if not question.strip():
            continue

        data = _ask_agent(question, thread_id)
        if data is None:
            continue  # Error already printed by _ask_agent.

        print(f"\nAgentDesk Agent: {data['answer']}")

        if data.get("sources"):
            print(f"🔗 [Sources: {', '.join(data['sources'])}]")

        print()  # Blank line between turns for readability.


if __name__ == "__main__":
    main()
