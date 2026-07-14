import React, { useState, useRef, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { RootState, AppDispatch } from '../store';
import { addMessage, sendMessage, clearChat } from '../store/chatSlice';
import { resetForm } from '../store/formSlice';
import { motion, AnimatePresence } from 'motion/react';
import { Bot, Trash2, Sparkles } from 'lucide-react';

const ChatInterface: React.FC = () => {
  const [input, setInput] = useState('');
  const dispatch = useDispatch<AppDispatch>();
  const { messages, isLoading } = useSelector((state: RootState) => state.chat);
  const chatEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const text = input.trim();
    setInput('');
    dispatch(addMessage({ role: 'user', content: text }));
    dispatch(sendMessage(text));
  };

  return (
    <div className="flex flex-col h-full bg-white">
      <header className="px-8 py-6 border-b border-slate-100 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="w-10 h-10 rounded-xl bg-brand-primary flex items-center justify-center text-white shadow-lg shadow-brand-primary/20">
            <Bot className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-base font-bold text-slate-900 font-display">Interaction Assistant</h2>
            <div className="flex items-center gap-2">
              <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
              <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Active Intelligence</p>
            </div>
          </div>
        </div>
        <button
          onClick={() => {
            dispatch(clearChat());
            dispatch(resetForm());
          }}
          className="p-2 text-slate-300 hover:text-rose-500 transition-colors rounded-lg hover:bg-rose-50"
          title="Reset Environment"
        >
          <Trash2 className="w-5 h-5" />
        </button>
      </header>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-8 py-6 space-y-6 bg-slate-50/30">
        {/* Instruction Bubble */}
        <div className="flex justify-start">
          <div className="max-w-[90%] px-5 py-4 bg-white text-slate-600 text-sm rounded-2xl border border-slate-100 shadow-sm leading-relaxed">
            <p className="font-medium text-slate-400 mb-1 uppercase text-[10px] tracking-widest">Guide</p>
            Describe your interaction (e.g., <span className="text-brand-primary">"Met Dr. Smith, discussed efficacy, shared brochure"</span>) to automatically populate the engagement log.
          </div>
        </div>

        <AnimatePresence initial={false}>
          {messages.map((m, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div className={`max-w-[85%] px-5 py-4 rounded-2xl text-sm shadow-sm transition-all ${
                m.role === 'user'
                  ? 'bg-slate-900 text-white shadow-slate-200'
                  : m.content.includes('logged successfully')
                    ? 'bg-emerald-50 text-emerald-900 border border-emerald-100'
                    : 'bg-white text-slate-700 border border-slate-100'
              }`}>
                <div className="whitespace-pre-wrap leading-relaxed">
                  {m.content}
                </div>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
        
        {isLoading && (
          <div className="flex justify-start">
            <div className="flex items-center gap-2 px-5 py-3 bg-white rounded-2xl border border-slate-100 shadow-sm">
              <div className="flex gap-1">
                <div className="w-1.5 h-1.5 bg-brand-primary rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                <div className="w-1.5 h-1.5 bg-brand-primary rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                <div className="w-1.5 h-1.5 bg-brand-primary rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
              </div>
              <span className="text-xs font-bold text-slate-400 uppercase tracking-widest ml-2">Extracting Details</span>
            </div>
          </div>
        )}
        <div ref={chatEndRef} />
      </div>

      {/* Input */}
      <div className="p-8 bg-white border-t border-slate-100">
        <form onSubmit={handleSubmit} className="relative">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Log interaction details..."
            rows={2}
            className="w-full pl-6 pr-16 py-5 bg-slate-50 border-none rounded-2xl text-sm focus:ring-2 focus:ring-brand-primary/10 transition-all placeholder:text-slate-400 resize-none font-medium text-slate-900"
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSubmit(e);
              }
            }}
          />
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="absolute right-3 bottom-3 w-10 h-10 bg-brand-primary text-white rounded-xl flex items-center justify-center hover:bg-brand-secondary disabled:opacity-30 transition-all shadow-lg shadow-brand-primary/20 group"
          >
            <Sparkles className="w-5 h-5 group-hover:rotate-12 transition-transform" />
          </button>
        </form>
        <p className="text-center mt-4 text-[10px] text-slate-400 font-bold uppercase tracking-[0.2em]">Clinical Scribe v2.4</p>
      </div>
    </div>
  );
};

export default ChatInterface;
