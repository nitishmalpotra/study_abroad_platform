import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Link } from 'react-router-dom';
import {
  ChevronRight,
  FileText,
  Sparkles,
  CheckCircle2,
  AlertCircle,
  RotateCcw,
  Loader2,
} from 'lucide-react';
import ToolLeadGate from '../components/ToolLeadGate';

interface ScoreItem {
  label: string;
  score: number;
  max: number;
  feedback: string;
  color: string;
}

const mockResults: ScoreItem[] = [
  {
    label: 'Grammar & Clarity',
    score: 7.5,
    max: 10,
    feedback: 'Generally well-written with minor grammatical issues. Consider revising passive voice constructions in paragraphs 2 and 4 for more direct communication.',
    color: 'bg-emerald-500',
  },
  {
    label: 'Structure & Flow',
    score: 6.8,
    max: 10,
    feedback: 'Logical progression is present but could be strengthened. The transition between your academic background and career goals feels abrupt. Add a bridging sentence.',
    color: 'bg-blue-500',
  },
  {
    label: 'Impact & Persuasion',
    score: 7.2,
    max: 10,
    feedback: 'Good use of specific examples. However, the opening paragraph could be more engaging. Avoid generic statements like "Since childhood, I have been passionate about..."',
    color: 'bg-amber-500',
  },
  {
    label: 'Relevance to Program',
    score: 8.0,
    max: 10,
    feedback: 'Strong alignment with the target program. You effectively connect your research interests to faculty expertise. Consider mentioning specific courses or labs.',
    color: 'bg-rose-500',
  },
];

const suggestions = [
  'Replace the opening with a specific anecdote or experience that sparked your interest.',
  'Quantify your achievements where possible (e.g., "improved efficiency by 30%").',
  'Add a paragraph about why this specific university/program is the right fit.',
  'Strengthen your closing by tying your long-term career goals back to the program.',
  'Reduce the SOP length from ~1200 words to under 1000 for a tighter narrative.',
];

function SOPTool() {
  const [sopText, setSopText] = useState('');
  const [state, setState] = useState<'input' | 'loading' | 'result'>('input');

  const handleAnalyze = () => {
    if (sopText.trim().length < 50) return;
    setState('loading');
    setTimeout(() => setState('result'), 3000);
  };

  const handleReset = () => {
    setSopText('');
    setState('input');
  };

  const overallScore = mockResults.reduce((acc, r) => acc + r.score, 0) / mockResults.length;

  return (
    <section className="section-padding bg-slate-50">
      <div className="container-max mx-auto max-w-4xl">
        <AnimatePresence mode="wait">
          {state === 'input' && (
            <motion.div key="input" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }}>
              <div className="card p-6">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 bg-emerald-50 rounded-xl flex items-center justify-center">
                    <FileText className="w-5 h-5 text-emerald-600" />
                  </div>
                  <div>
                    <h2 className="text-lg font-bold text-brand-900">Paste Your SOP</h2>
                    <p className="text-sm text-slate-500">Minimum 50 characters required</p>
                  </div>
                </div>
                <textarea
                  value={sopText}
                  onChange={(e) => setSopText(e.target.value)}
                  rows={14}
                  className="w-full px-4 py-3 border border-slate-200 rounded-xl text-sm resize-none focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent leading-relaxed"
                  placeholder="Paste your Statement of Purpose here. The AI will analyze it for grammar, structure, impact, and relevance..."
                />
                <div className="flex items-center justify-between mt-4">
                  <span className="text-xs text-slate-400">
                    {sopText.length} characters {sopText.length > 0 && sopText.length < 50 && '(minimum 50)'}
                  </span>
                  <button
                    onClick={handleAnalyze}
                    disabled={sopText.trim().length < 50}
                    className="btn-primary text-sm disabled:opacity-40 disabled:cursor-not-allowed"
                  >
                    <Sparkles className="w-4 h-4" />
                    Analyze SOP
                  </button>
                </div>
              </div>
            </motion.div>
          )}

          {state === 'loading' && (
            <motion.div key="loading" initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0, scale: 0.95 }} className="card p-12 text-center">
              <motion.div animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 1.5, ease: 'linear' }} className="w-16 h-16 mx-auto mb-6">
                <Loader2 className="w-16 h-16 text-brand-700" />
              </motion.div>
              <h3 className="text-xl font-bold text-brand-900 mb-2">Analyzing Your SOP</h3>
              <p className="text-sm text-slate-500 max-w-sm mx-auto">
                Our AI is reviewing your statement for grammar, structure, impact, and program relevance...
              </p>
              <div className="mt-8 max-w-xs mx-auto">
                <motion.div className="h-1.5 bg-slate-100 rounded-full overflow-hidden">
                  <motion.div
                    className="h-full bg-brand-700 rounded-full"
                    initial={{ width: '0%' }}
                    animate={{ width: '100%' }}
                    transition={{ duration: 3, ease: 'easeInOut' }}
                  />
                </motion.div>
              </div>
            </motion.div>
          )}

          {state === 'result' && (
            <motion.div key="result" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
              <div className="card p-6">
                <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-6">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-accent-50 rounded-xl flex items-center justify-center">
                      <CheckCircle2 className="w-5 h-5 text-accent-600" />
                    </div>
                    <div>
                      <h2 className="text-lg font-bold text-brand-900">Analysis Complete</h2>
                      <p className="text-sm text-slate-500">Here's how your SOP scores</p>
                    </div>
                  </div>
                  <button onClick={handleReset} className="btn-outline text-sm py-2">
                    <RotateCcw className="w-4 h-4" />
                    Analyze Another
                  </button>
                </div>

                <div className="bg-brand-800 rounded-xl p-6 mb-6 flex items-center gap-6">
                  <div className="text-center">
                    <p className="text-4xl font-bold text-white">{overallScore.toFixed(1)}</p>
                    <p className="text-sm text-brand-200">out of 10</p>
                  </div>
                  <div className="flex-1">
                    <p className="text-sm text-brand-100 font-medium mb-1">Overall Score</p>
                    <p className="text-sm text-brand-300">
                      Your SOP is above average. Focus on the suggestions below to push it to the next level.
                    </p>
                  </div>
                </div>

                <div className="space-y-4">
                  {mockResults.map((item) => (
                    <div key={item.label} className="p-4 bg-slate-50 rounded-xl">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-semibold text-brand-800">{item.label}</span>
                        <span className="text-sm font-bold text-brand-900">{item.score}/{item.max}</span>
                      </div>
                      <div className="h-2 bg-slate-200 rounded-full overflow-hidden mb-3">
                        <motion.div
                          className={`h-full ${item.color} rounded-full`}
                          initial={{ width: 0 }}
                          animate={{ width: `${(item.score / item.max) * 100}%` }}
                          transition={{ duration: 0.8, delay: 0.2 }}
                        />
                      </div>
                      <p className="text-xs text-slate-600 leading-relaxed">{item.feedback}</p>
                    </div>
                  ))}
                </div>
              </div>

              <div className="card p-6">
                <div className="flex items-center gap-3 mb-4">
                  <AlertCircle className="w-5 h-5 text-amber-500" />
                  <h3 className="text-lg font-bold text-brand-900">Key Suggestions</h3>
                </div>
                <ol className="space-y-3">
                  {suggestions.map((s, i) => (
                    <li key={i} className="flex items-start gap-3 text-sm text-slate-700">
                      <span className="w-6 h-6 bg-amber-50 text-amber-700 rounded-lg flex items-center justify-center text-xs font-bold shrink-0">
                        {i + 1}
                      </span>
                      <span className="leading-relaxed">{s}</span>
                    </li>
                  ))}
                </ol>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </section>
  );
}

export default function SOPReviewPage() {
  return (
    <>
      <section className="bg-brand-900 pt-28 pb-16 lg:pt-36 lg:pb-20">
        <div className="container-max mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="max-w-2xl">
            <div className="flex items-center gap-2 text-sm text-brand-300 mb-4">
              <Link to="/tools" className="hover:text-white transition-colors">Tools</Link>
              <ChevronRight className="w-4 h-4" />
              <span className="text-white">AI SOP Review</span>
            </div>
            <h1 className="text-3xl lg:text-5xl font-bold text-white mb-4">AI SOP Review</h1>
            <p className="text-lg text-brand-300">
              Get instant AI-powered feedback on your Statement of Purpose with detailed scoring and actionable suggestions.
            </p>
          </motion.div>
        </div>
      </section>

      <ToolLeadGate
        toolName="sop-review"
        title="Unlock the AI SOP Review"
        description="Tell us a bit about yourself to access free AI-powered feedback on your Statement of Purpose."
      >
        <SOPTool />
      </ToolLeadGate>
    </>
  );
}
