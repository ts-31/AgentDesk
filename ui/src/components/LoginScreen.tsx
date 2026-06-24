import { ArrowRight, EyeOff, Eye, Lock, Mail, Loader2 } from 'lucide-react';
import { motion } from 'motion/react';
import { useState } from 'react';
import { useAuth } from '../context/AuthContext';

export default function LoginScreen() {
  const { login } = useAuth();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);
  const [isLoggingIn, setIsLoggingIn] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoggingIn(true);
    try {
      await login(email, password);
      // AuthContext sets isLoggedIn → App re-renders to SupportScreen.
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed. Please try again.');
    } finally {
      setIsLoggingIn(false);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen relative overflow-hidden bg-background px-6">
      {/* Background glow */}
      <div className="fixed inset-0 pointer-events-none opacity-40">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-primary opacity-5 rounded-full blur-[120px]"></div>
        <div className="absolute bottom-[-10%] right-[-10%] w-[30%] h-[30%] bg-tertiary-container opacity-5 rounded-full blur-[100px]"></div>
      </div>

      <motion.main 
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="relative z-10 w-full max-w-[420px]"
      >
        {/* Brand Header */}
        <div className="flex flex-col items-center mb-10">
          <div className="mb-6">
            <img 
              alt="AgentDesk AI Logo" 
              src="https://lh3.googleusercontent.com/aida/AP1WRLvtCSXWB2MznQZ1Q35xQfWAhQdMCzNiDlv048gWjvgjJvGXa6w8Qd3DMrTHgdRYu9L3lvr5jQgOvtgy0R-tsq7K88hyHQms2y8KLXHrVMXZ3aqX-5O85f3dBjeYxXDsA-IzljhV2brgQ7OlUsYl5QzgtzlMDgDAwjce6RC0obL7QYPY-R-2d55U-0mnTt6K1NOeMwHZCf5HwEfLruMwyzsijw4dDOY7QkAY8VztZXGNA3hTXseOwF0Sdyz6"
              className="h-12 w-auto object-contain transition-transform hover:scale-105 duration-300"
            />
          </div>
          <div className="text-center space-y-1">
            <h1 className="text-2xl font-medium tracking-tight text-on-surface">Welcome back</h1>
            <p className="text-sm text-on-surface-variant">Access your team dashboard and insights</p>
          </div>
        </div>

        {/* Login Card */}
        <div className="bg-surface-container-low border border-outline-variant/30 rounded-xl p-8 shadow-2xl">
          <form className="space-y-6" onSubmit={handleSubmit}>
            {/* Email */}
            <div className="space-y-2">
              <label className="text-xs font-semibold text-outline uppercase tracking-widest block">
                Email Address
              </label>
              <div className="relative group">
                <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-outline-variant transition-colors group-focus-within:text-primary" />
                <input 
                  type="email" 
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="name@company.com"
                  className="w-full bg-background border border-outline-variant/40 rounded-lg py-3 pl-12 pr-4 text-sm text-on-surface placeholder:text-outline-variant/60 focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary transition-all duration-200"
                />
              </div>
            </div>

            {/* Password */}
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <label className="text-xs font-semibold text-outline uppercase tracking-widest block">
                  Password
                </label>
                <a href="#" className="text-[10px] font-semibold text-primary hover:text-primary-container transition-colors uppercase tracking-wider">
                  Forgot?
                </a>
              </div>
              <div className="relative group">
                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-outline-variant transition-colors group-focus-within:text-primary" />
                <input 
                  type={showPassword ? 'text' : 'password'}
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full bg-background border border-outline-variant/40 rounded-lg py-3 pl-12 pr-12 text-sm text-on-surface placeholder:text-outline-variant/60 focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary transition-all duration-200"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-4 top-1/2 -translate-y-1/2 text-outline-variant hover:text-on-surface transition-colors"
                >
                  {showPassword ? <Eye className="w-5 h-5" /> : <EyeOff className="w-5 h-5" />}
                </button>
              </div>
            </div>

            {/* Remember Me Toggle */}
            <div 
              className="flex items-center gap-2 cursor-pointer select-none"
              onClick={() => setRememberMe(!rememberMe)}
            >
              <div className={`w-8 h-4 rounded-full relative transition-colors duration-200 ${rememberMe ? 'bg-primary' : 'bg-outline-variant/30'}`}>
                <div className={`absolute left-0.5 top-0.5 w-3 h-3 bg-white rounded-full transition-transform duration-200 transform ${rememberMe ? 'translate-x-4' : ''}`}></div>
              </div>
              <span className="text-sm text-on-surface-variant">Remember this device</span>
            </div>

            {/* Inline Error */}
            {error && (
              <motion.p
                initial={{ opacity: 0, y: -4 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-sm text-error text-center"
              >
                {error}
              </motion.p>
            )}

            {/* Submit Button */}
            <button 
              type="submit" 
              disabled={isLoggingIn}
              className="w-full bg-primary hover:bg-primary-container text-on-primary py-3 rounded-lg text-xs font-semibold tracking-widest uppercase transition-all duration-300 flex justify-center items-center gap-2 group disabled:opacity-80"
            >
              {isLoggingIn ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Validating...
                </>
              ) : (
                <>
                  Sign In
                  <ArrowRight className="w-[18px] h-[18px] group-hover:translate-x-1 transition-transform" />
                </>
              )}
            </button>
          </form>

          {/* Social SSO */}
          <div className="relative my-8">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-outline-variant/20"></div>
            </div>
            <div className="relative flex justify-center text-[10px] font-semibold uppercase tracking-[0.2em]">
              <span className="bg-surface-container-low px-4 text-outline">or continue with</span>
            </div>
          </div>

          <button className="w-full border border-outline-variant/40 hover:bg-surface-container-highest/50 py-3 rounded-lg text-sm text-on-surface transition-all duration-200 flex justify-center items-center gap-2">
            <svg className="w-4 h-4" viewBox="0 0 24 24">
              <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="currentColor"></path>
              <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="currentColor"></path>
              <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="currentColor"></path>
              <path d="M12 5.38c1.62 0 3.06.56 4.21 1.66l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="currentColor"></path>
            </svg>
            Google Single Sign-On
          </button>
        </div>

        {/* Footer */}
        <footer className="mt-8 flex justify-between items-center px-1">
          <p className="text-sm text-outline-variant">
            New here? <a href="#" className="text-primary hover:underline underline-offset-4">Create account</a>
          </p>
          <div className="flex gap-4">
            <a href="#" className="text-[10px] font-semibold text-outline-variant hover:text-on-surface uppercase tracking-wider transition-colors">Help</a>
            <a href="#" className="text-[10px] font-semibold text-outline-variant hover:text-on-surface uppercase tracking-wider transition-colors">Privacy</a>
          </div>
        </footer>
      </motion.main>
    </div>
  );
}
