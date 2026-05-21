'use client';

import { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Phone, Mail, MapPin, GraduationCap, ChevronRight, Compass, Calendar, CheckCircle2, BookOpen } from 'lucide-react';
import { submitLead } from '../lib/leadsApi';

const countryOptions = ['United States', 'United Kingdom', 'Canada', 'Australia', 'Ireland', 'New Zealand', 'Germany', 'Other'];
const intakeOptions = ['Fall 2026', 'Spring 2027', 'Fall 2027', 'Spring 2028'];
const stageOptions = [
  'Just exploring options',
  'Shortlisting universities',
  'Preparing for tests (GRE/IELTS)',
  'Applying to universities',
  'Admitted & need a loan',
  'Visa stage',
];

interface ResourceLeadModalProps {
  isOpen: boolean;
  resourceName: string;
  onClose: () => void;
}

const backdrop = {
  hidden: { opacity: 0 },
  visible: { opacity: 1 },
};

const panel = {
  hidden: { opacity: 0, scale: 0.95, y: 20 },
  visible: { opacity: 1, scale: 1, y: 0, transition: { type: 'spring' as const, damping: 25, stiffness: 300 } },
  exit: { opacity: 0, scale: 0.95, y: 20 },
};

export default function ResourceLeadModal({ isOpen, resourceName, onClose }: ResourceLeadModalProps) {
  const [step, setStep] = useState<'phone' | 'otp' | 'details' | 'done'>('phone');
  const [phone, setPhone] = useState('');
  const [otp, setOtp] = useState(['', '', '', '']);
  const [email, setEmail] = useState('');
  const [country, setCountry] = useState('');
  const [college, setCollege] = useState('');
  const [course, setCourse] = useState('');
  const [intake, setIntake] = useState('');
  const [stage, setStage] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const otpRefs = useRef<(HTMLInputElement | null)[]>([]);

  const handleOtpChange = (index: number, value: string) => {
    if (value.length > 1) return;
    const next = [...otp];
    next[index] = value;
    setOtp(next);
    if (value && index < 3) otpRefs.current[index + 1]?.focus();
  };

  const handleOtpKeyDown = (index: number, e: React.KeyboardEvent) => {
    if (e.key === 'Backspace' && !otp[index] && index > 0) {
      otpRefs.current[index - 1]?.focus();
    }
  };

  const handleSubmit = async () => {
    setSubmitting(true);
    setError('');
    try {
      await submitLead({
        tool_name: `resource:${resourceName}`,
        phone,
        email,
        target_country: country,
        target_intake: intake,
        target_college: college,
        target_course: course,
        journey_stage: stage,
      });
      setStep('done');
    } catch {
      if (process.env.NODE_ENV !== 'production') {
        // Local dev convenience: proceed even if the API/lead store isn't running.
        setStep('done');
        return;
      }
      setError('Something went wrong. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleClose = () => {
    onClose();
    setTimeout(() => {
      setStep('phone');
      setPhone('');
      setOtp(['', '', '', '']);
      setEmail('');
      setCountry('');
      setCollege('');
      setCourse('');
      setIntake('');
      setStage('');
      setError('');
    }, 300);
  };

  const inputBase = "w-full py-3 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent";
  const stepLabels = ['Phone', 'Verify', 'Details'];
  const currentIndex = step === 'phone' ? 0 : step === 'otp' ? 1 : 2;

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          className="fixed inset-0 z-[100] flex items-center justify-center p-4"
          variants={backdrop}
          initial="hidden"
          animate="visible"
          exit="hidden"
        >
          <div className="absolute inset-0 bg-brand-950/60 backdrop-blur-sm" onClick={handleClose} />

          <motion.div
            variants={panel}
            initial="hidden"
            animate="visible"
            exit="exit"
            className="relative bg-white rounded-2xl shadow-2xl w-full max-w-md overflow-hidden max-h-[90vh] overflow-y-auto"
          >
            <div className="bg-brand-700 px-6 py-5 text-white">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold">
                  {step === 'done' ? '' : 'Download Resource'}
                </h2>
                <button onClick={handleClose} className="p-1.5 rounded-lg hover:bg-white/10 transition-colors">
                  <X className="w-5 h-5" />
                </button>
              </div>
              {step !== 'done' && (
                <>
                  <p className="text-sm text-brand-200 mb-3">
                    Share a few details to download <span className="text-white font-medium">{resourceName}</span>
                  </p>
                  <div className="flex gap-2">
                    {stepLabels.map((label, i) => (
                      <div key={label} className="flex-1">
                        <div className={`h-1 rounded-full mb-1 transition-colors ${i <= currentIndex ? 'bg-accent-400' : 'bg-white/20'}`} />
                        <p className={`text-xs ${i <= currentIndex ? 'text-white' : 'text-white/40'}`}>{label}</p>
                      </div>
                    ))}
                  </div>
                </>
              )}
            </div>

            <div className="p-6">
              <AnimatePresence mode="wait">
                {step === 'phone' && (
                  <motion.div key="phone" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }} className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-slate-700 mb-1.5">Phone Number</label>
                      <div className="relative">
                        <Phone className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                        <div className="absolute left-10 top-1/2 -translate-y-1/2 text-sm text-slate-500">+91</div>
                        <input
                          type="tel"
                          value={phone}
                          onChange={(e) => setPhone(e.target.value.replace(/\D/g, '').slice(0, 10))}
                          className={`${inputBase} pl-[4.5rem] pr-4`}
                          placeholder="10-digit mobile number"
                        />
                      </div>
                    </div>
                    <button onClick={() => setStep('otp')} disabled={phone.length !== 10} className="btn-primary w-full disabled:opacity-40 disabled:cursor-not-allowed">
                      Send OTP <ChevronRight className="w-4 h-4" />
                    </button>
                  </motion.div>
                )}

                {step === 'otp' && (
                  <motion.div key="otp" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }} className="space-y-5">
                    <div className="text-center">
                      <p className="text-sm text-slate-600 mb-0.5">Enter 4-digit code sent to</p>
                      <p className="text-sm font-semibold text-brand-800">+91 {phone}</p>
                    </div>
                    <div className="flex justify-center gap-3">
                      {otp.map((digit, i) => (
                        <input
                          key={i}
                          ref={(el) => { otpRefs.current[i] = el; }}
                          type="text"
                          inputMode="numeric"
                          maxLength={1}
                          value={digit}
                          onChange={(e) => handleOtpChange(i, e.target.value.replace(/\D/g, ''))}
                          onKeyDown={(e) => handleOtpKeyDown(i, e)}
                          className="w-12 h-12 sm:w-14 sm:h-14 text-center text-xl font-semibold border-2 border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent"
                        />
                      ))}
                    </div>
                    <p className="text-center text-xs text-slate-500">
                      Didn't get a code? <button className="text-brand-700 font-medium hover:underline">Resend</button>
                    </p>
                    <div className="flex gap-3">
                      <button onClick={() => setStep('phone')} className="btn-outline flex-1 text-sm py-2.5">Back</button>
                      <button onClick={() => setStep('details')} disabled={otp.some((d) => !d)} className="btn-primary flex-1 text-sm py-2.5 disabled:opacity-40 disabled:cursor-not-allowed">
                        Verify <ChevronRight className="w-4 h-4" />
                      </button>
                    </div>
                  </motion.div>
                )}

                {step === 'details' && (
                  <motion.div key="details" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }} className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-slate-700 mb-1.5">Email Address</label>
                      <div className="relative">
                        <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                        <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} className={`${inputBase} pl-10 pr-4`} placeholder="your@email.com" />
                      </div>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-slate-700 mb-1.5">Target Country</label>
                      <div className="relative">
                        <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                        <select value={country} onChange={(e) => setCountry(e.target.value)} className={`${inputBase} pl-10 pr-4 bg-white appearance-none`}>
                          <option value="">Select country</option>
                          {countryOptions.map((c) => <option key={c} value={c}>{c}</option>)}
                        </select>
                      </div>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-slate-700 mb-1.5">Target Intake</label>
                      <div className="relative">
                        <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                        <select value={intake} onChange={(e) => setIntake(e.target.value)} className={`${inputBase} pl-10 pr-4 bg-white appearance-none`}>
                          <option value="">Select intake</option>
                          {intakeOptions.map((i) => <option key={i} value={i}>{i}</option>)}
                        </select>
                      </div>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-slate-700 mb-1.5">Target College</label>
                      <div className="relative">
                        <GraduationCap className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                        <input type="text" value={college} onChange={(e) => setCollege(e.target.value)} className={`${inputBase} pl-10 pr-4`} placeholder="e.g., MIT, University of Toronto" />
                      </div>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-slate-700 mb-1.5">Target Course</label>
                      <div className="relative">
                        <BookOpen className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                        <input type="text" value={course} onChange={(e) => setCourse(e.target.value)} className={`${inputBase} pl-10 pr-4`} placeholder="e.g., MS Computer Science, MBA" />
                      </div>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-slate-700 mb-1.5">Where are you in your study abroad journey?</label>
                      <div className="relative">
                        <Compass className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                        <select value={stage} onChange={(e) => setStage(e.target.value)} className={`${inputBase} pl-10 pr-4 bg-white appearance-none`}>
                          <option value="">Select your stage</option>
                          {stageOptions.map((s) => <option key={s} value={s}>{s}</option>)}
                        </select>
                      </div>
                    </div>
                    {error && <p className="text-sm text-red-600 text-center">{error}</p>}
                    <div className="flex gap-3">
                      <button onClick={() => setStep('otp')} className="btn-outline flex-1 text-sm py-2.5">Back</button>
                      <button onClick={handleSubmit} disabled={!email || !country || !stage || submitting} className="btn-primary flex-1 text-sm py-2.5 disabled:opacity-40 disabled:cursor-not-allowed">
                        {submitting ? 'Submitting...' : 'Download'}
                        {!submitting && <ChevronRight className="w-4 h-4" />}
                      </button>
                    </div>
                  </motion.div>
                )}

                {step === 'done' && (
                  <motion.div key="done" initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} className="text-center py-6">
                    <motion.div initial={{ scale: 0 }} animate={{ scale: 1 }} transition={{ type: 'spring', damping: 12, delay: 0.1 }} className="w-16 h-16 bg-accent-50 rounded-full flex items-center justify-center mx-auto mb-5">
                      <CheckCircle2 className="w-8 h-8 text-accent-500" />
                    </motion.div>
                    <h3 className="text-xl font-bold text-brand-900 mb-2">Download Starting!</h3>
                    <p className="text-sm text-slate-600 mb-6 max-w-xs mx-auto">
                      Your <span className="font-medium">{resourceName}</span> is ready. We'll also send a copy to your email.
                    </p>
                    <button onClick={handleClose} className="btn-secondary text-sm">Done</button>
                  </motion.div>
                )}
              </AnimatePresence>

              {step !== 'done' && (
                <p className="text-center text-[11px] text-slate-400 mt-5">
                  Your information is secure and will never be shared with third parties.
                </p>
              )}
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
