/**
 * AuthContext.tsx — Global session state for AgentDesk.
 *
 * Provides:
 *   isLoggedIn  — true if a valid access_token exists in localStorage.
 *   login()     — calls api/auth.ts → login(), then sets isLoggedIn = true.
 *   logout()    — calls api/auth.ts → logout(), then sets isLoggedIn = false.
 *
 * Also listens for the "auth:logout" CustomEvent dispatched by api/client.ts
 * when a silent token refresh fails (access + refresh both expired/invalid).
 */

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from 'react';
import { login as apiLogin, logout as apiLogout } from '../api/auth';
import { getAccessToken } from '../api/client';

interface AuthContextValue {
  isLoggedIn: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  // Initialise from localStorage so a page refresh restores the session.
  const [isLoggedIn, setIsLoggedIn] = useState<boolean>(
    () => getAccessToken() !== null,
  );

  const login = useCallback(async (email: string, password: string) => {
    await apiLogin(email, password); // throws on failure
    setIsLoggedIn(true);
  }, []);

  const logout = useCallback(async () => {
    await apiLogout();
    setIsLoggedIn(false);
  }, []);

  // Listen for the auto-logout event fired by the API client when both
  // access and refresh tokens are expired or invalid.
  useEffect(() => {
    const handleAutoLogout = () => {
      setIsLoggedIn(false);
    };
    window.addEventListener('auth:logout', handleAutoLogout);
    return () => window.removeEventListener('auth:logout', handleAutoLogout);
  }, []);

  return (
    <AuthContext.Provider value={{ isLoggedIn, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

/** Hook — must be used inside <AuthProvider>. */
export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error('useAuth must be used within an <AuthProvider>');
  }
  return ctx;
}
