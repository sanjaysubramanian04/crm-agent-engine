import React from 'react';
import { useSelector } from 'react-redux';
import { RootState } from '../store';
import InteractionForm from './InteractionForm';
import ChatInterface from './ChatInterface';
import { motion, AnimatePresence } from 'motion/react';
import { ClipboardList, Bot, Sparkles } from 'lucide-react';

const Dashboard: React.FC = () => {
  const nextBestAction = useSelector((state: RootState) => state.form.nextBestAction);

  return (
    <div className="flex h-screen bg-background-soft overflow-hidden">
      {/* Left Column: Form & Analysis */}
      <div className="w-[60%] flex flex-col overflow-y-auto">
        <div className="flex-1 p-0">
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5 }}
          >
            <InteractionForm />
          </motion.div>
          
          <AnimatePresence>
            {nextBestAction && (
              <div className="px-14 pb-12">
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, scale: 0.95 }}
                  className="glass-card p-8"
                >
                  <div className="flex items-center gap-3 mb-6">
                    <div className="w-10 h-10 rounded-xl bg-brand-primary/10 flex items-center justify-center text-brand-primary">
                      <Bot className="w-5 h-5" />
                    </div>
                    <div>
                      <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider">AI Insights</h3>
                      <p className="text-xs text-slate-500 font-medium">Recommended Clinical Next Steps</p>
                    </div>
                  </div>

                  <div className="prose prose-sm max-w-none text-slate-600">
                    <div className="whitespace-pre-wrap leading-relaxed font-sans">
                      {nextBestAction}
                    </div>
                  </div>
                </motion.div>
              </div>
            )}
          </AnimatePresence>
        </div>
      </div>

      {/* Right Column: Chat Interface */}
      <div className="w-[40%] shrink-0 shadow-[-10px_0_30px_-15px_rgba(0,0,0,0.1)] z-10 border-l border-slate-200">
        <ChatInterface />
      </div>
    </div>
  );
};

export default Dashboard;
