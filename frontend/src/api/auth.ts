/**
 * auth.ts — Login and logout functions for TeamFlow.
 *
 * login()  → POST /auth/login, stores tokens in localStorage.
 * logout() → POST /auth/logout (fire-and-forget), clears localStorage.
 */

import { saveTokens, clearTokens } from './client';

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '/api';

export async function login(email: string, password: string): Promise<void> {
  const res = await fetch(`${BASE_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });

  if (!res.ok) {
    // Always throw the same message regardless of which field was wrong
    // (mirrors the backend's enumeration-safe 401 design).
    throw new Error('Incorrect email or password.');
  }

  const data = await res.json();
  saveTokens(data.access_token, data.refresh_token);
}

export async function logout(): Promise<void> {
  // Fire-and-forget — the backend endpoint is a no-op for stateless JWTs.
  const token = localStorage.getItem('access_token');
  if (token) {
    fetch(`${BASE_URL}/auth/logout`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` },
    }).catch(() => {/* ignore */});
  }
  clearTokens();
}
