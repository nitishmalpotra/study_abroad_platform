'use client';

import { useMemo, useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import Link from 'next/link';
import {
  AlertCircle,
  BarChart3,
  CheckCircle2,
  ChevronRight,
  Loader2,
  Plus,
  RotateCcw,
  ShieldCheck,
  Sparkles,
  Target,
  Trash2,
} from 'lucide-react';
import ToolLeadGate from '../components/ToolLeadGate';
import type { AdmissionsPredictionRequest, AdmissionsPredictionResponse, ApiError } from '../contracts/api';
import {
  AdmissionsPredictionApiError,
  submitAdmissionsPrediction,
  type AdmissionsPredictionMode,
} from '../lib/admissionsApi';

const emptyApiError: ApiError = {
  code: 'validation_error',
  message: '',
  details: [],
};

const inputBase = 'w-full px-4 py-3 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent';

const chanceStyles = {
  Safe: 'bg-emerald-50 text-emerald-700 border-emerald-100',
  Target: 'bg-blue-50 text-blue-700 border-blue-100',
  Reach: 'bg-amber-50 text-amber-700 border-amber-100',
  Unrealistic: 'bg-rose-50 text-rose-700 border-rose-100',
};

const initialForm: AdmissionsPredictionRequest = {
  full_name: '',
  target_intake: '',
  target_country: '',
  undergrad_degree_name: '',
  cgpa: 0,
  cgpa_scale: 10,
  gre_score: null,
  gmat_score: null,
  english_test: null,
  english_score: null,
  work_experience_months: 0,
  research_publications: 0,
  target_programs: [''],
};

function numberOrNull(value: string): number | null {
  if (value.trim() === '') return null;
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : null;
}

function numberOrZero(value: string): number {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : 0;
}

function validateForm(form: AdmissionsPredictionRequest): ApiError | null {
  const details: string[] = [];
  const requiredFields: Array<[keyof AdmissionsPredictionRequest, string]> = [
    ['full_name', 'Full name is required.'],
    ['target_intake', 'Target intake is required.'],
    ['target_country', 'Target country is required.'],
    ['undergrad_degree_name', 'Undergraduate degree is required.'],
  ];

  requiredFields.forEach(([field, message]) => {
    const value = form[field];
    if (typeof value === 'string' && value.trim().length === 0) details.push(message);
  });

  if (form.cgpa <= 0 || form.cgpa > form.cgpa_scale) {
    details.push(`CGPA must be greater than 0 and no more than ${form.cgpa_scale}.`);
  }

  if (form.gre_score !== null && (form.gre_score < 260 || form.gre_score > 340)) {
    details.push('GRE score must be between 260 and 340.');
  }

  if (form.gmat_score !== null && (form.gmat_score < 200 || form.gmat_score > 805)) {
    details.push('GMAT score must be between 200 and 805.');
  }

  if (form.english_test === 'IELTS' && (form.english_score === null || form.english_score < 0 || form.english_score > 9)) {
    details.push('IELTS score must be between 0 and 9.');
  }

  if (form.english_test === 'TOEFL' && (form.english_score === null || form.english_score < 0 || form.english_score > 120)) {
    details.push('TOEFL score must be between 0 and 120.');
  }

  if (form.english_test === null && form.english_score !== null) {
    details.push('Choose IELTS or TOEFL when entering an English test score.');
  }

  const programs = form.target_programs.map((program) => program.trim()).filter(Boolean);
  if (programs.length === 0) details.push('Add at least one target program.');
  if (new Set(programs.map((program) => program.toLowerCase())).size !== programs.length) {
    details.push('Target programs must be distinct.');
  }

  if (details.length === 0) return null;

  return {
    ...emptyApiError,
    message: 'Please fix the highlighted admit predictor fields before submitting.',
    details,
  };
}

function AdmitPredictorTool() {
  const [form, setForm] = useState<AdmissionsPredictionRequest>(initialForm);
  const [state, setState] = useState<'input' | 'loading' | 'result'>('input');
  const [activeMode, setActiveMode] = useState<AdmissionsPredictionMode>('live');
  const [result, setResult] = useState<AdmissionsPredictionResponse | null>(null);
  const [error, setError] = useState<ApiError | null>(null);

  const cleanedPayload = useMemo<AdmissionsPredictionRequest>(
    () => ({
      ...form,
      full_name: form.full_name.trim(),
      target_intake: form.target_intake.trim(),
      target_country: form.target_country.trim(),
      undergrad_degree_name: form.undergrad_degree_name.trim(),
      target_programs: form.target_programs.map((program) => program.trim()).filter(Boolean),
    }),
    [form],
  );

  const updateField = <K extends keyof AdmissionsPredictionRequest>(field: K, value: AdmissionsPredictionRequest[K]) => {
    setForm((current) => ({ ...current, [field]: value }));
    setError(null);
  };

  const updateProgram = (index: number, value: string) => {
    setForm((current) => ({
      ...current,
      target_programs: current.target_programs.map((program, programIndex) => (programIndex === index ? value : program)),
    }));
    setError(null);
  };

  const addProgram = () => {
    setForm((current) => ({
      ...current,
      target_programs: current.target_programs.length >= 5 ? current.target_programs : [...current.target_programs, ''],
    }));
  };

  const removeProgram = (index: number) => {
    setForm((current) => ({
      ...current,
      target_programs: current.target_programs.length === 1
        ? ['']
        : current.target_programs.filter((_, programIndex) => programIndex !== index),
    }));
    setError(null);
  };

  const handlePredict = async (mode: AdmissionsPredictionMode) => {
    const validationError = validateForm(cleanedPayload);
    if (validationError) {
      setError(validationError);
      return;
    }

    setActiveMode(mode);
    setState('loading');
    setError(null);
    setResult(null);

    try {
      const response = await submitAdmissionsPrediction(cleanedPayload, mode);
      setResult(response);
      setState('result');
    } catch (caught) {
      if (caught instanceof AdmissionsPredictionApiError) {
        setError(caught.payload);
      } else {
        setError({
          code: 'unknown_error',
          message: 'The admit prediction request failed safely. Please try again later.',
          details: [],
        });
      }
      setState('input');
    }
  };

  const handleReset = () => {
    setForm(initialForm);
    setResult(null);
    setError(null);
    setState('input');
  };

  return (
    <section className="section-padding bg-slate-50">
      <div className="container-max mx-auto max-w-5xl">
        <AnimatePresence mode="wait">
          {state === 'input' && (
            <motion.div key="input" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }}>
              <div className="card p-6">
                <div className="flex items-center gap-3 mb-6">
                  <div className="w-10 h-10 bg-rose-50 rounded-xl flex items-center justify-center">
                    <Target className="w-5 h-5 text-rose-600" />
                  </div>
                  <div>
                    <h2 className="text-lg font-bold text-brand-900">Applicant Profile</h2>
                    <p className="text-sm text-slate-500">Live mode uses the admissions API; demo mode returns deterministic sample predictions.</p>
                  </div>
                </div>

                <div className="grid md:grid-cols-2 gap-4">
                  <input value={form.full_name} onChange={(event) => updateField('full_name', event.target.value)} className={inputBase} placeholder="Full name" />
                  <input value={form.target_intake} onChange={(event) => updateField('target_intake', event.target.value)} className={inputBase} placeholder="Target intake, e.g. Fall 2026" />
                  <input value={form.target_country} onChange={(event) => updateField('target_country', event.target.value)} className={inputBase} placeholder="Target country" />
                  <input value={form.undergrad_degree_name} onChange={(event) => updateField('undergrad_degree_name', event.target.value)} className={inputBase} placeholder="Undergraduate degree, e.g. BTech CSE" />
                </div>

                <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4 mt-4">
                  <input value={form.cgpa || ''} onChange={(event) => updateField('cgpa', numberOrZero(event.target.value))} className={inputBase} placeholder="CGPA" inputMode="decimal" />
                  <select value={form.cgpa_scale} onChange={(event) => updateField('cgpa_scale', Number(event.target.value) as 4 | 10)} className={inputBase}>
                    <option value={10}>10-point CGPA</option>
                    <option value={4}>4-point GPA</option>
                  </select>
                  <input value={form.gre_score ?? ''} onChange={(event) => updateField('gre_score', numberOrNull(event.target.value))} className={inputBase} placeholder="GRE score (optional)" inputMode="numeric" />
                  <input value={form.gmat_score ?? ''} onChange={(event) => updateField('gmat_score', numberOrNull(event.target.value))} className={inputBase} placeholder="GMAT score (optional)" inputMode="numeric" />
                </div>

                <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4 mt-4">
                  <select
                    value={form.english_test ?? ''}
                    onChange={(event) => updateField('english_test', event.target.value === '' ? null : event.target.value as 'IELTS' | 'TOEFL')}
                    className={inputBase}
                  >
                    <option value="">English test</option>
                    <option value="IELTS">IELTS</option>
                    <option value="TOEFL">TOEFL</option>
                  </select>
                  <input value={form.english_score ?? ''} onChange={(event) => updateField('english_score', numberOrNull(event.target.value))} className={inputBase} placeholder="English score" inputMode="decimal" />
                  <input value={form.work_experience_months || ''} onChange={(event) => updateField('work_experience_months', numberOrZero(event.target.value))} className={inputBase} placeholder="Work experience months" inputMode="numeric" />
                  <input value={form.research_publications || ''} onChange={(event) => updateField('research_publications', numberOrZero(event.target.value))} className={inputBase} placeholder="Research publications" inputMode="numeric" />
                </div>

                <div className="mt-6">
                  <div className="flex items-center justify-between gap-3 mb-3">
                    <h3 className="text-sm font-bold text-brand-900">Target Programs</h3>
                    <button onClick={addProgram} disabled={form.target_programs.length >= 5} className="btn-outline text-xs py-2 px-3 disabled:opacity-40 disabled:cursor-not-allowed">
                      <Plus className="w-4 h-4" />
                      Add Program
                    </button>
                  </div>
                  <div className="space-y-3">
                    {form.target_programs.map((program, index) => (
                      <div key={index} className="flex gap-2">
                        <input
                          value={program}
                          onChange={(event) => updateProgram(index, event.target.value)}
                          className={inputBase}
                          placeholder={`Program ${index + 1}, e.g. MS Computer Science at Northeastern University`}
                        />
                        <button onClick={() => removeProgram(index)} className="w-12 shrink-0 inline-flex items-center justify-center rounded-xl border border-slate-200 text-slate-500 hover:text-rose-600 hover:border-rose-200 transition-colors" aria-label="Remove program">
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    ))}
                  </div>
                  <p className="mt-2 text-xs text-slate-400">Add 1–5 distinct programs. Results are returned in the shared admissions prediction contract.</p>
                </div>

                {error && (
                  <div className="mt-5 p-4 bg-rose-50 border border-rose-100 rounded-xl">
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

                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mt-6">
                  <span className="text-xs text-slate-400">Mock calls do not use live AI quota. Live calls may be rate-limited by the backend.</span>
                  <div className="flex flex-col sm:flex-row gap-3">
                    <button onClick={() => void handlePredict('mock')} className="btn-outline text-sm">
                      <ShieldCheck className="w-4 h-4" />
                      Demo Prediction
                    </button>
                    <button onClick={() => void handlePredict('live')} className="btn-primary text-sm">
                      <Sparkles className="w-4 h-4" />
                      Predict Chances
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
              <h3 className="text-xl font-bold text-brand-900 mb-2">{activeMode === 'mock' ? 'Loading Demo Prediction' : 'Predicting Admission Chances'}</h3>
              <p className="text-sm text-slate-500 max-w-sm mx-auto">
                {activeMode === 'mock'
                  ? 'Fetching deterministic admissions output from the mock API.'
                  : 'The secure API is evaluating your profile against the selected programs.'}
              </p>
              <div className="mt-8 max-w-xs mx-auto">
                <motion.div className="h-1.5 bg-slate-100 rounded-full overflow-hidden">
                  <motion.div className="h-full bg-brand-700 rounded-full" initial={{ width: '0%' }} animate={{ width: '100%' }} transition={{ duration: activeMode === 'mock' ? 1 : 3, ease: 'easeInOut' }} />
                </motion.div>
              </div>
            </motion.div>
          )}

          {state === 'result' && result && (
            <motion.div key="result" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
              <div className="card p-6">
                <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-6">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-accent-50 rounded-xl flex items-center justify-center">
                      <CheckCircle2 className="w-5 h-5 text-accent-600" />
                    </div>
                    <div>
                      <div className="flex flex-wrap items-center gap-2">
                        <h2 className="text-lg font-bold text-brand-900">Prediction Complete</h2>
                        {result.mode === 'mock' && <span className="px-2 py-1 bg-lavender-100 text-brand-700 text-xs font-semibold rounded-full">Demo output</span>}
                      </div>
                      <p className="text-sm text-slate-500">
                        {result.mode === 'mock' ? 'This is deterministic sample feedback from the mock API, not a DeepSeek prediction.' : 'Live admissions prediction returned by the backend API.'}
                      </p>
                    </div>
                  </div>
                  <button onClick={handleReset} className="btn-outline text-sm py-2">
                    <RotateCcw className="w-4 h-4" />
                    Predict Another
                  </button>
                </div>

                <div className="grid gap-4">
                  {result.prediction.target_predictions.map((prediction) => (
                    <div key={prediction.program_name} className="p-5 bg-slate-50 rounded-xl border border-slate-100">
                      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-4">
                        <div>
                          <h3 className="text-base font-bold text-brand-900">{prediction.program_name}</h3>
                          <p className="text-sm text-slate-500 mt-1">{prediction.brief_reasoning}</p>
                        </div>
                        <span className={`inline-flex w-fit items-center rounded-full border px-3 py-1 text-xs font-bold ${chanceStyles[prediction.chance_category]}`}>
                          {prediction.chance_category}
                        </span>
                      </div>
                      <div className="flex items-center gap-4">
                        <div className="flex-1 h-2.5 bg-slate-200 rounded-full overflow-hidden">
                          <motion.div className="h-full bg-accent-500 rounded-full" initial={{ width: 0 }} animate={{ width: `${prediction.estimated_probability_percentage}%` }} transition={{ duration: 0.8 }} />
                        </div>
                        <span className="text-sm font-bold text-brand-900 w-12 text-right">{prediction.estimated_probability_percentage}%</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="grid lg:grid-cols-2 gap-6">
                <ResultList title="Profile Strengths" icon={<CheckCircle2 className="w-5 h-5 text-emerald-600" />} items={result.prediction.profile_strengths} />
                <ResultList title="Profile Weaknesses" icon={<AlertCircle className="w-5 h-5 text-amber-600" />} items={result.prediction.profile_weaknesses} />
                <ResultList title="Action Roadmap" icon={<BarChart3 className="w-5 h-5 text-blue-600" />} items={result.prediction.actionable_roadmap} />
                <ResultList title="Recommended Universities" icon={<Target className="w-5 h-5 text-rose-600" />} items={result.prediction.recommended_universities} />
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </section>
  );
}

function ResultList({ title, icon, items }: { title: string; icon: React.ReactNode; items: string[] }) {
  return (
    <div className="card p-5">
      <div className="flex items-center gap-3 mb-4">
        <div className="w-10 h-10 bg-slate-50 rounded-xl flex items-center justify-center">{icon}</div>
        <h3 className="text-base font-bold text-brand-900">{title}</h3>
      </div>
      <ul className="space-y-3">
        {items.map((item, index) => (
          <li key={`${item}-${index}`} className="flex items-start gap-3 text-sm text-slate-600 leading-relaxed">
            <span className="mt-2 w-1.5 h-1.5 bg-accent-500 rounded-full shrink-0" />
            {item}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default function AdmitPredictorPage() {
  return (
    <>
      <section className="bg-brand-900 pt-28 pb-16 lg:pt-36 lg:pb-20">
        <div className="container-max mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="max-w-2xl">
            <div className="flex items-center gap-2 text-sm text-brand-300 mb-4">
              <Link href="/tools" className="hover:text-white transition-colors">Tools</Link>
              <ChevronRight className="w-4 h-4" />
              <span className="text-white">Admit Predictor</span>
            </div>
            <h1 className="text-3xl lg:text-5xl font-bold text-white mb-4">Admit Predictor</h1>
            <p className="text-lg text-brand-300">
              Estimate admission chances across target programs with profile strengths, weaknesses, roadmap, and university recommendations.
            </p>
          </motion.div>
        </div>
      </section>

      <ToolLeadGate
        toolName="admit-predictor"
        title="Unlock the Admit Predictor"
        description="Tell us a bit about yourself to access free AI-powered admissions predictions."
      >
        <AdmitPredictorTool />
      </ToolLeadGate>
    </>
  );
}
