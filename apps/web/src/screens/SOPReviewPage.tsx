'use client';

import { useMemo, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Link from 'next/link';
import {
  ChevronRight,
  FileText,
  Sparkles,
  CheckCircle2,
  AlertCircle,
  RotateCcw,
  Loader2,
  ShieldCheck,
} from 'lucide-react';
import ToolLeadGate from '../components/ToolLeadGate';
import type { ApiError, SOPReviewRequest, SOPReviewResponse } from '../contracts/api';
import { SOPReviewApiError, submitSOPReview, type SOPReviewMode } from '../lib/sopReviewApi';

const criterionColors = [
  'bg-emerald-500',
  'bg-blue-500',
  'bg-amber-500',
  'bg-rose-500',
  'bg-violet-500',
];

const emptyApiError: ApiError = {
  code: 'validation_error',
  message: '',
  details: [],
};

const inputBase = 'w-full px-4 py-3 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent';

function wordCount(value: string): number {
  return value.trim().split(/\s+/).filter(Boolean).length;
}

function SOPTool() {
  const [form, setForm] = useState<SOPReviewRequest>({
    full_name: '',
    mobile: '',
    university: '',
    intake: '',
    country: '',
    sop_text: '',
  });
  const [state, setState] = useState<'input' | 'loading' | 'result'>('input');
  const [activeMode, setActiveMode] = useState<SOPReviewMode>('live');
  const [result, setResult] = useState<SOPReviewResponse | null>(null);
  const [error, setError] = useState<ApiError | null>(null);

  const sopWordCount = useMemo(() => wordCount(form.sop_text), [form.sop_text]);
  const canSubmit = Object.values(form).every((value) => value.trim().length > 0);
  const grade = result?.grade;
  const isDemo = result?.mode === 'mock';

  const updateField = (field: keyof SOPReviewRequest, value: string) => {
    setForm((current) => ({ ...current, [field]: value }));
    setError(null);
  };

  const handleAnalyze = async (mode: SOPReviewMode) => {
    if (!canSubmit) {
      setError({ ...emptyApiError, message: 'Please complete all SOP review fields before submitting.' });
      return;
    }

    setActiveMode(mode);
    setState('loading');
    setError(null);
    setResult(null);

    try {
      const response = await submitSOPReview(form, mode);
      setResult(response);
      setState('result');
    } catch (caught) {
      if (caught instanceof SOPReviewApiError) {
        setError(caught.payload);
      } else {
        setError({
          code: 'unknown_error',
          message: 'The SOP review request failed safely. Please try again later.',
          details: [],
        });
      }
      setState('input');
    }
  };

  const handleReset = () => {
    setForm({
      full_name: '',
      mobile: '',
      university: '',
      intake: '',
      country: '',
      sop_text: '',
    });
    setResult(null);
    setError(null);
    setState('input');
  };

  return (
    <section className="section-padding bg-slate-50">
      <div className="container-max mx-auto max-w-4xl">
        <AnimatePresence mode="wait">
          {state === 'input' && (
            <motion.div key="input" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }}>
              <div className="card p-6">
                <div className="flex items-center gap-3 mb-5">
                  <div className="w-10 h-10 bg-emerald-50 rounded-xl flex items-center justify-center">
                    <FileText className="w-5 h-5 text-emerald-600" />
                  </div>
                  <div>
                    <h2 className="text-lg font-bold text-brand-900">Paste Your SOP</h2>
	                    <p className="text-sm text-slate-500">Live review uses the secure backend API; demo mode returns sample output. AI feedback is informational and should be reviewed by a human.</p>
                  </div>
                </div>

                <div className="grid sm:grid-cols-2 gap-4 mb-4">
                  <input value={form.full_name} onChange={(e) => updateField('full_name', e.target.value)} className={inputBase} placeholder="Full name" />
                  <input value={form.mobile} onChange={(e) => updateField('mobile', e.target.value.replace(/\D/g, '').slice(0, 15))} className={inputBase} placeholder="Mobile number" inputMode="numeric" />
                  <input value={form.university} onChange={(e) => updateField('university', e.target.value)} className={inputBase} placeholder="Target university" />
                  <input value={form.intake} onChange={(e) => updateField('intake', e.target.value)} className={inputBase} placeholder="Target intake, e.g. Fall 2026" />
                  <input value={form.country} onChange={(e) => updateField('country', e.target.value)} className={`${inputBase} sm:col-span-2`} placeholder="Target country" />
                </div>

                <textarea
                  value={form.sop_text}
                  onChange={(e) => updateField('sop_text', e.target.value)}
                  rows={14}
                  className={`${inputBase} resize-none leading-relaxed`}
                  placeholder="Paste your Statement of Purpose here. Live mode checks the backend SOP rubric: academic fit, university specificity, career clarity, narrative flow, and language tone."
                />

                {error && (
                  <div className="mt-4 p-4 bg-rose-50 border border-rose-100 rounded-xl">
                    <div className="flex items-start gap-3">
                      <AlertCircle className="w-5 h-5 text-rose-500 shrink-0 mt-0.5" />
                      <div>
                        <p className="text-sm font-semibold text-rose-800">{error.message}</p>
                        {error.details.length > 0 && (
                          <ul className="mt-2 space-y-1">
                            {error.details.map((detail, index) => (
                              <li key={`${detail}-${index}`} className="text-xs text-rose-700">{detail}</li>
                            ))}
                          </ul>
                        )}
                      </div>
                    </div>
                  </div>
                )}

                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mt-4">
                  <span className="text-xs text-slate-400">
                    {form.sop_text.length} characters · {sopWordCount} words · backend expects 100–2500 words for live scoring
                  </span>
                  <div className="flex flex-col sm:flex-row gap-3">
                    <button
                      onClick={() => void handleAnalyze('mock')}
                      disabled={!canSubmit}
                      className="btn-outline text-sm disabled:opacity-40 disabled:cursor-not-allowed"
                    >
                      <ShieldCheck className="w-4 h-4" />
                      Demo Review
                    </button>
                    <button
                      onClick={() => void handleAnalyze('live')}
                      disabled={!canSubmit}
                      className="btn-primary text-sm disabled:opacity-40 disabled:cursor-not-allowed"
                    >
                      <Sparkles className="w-4 h-4" />
                      Analyze SOP
                    </button>
                  </div>
                </div>
              </div>
            </motion.div>
          )}

          {state === 'loading' && (
            <motion.div key="loading" initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0, scale: 0.95 }} className="card p-12 text-center">
              <motion.div animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 1.5, ease: 'linear' }} className="w-16 h-16 mx-auto mb-6">
                <Loader2 className="w-16 h-16 text-brand-700" />
              </motion.div>
              <h3 className="text-xl font-bold text-brand-900 mb-2">{activeMode === 'mock' ? 'Loading Demo Review' : 'Analyzing Your SOP'}</h3>
              <p className="text-sm text-slate-500 max-w-sm mx-auto">
                {activeMode === 'mock'
                  ? 'Fetching deterministic demo output from the mock API. No DeepSeek request is made.'
                  : 'The secure API is reviewing your SOP against the backend rubric.'}
              </p>
              <div className="mt-8 max-w-xs mx-auto">
                <motion.div className="h-1.5 bg-slate-100 rounded-full overflow-hidden">
                  <motion.div
                    className="h-full bg-brand-700 rounded-full"
                    initial={{ width: '0%' }}
                    animate={{ width: '100%' }}
                    transition={{ duration: activeMode === 'mock' ? 1 : 3, ease: 'easeInOut' }}
                  />
                </motion.div>
              </div>
            </motion.div>
          )}

          {state === 'result' && result && (
            <motion.div key="result" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
              <div className="card p-6">
                <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-6">
                  <div className="flex items-center gap-3">
                    <div className={`w-10 h-10 ${grade ? 'bg-accent-50' : 'bg-amber-50'} rounded-xl flex items-center justify-center`}>
                      {grade ? <CheckCircle2 className="w-5 h-5 text-accent-600" /> : <AlertCircle className="w-5 h-5 text-amber-500" />}
                    </div>
                    <div>
                      <div className="flex flex-wrap items-center gap-2">
                        <h2 className="text-lg font-bold text-brand-900">{grade ? 'Analysis Complete' : 'SOP Needs Revision Before Scoring'}</h2>
                        {isDemo && <span className="px-2 py-1 bg-lavender-100 text-brand-700 text-xs font-semibold rounded-full">Demo output</span>}
                      </div>
                      <p className="text-sm text-slate-500">
                        {isDemo ? 'This is deterministic sample feedback from the mock API, not a DeepSeek review.' : result.gatekeeper.reason}
                      </p>
                    </div>
                  </div>
                  <button onClick={handleReset} className="btn-outline text-sm py-2">
                    <RotateCcw className="w-4 h-4" />
                    Analyze Another
                  </button>
                </div>

                {grade ? (
                  <>
                    <div className="bg-brand-800 rounded-xl p-6 mb-6 flex items-center gap-6">
                      <div className="text-center">
                        <p className="text-4xl font-bold text-white">{grade.overall_score.toFixed(1)}</p>
                        <p className="text-sm text-brand-200">out of 10</p>
                      </div>
                      <div className="flex-1">
                        <p className="text-sm text-brand-100 font-medium mb-1">Overall Score</p>
                        <p className="text-sm text-brand-300">{grade.summary}</p>
                      </div>
                    </div>

                    <div className="space-y-4">
                      {grade.criteria_breakdown.map((item, index) => (
                        <div key={item.name} className="p-4 bg-slate-50 rounded-xl">
                          <div className="flex items-center justify-between mb-2">
                            <span className="text-sm font-semibold text-brand-800">{item.name}</span>
                            <span className="text-sm font-bold text-brand-900">{item.score}/10</span>
                          </div>
                          <div className="h-2 bg-slate-200 rounded-full overflow-hidden mb-3">
                            <motion.div
                              className={`h-full ${criterionColors[index]} rounded-full`}
                              initial={{ width: 0 }}
                              animate={{ width: `${(item.score / 10) * 100}%` }}
                              transition={{ duration: 0.8, delay: 0.2 }}
                            />
                          </div>
                          <p className="text-xs text-slate-600 leading-relaxed">{item.feedback}</p>
                        </div>
                      ))}
                    </div>
                  </>
                ) : (
                  <div className="p-5 bg-amber-50 border border-amber-100 rounded-xl">
                    <p className="text-sm font-semibold text-amber-800 mb-1">Review not scored</p>
                    <p className="text-sm text-amber-700 leading-relaxed">{result.gatekeeper.reason}</p>
                  </div>
                )}
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
              <Link href="/tools" className="hover:text-white transition-colors">Tools</Link>
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
