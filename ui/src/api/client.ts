/**
 * client.ts — Auth-aware fetch wrapper for TeamFlow.
 *
 * Every request:
 *   1. Prepends VITE_API_BASE_URL to the path.
 *   2. Attaches "Authorization: Bearer <access_token>" from localStorage.
 *   3. On 401: silently attempts one token refresh via POST /auth/refresh.
 *      - Success → saves new access_token, retries the original request.
 *      - Failure → clears localStorage, dispatches "auth:logout" event.
 */

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '/api';

const TOKEN_KEY = 'access_token';
const REFRESH_KEY = 'refresh_token';

export function getAccessToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function getRefreshToken(): string | null {
  return localStorage.getItem(REFRESH_KEY);
}

export function saveTokens(accessToken: string, refreshToken: string): void {
  localStorage.setItem(TOKEN_KEY, accessToken);
  localStorage.setItem(REFRESH_KEY, refreshToken);
}

export function clearTokens(): void {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(REFRESH_KEY);
}

/** Fire a global logout event — AuthContext listens to this. */
function dispatchLogout(): void {
  window.dispatchEvent(new CustomEvent('auth:logout'));
}

/** Attempt a silent token refresh. Returns true on success. */
async function tryRefresh(): Promise<boolean> {
  const refreshToken = getRefreshToken();
  if (!refreshToken) return false;

  try {
    const res = await fetch(`${BASE_URL}/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });

    if (!res.ok) return false;

    const data = await res.json();
    saveTokens(data.access_token, data.refresh_token);
    return true;
  } catch {
    return false;
  }
}

/** Build headers with the current access token. */
function authHeaders(extra?: HeadersInit): HeadersInit {
  const token = getAccessToken();
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...extra,
  };
}

/**
 * Main API client. Behaves like fetch but handles auth automatically.
 *
 * Usage:
 *   const res = await apiClient('/agent/ask', { method: 'POST', body: JSON.stringify({...}) });
 */
export async function apiClient(
  path: string,
  init: RequestInit = {},
): Promise<Response> {
  const url = `${BASE_URL}${path}`;

  // First attempt
  const res = await fetch(url, {
    ...init,
    headers: authHeaders(init.headers),
  });

  if (res.status !== 401) return res;

  // 401 — try silent refresh
  const refreshed = await tryRefresh();

  if (!refreshed) {
    clearTokens();
    dispatchLogout();
    return res; // return the 401 so callers can react if needed
  }

  // Retry with the new access token
  const retryRes = await fetch(url, {
    ...init,
    headers: authHeaders(init.headers),
  });

  if (retryRes.status === 401) {
    // Refresh token itself is invalid/expired
    clearTokens();
    dispatchLogout();
  }

  return retryRes;
}
