import { Sparkles, CheckCircle2, AlertTriangle, Book, FileText, BarChart, ThumbsUp, ThumbsDown, Copy, Paperclip, Send, Search, Bot } from 'lucide-react';
import { motion } from 'motion/react';
import { useState, useRef, useEffect } from 'react';

// Type alias
type Message = {
  id: string;
  role: 'user' | 'ai';
  text: string;
  timestamp: string;
};

export default function SupportScreen() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'user',
      text: 'Can you summarize the status of Project Alpha and list any recent blockers?',
      timestamp: '10:24 AM'
    },
    {
      id: '2',
      role: 'ai',
      text: 'fake_body_to_render_rich',
      timestamp: '10:24 AM'
    }
  ]);
  const [inputText, setInputText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  const handleSend = () => {
    if (!inputText.trim()) return;
    
    const newUserMsg: Message = {
      id: Date.now().toString(),
      role: 'user',
      text: inputText,
      timestamp: 'JUST NOW'
    };

    setMessages((prev) => [...prev, newUserMsg]);
    setInputText('');
    setIsTyping(true);

    setTimeout(() => {
      const newAiMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: 'ai',
        text: 'I have logged this information for you. Is there anything else you need assistance with today?',
        timestamp: 'JUST NOW'
      };
      setMessages((prev) => [...prev, newAiMsg]);
      setIsTyping(false);
    }, 2000);
  };

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  return (
    <div className="flex flex-col min-h-screen relative bg-background mt-16">
      {/* Top Header */}
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
        <div className="flex items-center gap-4">
          <button className="flex items-center justify-center p-2 rounded-lg hover:bg-surface-container-high transition-colors">
            <Search className="w-5 h-5 text-on-surface-variant" />
          </button>
          <div className="relative group">
            <div className="w-8 h-8 rounded-full overflow-hidden border border-primary/30 cursor-pointer ring-offset-2 ring-offset-background hover:ring-2 hover:ring-primary transition-all bg-gradient-to-tr from-surface-container to-surface-container-high shadow-[inset_0_0_8px_rgba(192,193,255,0.2)] flex items-center justify-center">
              <Bot className="w-4 h-4 text-primary" />
            </div>
          </div>
        </div>
      </header>

      <main className="flex-1 flex flex-col items-center w-full px-6 pb-32">
        {/* Welcome Hero */}
        <section className="w-full max-w-3xl text-center py-12 mt-4">
          <h1 className="text-4xl md:text-5xl font-semibold tracking-tight text-on-surface mb-3">
            How can we help you today?
          </h1>
          <p className="text-base text-on-surface-variant opacity-80">
            Ask anything about your team's workflow, resource allocation, or project analytics.
          </p>
        </section>

        {/* Chat History */}
        <section className="w-full max-w-3xl flex flex-col gap-6">
          {messages.map((msg, index) => {
            const isUser = msg.role === 'user';

            return (
              <motion.div 
                key={msg.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
                className={`flex flex-col ${isUser ? 'items-end' : 'items-start'} gap-2`}
              >
                {!isUser && (
                  <div className="flex items-center gap-2 mb-1">
                    <div className="w-6 h-6 bg-primary/20 rounded flex items-center justify-center">
                      <Sparkles className="w-4 h-4 text-primary fill-current" />
                    </div>
                    <span className="text-[12px] font-semibold text-primary uppercase tracking-wider">
                      TeamFlow AI
                    </span>
                  </div>
                )}

                <div 
                  className={`
                    px-4 py-3 rounded-xl max-w-[85%] sm:max-w-[95%] border text-sm
                    ${isUser 
                      ? 'bg-secondary-container text-on-secondary-container rounded-tr-sm border-[rgba(255,255,255,0.08)]' 
                      : 'bg-surface-container border-outline-variant rounded-tl-sm text-on-surface'
                    }
                  `}
                >
                  {isUser ? (
                    <p className="leading-relaxed">{msg.text}</p>
                  ) : (
                    msg.id === '2' ? (
                      // Render rich initial response
                      <div className="flex flex-col">
                        <p className="leading-relaxed mb-4 text-on-surface">
                          Project Alpha is currently at <strong>68% completion</strong>. The timeline has shifted by 4 days due to delays in the API integration phase.
                        </p>
                        <ul className="space-y-2 mb-4">
                          <li className="flex items-start gap-2">
                            <CheckCircle2 className="w-[18px] h-[18px] text-primary shrink-0 mt-[2px]" />
                            <span className="text-on-surface-variant">Frontend design audit completed on Tuesday.</span>
                          </li>
                          <li className="flex items-start gap-2">
                            <AlertTriangle className="w-[18px] h-[18px] text-error shrink-0 mt-[2px]" />
                            <span className="text-on-surface-variant">Blocker: Auth module pending security review from the DevOps team.</span>
                          </li>
                        </ul>
                        
                        <div className="mt-6 pt-4 border-t border-outline-variant/30">
                          <div className="flex items-center gap-1 mb-2">
                            <Book className="w-3.5 h-3.5 text-outline" />
                            <span className="text-[10px] font-semibold text-outline uppercase tracking-wider">Sources</span>
                          </div>
                          <div className="flex flex-wrap gap-2">
                            <a href="#" className="flex items-center gap-1.5 bg-surface-container-highest px-2 py-1.5 rounded border border-outline-variant hover:border-primary transition-colors">
                              <FileText className="w-3 h-3 text-primary" />
                              <span className="font-mono text-[11px] text-on-surface-variant">alpha-spec-v2.pdf</span>
                            </a>
                            <a href="#" className="flex items-center gap-1.5 bg-surface-container-highest px-2 py-1.5 rounded border border-outline-variant hover:border-primary transition-colors">
                              <BarChart className="w-3 h-3 text-primary" />
                              <span className="font-mono text-[11px] text-on-surface-variant">q3-roadmap-board</span>
                            </a>
                          </div>
                        </div>
                      </div>
                    ) : (
                      // Render dynamic responses
                      <p className="leading-relaxed">{msg.text}</p>
                    )
                  )}
                </div>

                {isUser ? (
                  <span className="text-[10px] font-semibold text-outline-variant mr-1">
                    {msg.timestamp}
                  </span>
                ) : (
                  <div className="flex gap-4 mt-1 ml-1">
                    <button className="group flex items-center">
                      <ThumbsUp className="w-[18px] h-[18px] text-outline group-hover:text-primary transition-colors" />
                    </button>
                    <button className="group flex items-center">
                      <ThumbsDown className="w-[18px] h-[18px] text-outline group-hover:text-error transition-colors" />
                    </button>
                    <button className="group flex items-center">
                      <Copy className="w-[18px] h-[18px] text-outline group-hover:text-primary transition-colors" />
                    </button>
                  </div>
                )}
              </motion.div>
            );
          })}

          {isTyping && (
            <div className="flex items-center gap-1.5 ml-4 py-2">
              <div className="w-1.5 h-1.5 bg-primary rounded-full animate-bounce"></div>
              <div className="w-1.5 h-1.5 bg-primary rounded-full animate-bounce delay-150"></div>
              <div className="w-1.5 h-1.5 bg-primary rounded-full animate-bounce delay-300"></div>
            </div>
          )}
          <div ref={bottomRef} />
        </section>
      </main>

      {/* Input Footer */}
      <footer className="fixed bottom-0 left-0 right-0 p-6 flex justify-center bg-gradient-to-t from-background via-background/90 to-transparent pointer-events-none">
        <div className="w-full max-w-3xl pointer-events-auto">
          <div className="relative bg-surface-container border border-outline-variant rounded-xl shadow-2xl focus-within:border-primary focus-within:ring-1 focus-within:ring-primary transition-all group overflow-hidden">
            <textarea 
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSend();
                }
              }}
              placeholder="Ask a follow-up or provide context..."
              rows={1}
              className="w-full bg-transparent border-none text-on-surface placeholder:text-outline-variant/60 focus:ring-0 py-4 px-6 resize-none text-sm min-h-[56px] pr-28 outline-none"
              style={{ overflow: 'hidden' }}
            />
            <div className="absolute right-4 bottom-3 flex items-center gap-2">
              <button className="p-1.5 text-outline-variant hover:text-primary transition-colors">
                <Paperclip className="w-5 h-5" />
              </button>
              <button 
                onClick={handleSend}
                disabled={!inputText.trim()}
                className="bg-primary hover:bg-primary-container disabled:bg-surface-variant disabled:text-outline text-on-primary w-8 h-8 rounded-lg flex items-center justify-center transition-all active:scale-95 shadow-lg shadow-primary/20"
              >
                <Send className="w-[18px] h-[18px] fill-current" />
              </button>
            </div>
            {/* Subtle top glow highlight */}
            <div className="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-primary/30 to-transparent"></div>
          </div>
          <p className="text-center mt-3 text-[10px] font-semibold text-outline-variant/60 uppercase tracking-widest">
            AI can make mistakes. Verify important information.
          </p>
        </div>
      </footer>
    </div>
  );
}
