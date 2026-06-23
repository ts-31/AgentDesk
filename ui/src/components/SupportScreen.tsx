import { Send, Loader2, LogOut, Bot } from 'lucide-react';
import { motion } from 'motion/react';
import { useState, useRef, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { askAgent } from '../api/agent';

type Message = {
  id: string;
  role: 'user' | 'ai';
  text: string;
};

export default function SupportScreen() {
  const { logout } = useAuth();

  // One stable thread_id per login session.
  const threadId = useRef<string>(crypto.randomUUID());

  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  const handleSend = async () => {
    const question = inputText.trim();
    if (!question || isTyping) return;

    const userMsg: Message = {
      id: crypto.randomUUID(),
      role: 'user',
      text: question,
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputText('');
    setIsTyping(true);

    try {
      const answer = await askAgent(question, threadId.current);
      setMessages((prev) => [
        ...prev,
        { id: crypto.randomUUID(), role: 'ai', text: answer },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          role: 'ai',
          text: 'Something went wrong. Please try again.',
        },
      ]);
    } finally {
      setIsTyping(false);
    }
  };

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  return (
    <div className="flex flex-col min-h-screen bg-background">
      {/* Fixed header */}
      <header className="fixed top-0 left-0 right-0 z-50 glass-blur border-b border-outline-variant h-16 px-6 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <img
            alt="TeamFlow Logo"
            src="https://lh3.googleusercontent.com/aida/AP1WRLvtCSXWB2MznQZ1Q35xQfWAhQdMCzNiDlv048gWjvgjJvGXa6w8Qd3DMrTHgdRYu9L3lvr5jQgOvtgy0R-tsq7K88hyHQms2y8KLXHrVMXZ3aqX-5O85f3dBjeYxXDsA-IzljhV2brgQ7OlUsYl5QzgtzlMDgDAwjce6RC0obL7QYPY-R-2d55U-0mnTt6K1NOeMwHZCf5HwEfLruMwyzsijw4dDOY7QkAY8VztZXGNA3hTXseOwF0Sdyz6"
            className="h-8 w-auto"
          />
          <div className="h-4 w-[1px] bg-outline-variant mx-2"></div>
          <span className="text-[12px] font-semibold text-outline-variant tracking-widest uppercase">
            Support Assistant
          </span>
        </div>

        <div className="flex items-center gap-3">
          {/* User avatar pill */}
          <div className="w-8 h-8 rounded-full border border-primary/30 bg-gradient-to-tr from-surface-container to-surface-container-high shadow-[inset_0_0_8px_rgba(192,193,255,0.2)] flex items-center justify-center">
            <Bot className="w-4 h-4 text-primary" />
          </div>

          {/* Logout */}
          <button
            onClick={logout}
            title="Sign out"
            className="p-2 rounded-lg text-outline-variant hover:text-error hover:bg-surface-container-high transition-colors"
          >
            <LogOut className="w-5 h-5" />
          </button>
        </div>
      </header>

      {/* Scrollable message area */}
      <main className="flex-1 flex flex-col items-center w-full px-4 pt-24 pb-36">
        {/* Empty state */}
        {messages.length === 0 && !isTyping && (
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
            className="mt-16 text-center"
          >
            <h1 className="text-3xl font-semibold tracking-tight text-on-surface mb-2">
              How can I help you?
            </h1>
            <p className="text-sm text-on-surface-variant opacity-70">
              Ask anything about your team's workflow, projects, or data.
            </p>
          </motion.div>
        )}

        {/* Messages */}
        <div className="w-full max-w-2xl flex flex-col gap-4">
          {messages.map((msg) => {
            const isUser = msg.role === 'user';
            return (
              <motion.div
                key={msg.id}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.25 }}
                className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`
                    px-4 py-3 rounded-2xl max-w-[80%] text-sm leading-relaxed
                    ${isUser
                      ? 'bg-secondary-container text-on-secondary-container rounded-tr-sm'
                      : 'bg-surface-container border border-outline-variant/40 text-on-surface rounded-tl-sm'
                    }
                  `}
                >
                  {msg.text}
                </div>
              </motion.div>
            );
          })}

          {/* Typing indicator */}
          {isTyping && (
            <div className="flex justify-start">
              <div className="bg-surface-container border border-outline-variant/40 px-4 py-3 rounded-2xl rounded-tl-sm flex items-center gap-1.5">
                <div className="w-1.5 h-1.5 bg-primary rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                <div className="w-1.5 h-1.5 bg-primary rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                <div className="w-1.5 h-1.5 bg-primary rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
              </div>
            </div>
          )}

          <div ref={bottomRef} />
        </div>
      </main>

      {/* Fixed input footer */}
      <footer className="fixed bottom-0 left-0 right-0 p-4 flex justify-center bg-gradient-to-t from-background via-background/95 to-transparent pointer-events-none">
        <div className="w-full max-w-2xl pointer-events-auto">
          <div className="relative bg-surface-container border border-outline-variant rounded-xl shadow-2xl focus-within:border-primary focus-within:ring-1 focus-within:ring-primary transition-all overflow-hidden">
            {/* Top glow line */}
            <div className="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-primary/30 to-transparent"></div>

            <textarea
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSend();
                }
              }}
              placeholder="Ask a question..."
              rows={1}
              disabled={isTyping}
              className="w-full bg-transparent border-none text-on-surface placeholder:text-outline-variant/60 focus:ring-0 py-4 px-5 resize-none text-sm min-h-[56px] pr-16 outline-none disabled:opacity-60"
              style={{ overflow: 'hidden' }}
            />

            <div className="absolute right-3 bottom-3">
              <button
                onClick={handleSend}
                disabled={!inputText.trim() || isTyping}
                className="bg-primary hover:bg-primary-container disabled:bg-surface-variant disabled:text-outline text-on-primary w-9 h-9 rounded-lg flex items-center justify-center transition-all active:scale-95 shadow-lg shadow-primary/20"
              >
                {isTyping ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Send className="w-[18px] h-[18px] fill-current" />
                )}
              </button>
            </div>
          </div>

          <p className="text-center mt-2 text-[10px] font-semibold text-outline-variant/50 uppercase tracking-widest">
            AI can make mistakes. Verify important information.
          </p>
        </div>
      </footer>
    </div>
  );
}
