import React from 'react';
import { useSelector } from 'react-redux';
import { RootState } from '../store';
import { Mic, Search, Calendar, Clock, ChevronDown } from 'lucide-react';
import { motion } from 'motion/react';

const InteractionForm: React.FC = () => {
  const form = useSelector((state: RootState) => state.form);

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, x: -10 },
    visible: { opacity: 1, x: 0 }
  };

  return (
    <div className="bg-background-soft min-h-screen p-8 font-sans">
      <motion.div 
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        className="max-w-4xl mx-auto glass-card overflow-hidden"
      >
        <div className="p-10">
          <div className="flex items-center justify-between mb-10">
            <div>
              <h1 className="text-3xl font-bold text-slate-900 font-display">Interaction Log</h1>
              <p className="text-slate-500 mt-1">Record and analyze HCP engagement data</p>
            </div>
            <div className="px-3 py-1 bg-brand-primary/10 text-brand-primary rounded-full text-xs font-bold uppercase tracking-wider">
              {form.id ? `Ref: #${form.id}` : 'New Entry'}
            </div>
          </div>
          
          <div className="space-y-12">
            {/* Interaction Details Section */}
            <motion.section variants={itemVariants}>
              <div className="flex items-center gap-2 mb-6">
                <div className="w-1.5 h-6 bg-brand-primary rounded-full" />
                <h2 className="text-xs font-bold text-slate-400 uppercase tracking-widest">Primary Information</h2>
              </div>
              
              <div className="grid grid-cols-2 gap-x-10 gap-y-8">
                {/* HCP Name */}
                <div className="space-y-2.5 col-span-1">
                  <label className="block text-xs font-bold text-slate-600 uppercase tracking-tight">HCP Name</label>
                  <input
                    type="text"
                    value={form.hcpName}
                    readOnly
                    placeholder="Auto-extracted..."
                    className="input-field bg-slate-50/50 cursor-default"
                  />
                </div>

                {/* Interaction Type */}
                <div className="space-y-2.5 col-span-1">
                  <label className="block text-xs font-bold text-slate-600 uppercase tracking-tight">Channel</label>
                  <div className="relative">
                    <select
                      value={form.interactionType || 'Meeting'}
                      disabled
                      className="input-field bg-slate-50/50 appearance-none cursor-not-allowed pr-10"
                    >
                      <option>Meeting</option>
                      <option>Email</option>
                      <option>Call</option>
                    </select>
                    <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                  </div>
                </div>

                {/* Date */}
                <div className="space-y-2.5 col-span-1">
                  <label className="block text-xs font-bold text-slate-600 uppercase tracking-tight">Engagement Date</label>
                  <div className="relative">
                    <input
                      type="text"
                      value={form.date}
                      readOnly
                      placeholder="Pending extraction..."
                      className="input-field bg-slate-50/50"
                    />
                    <Calendar className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                  </div>
                </div>

                {/* Time */}
                <div className="space-y-2.5 col-span-1">
                  <label className="block text-xs font-bold text-slate-600 uppercase tracking-tight">Engagement Time</label>
                  <div className="relative">
                    <input
                      type="text"
                      value={form.time}
                      readOnly
                      placeholder="Pending extraction..."
                      className="input-field bg-slate-50/50"
                    />
                    <Clock className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                  </div>
                </div>

                {/* Attendees */}
                <div className="space-y-2.5 col-span-2">
                  <label className="block text-xs font-bold text-slate-600 uppercase tracking-tight">Stakeholders & Attendees</label>
                  <input
                    type="text"
                    value={form.attendees}
                    readOnly
                    placeholder="List of participants..."
                    className="input-field bg-slate-50/50"
                  />
                </div>
              </div>
            </motion.section>

            {/* Discussion & Context */}
            <motion.section variants={itemVariants}>
              <div className="flex items-center gap-2 mb-6">
                <div className="w-1.5 h-6 bg-brand-secondary rounded-full" />
                <h2 className="text-xs font-bold text-slate-400 uppercase tracking-widest">Discussion & Sentiment</h2>
              </div>
              
              <div className="grid grid-cols-2 gap-x-10 gap-y-8">
                {/* Topics Discussed */}
                <div className="space-y-2.5 col-span-2">
                  <label className="block text-xs font-bold text-slate-600 uppercase tracking-tight">Discussion Summary</label>
                  <textarea
                    value={form.topicsDiscussed}
                    readOnly
                    placeholder="Key discussion points will appear here..."
                    className="input-field bg-slate-50/50 min-h-[120px] resize-none leading-relaxed"
                  />
                </div>

                {/* Sentiment & Outcomes */}
                <div className="space-y-2.5 col-span-1">
                  <label className="block text-xs font-bold text-slate-600 uppercase tracking-tight">HCP Sentiment</label>
                  <div className="relative">
                    <input
                      type="text"
                      value={form.sentiment}
                      readOnly
                      className={`input-field font-medium ${
                        form.sentiment?.toLowerCase().includes('positive') ? 'text-emerald-600' : 
                        form.sentiment?.toLowerCase().includes('negative') ? 'text-rose-600' : 'text-slate-600'
                      }`}
                    />
                  </div>
                </div>
                <div className="space-y-2.5 col-span-1">
                  <label className="block text-xs font-bold text-slate-600 uppercase tracking-tight">Direct Outcomes</label>
                  <input
                    type="text"
                    value={form.outcomes}
                    readOnly
                    className="input-field"
                  />
                </div>

                {/* Follow-up Actions */}
                <div className="space-y-2.5 col-span-2">
                  <label className="block text-xs font-bold text-slate-600 uppercase tracking-tight">Agreed Next Actions</label>
                  <textarea
                    value={form.followUpActions}
                    readOnly
                    className="input-field bg-slate-50/50 min-h-[80px] resize-none"
                  />
                </div>
              </div>
            </motion.section>

          </div>
        </div>
      </motion.div>

      {/* Footer Status */}
      <div className="max-w-4xl mx-auto mt-6 flex items-center justify-between px-2">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest text-nowrap">AI Extraction Active</span>
          </div>
          <div className="w-px h-3 bg-slate-200" />
          <div className="flex items-center gap-2 cursor-pointer hover:text-brand-primary transition-colors text-slate-400 group">
            <Mic className="w-3.5 h-3.5 group-hover:scale-110 transition-transform" />
            <span className="text-[10px] font-bold uppercase tracking-widest italic text-nowrap">Dictation Mode</span>
          </div>
        </div>
        <p className="text-[10px] font-mono text-slate-400">SESSION_ID: {Math.random().toString(36).substring(7).toUpperCase()}</p>
      </div>
    </div>
  );
};

export default InteractionForm;
