'use client';

import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, ChevronRight, ChevronLeft, Phone, User, Mail, CheckCircle2, Shield, BookOpen } from 'lucide-react';
import { useModal } from '../context/ModalContext';

const countryOptions = ['United States', 'United Kingdom', 'Canada', 'Australia', 'Ireland', 'New Zealand', 'Germany', 'Other'];
const intakeOptions = ['Fall 2026', 'Spring 2027', 'Fall 2027', 'Spring 2028'];

const backdrop = {
  hidden: { opacity: 0 },
  visible: { opacity: 1 },
};

const modalVariants = {
  hidden: { opacity: 0, scale: 0.95, y: 20 },
  visible: { opacity: 1, scale: 1, y: 0, transition: { type: 'spring' as const, damping: 25, stiffness: 300 } },
  exit: { opacity: 0, scale: 0.95, y: 20 },
};

export default function LeadModal() {
  const { isOpen, closeModal } = useModal();
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    name: '',
    phone: '',
    otp: ['', '', '', ''],
    email: '',
    country: '',
    college: '',
    course: '',
    intake: '',
    loanAmount: '',
  });

  const otpRefs = useRef<(HTMLInputElement | null)[]>([]);

  useEffect(() => {
    if (!isOpen) {
      setTimeout(() => {
        setStep(1);
        setFormData({
          name: '',
          phone: '',
          otp: ['', '', '', ''],
          email: '',
          country: '',
          college: '',
          course: '',
          intake: '',
          loanAmount: '',
        });
      }, 300);
    }
  }, [isOpen]);

  const updateField = (field: string, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleOtpChange = (index: number, value: string) => {
    if (value.length > 1) return;
    const newOtp = [...formData.otp];
    newOtp[index] = value;
    setFormData((prev) => ({ ...prev, otp: newOtp }));
    if (value && index < 3) {
      otpRefs.current[index + 1]?.focus();
    }
  };

  const handleOtpKeyDown = (index: number, e: React.KeyboardEvent) => {
    if (e.key === 'Backspace' && !formData.otp[index] && index > 0) {
      otpRefs.current[index - 1]?.focus();
    }
  };

  const stepLabels = ['Your Details', 'Verify Phone', 'Loan Details'];
  const inputClass = "w-full pl-10 pr-4 py-3 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent";
  const selectClass = "w-full px-3 py-3 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent bg-white";

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
          <div className="absolute inset-0 bg-brand-950/60 backdrop-blur-sm" onClick={closeModal} />

          <motion.div
            variants={modalVariants}
            initial="hidden"
            animate="visible"
            exit="exit"
            className="relative bg-white rounded-2xl shadow-2xl w-full max-w-md overflow-hidden"
          >
            <div className="bg-brand-700 px-6 py-5 text-white">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold">
                  {step <= 3 ? 'Check Your Loan Eligibility' : ''}
                </h2>
                <button onClick={closeModal} className="p-1.5 rounded-lg hover:bg-white/10 transition-colors">
                  <X className="w-5 h-5" />
                </button>
              </div>
              {step <= 3 && (
                <div className="flex gap-2">
                  {stepLabels.map((label, i) => (
                    <div key={label} className="flex-1">
                      <div className={`h-1 rounded-full mb-1.5 transition-colors ${i + 1 <= step ? 'bg-accent-400' : 'bg-white/20'}`} />
                      <p className={`text-xs ${i + 1 <= step ? 'text-white' : 'text-white/40'}`}>{label}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="p-6">
              <AnimatePresence mode="wait">
                {step === 1 && (
                  <motion.div key="step1" initial={{ opacity: 0, x: 30 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -30 }} className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-slate-700 mb-1.5">Full Name</label>
                      <div className="relative">
                        <User className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                        <input type="text" value={formData.name} onChange={(e) => updateField('name', e.target.value)} className={inputClass} placeholder="Enter your full name" />
                      </div>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-slate-700 mb-1.5">Phone Number</label>
                      <div className="relative">
                        <Phone className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                        <div className="absolute left-10 top-1/2 -translate-y-1/2 text-sm text-slate-500">+91</div>
                        <input type="tel" value={formData.phone} onChange={(e) => updateField('phone', e.target.value.replace(/\D/g, '').slice(0, 10))} className="w-full pl-[4.5rem] pr-4 py-3 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent" placeholder="10-digit mobile number" />
                      </div>
                    </div>
                    <button onClick={() => setStep(2)} disabled={!formData.name || formData.phone.length !== 10} className="btn-primary w-full disabled:opacity-40 disabled:cursor-not-allowed">
                      Send OTP <ChevronRight className="w-4 h-4" />
                    </button>
                  </motion.div>
                )}

                {step === 2 && (
                  <motion.div key="step2" initial={{ opacity: 0, x: 30 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -30 }} className="space-y-5">
                    <div className="text-center">
                      <p className="text-sm text-slate-600 mb-1">We sent a 4-digit code to</p>
                      <p className="text-sm font-semibold text-brand-800">+91 {formData.phone}</p>
                    </div>
                    <div className="flex justify-center gap-3">
                      {formData.otp.map((digit, i) => (
                        <input key={i} ref={(el) => { otpRefs.current[i] = el; }} type="text" inputMode="numeric" maxLength={1} value={digit} onChange={(e) => handleOtpChange(i, e.target.value.replace(/\D/g, ''))} onKeyDown={(e) => handleOtpKeyDown(i, e)} className="w-12 h-12 sm:w-14 sm:h-14 text-center text-xl font-semibold border-2 border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent" />
                      ))}
                    </div>
                    <p className="text-center text-xs text-slate-500">
                      Didn't receive the code? <button className="text-brand-700 font-medium hover:underline">Resend</button>
                    </p>
                    <div className="flex gap-3">
                      <button onClick={() => setStep(1)} className="btn-outline flex-1 text-sm py-2.5"><ChevronLeft className="w-4 h-4" /> Back</button>
                      <button onClick={() => setStep(3)} disabled={formData.otp.some((d) => !d)} className="btn-primary flex-1 text-sm py-2.5 disabled:opacity-40 disabled:cursor-not-allowed">Verify <ChevronRight className="w-4 h-4" /></button>
                    </div>
                  </motion.div>
                )}

                {step === 3 && (
                  <motion.div key="step3" initial={{ opacity: 0, x: 30 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -30 }} className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-slate-700 mb-1.5">Email Address</label>
                      <div className="relative">
                        <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                        <input type="email" value={formData.email} onChange={(e) => updateField('email', e.target.value)} className={inputClass} placeholder="your@email.com" />
                      </div>
                    </div>
                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1.5">Target Country</label>
                        <select value={formData.country} onChange={(e) => updateField('country', e.target.value)} className={selectClass}>
                          <option value="">Select</option>
                          {countryOptions.map((c) => <option key={c} value={c}>{c}</option>)}
                        </select>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1.5">Target Intake</label>
                        <select value={formData.intake} onChange={(e) => updateField('intake', e.target.value)} className={selectClass}>
                          <option value="">Select</option>
                          {intakeOptions.map((i) => <option key={i} value={i}>{i}</option>)}
                        </select>
                      </div>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-slate-700 mb-1.5">Target College</label>
                      <input type="text" value={formData.college} onChange={(e) => updateField('college', e.target.value)} className="w-full px-4 py-3 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent" placeholder="e.g., MIT, University of Toronto" />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-slate-700 mb-1.5">Target Course</label>
                      <div className="relative">
                        <BookOpen className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                        <input type="text" value={formData.course} onChange={(e) => updateField('course', e.target.value)} className="w-full pl-10 pr-4 py-3 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent" placeholder="e.g., MS Computer Science, MBA" />
                      </div>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-slate-700 mb-1.5">Estimated Loan Amount</label>
                      <select value={formData.loanAmount} onChange={(e) => updateField('loanAmount', e.target.value)} className={selectClass}>
                        <option value="">Select range</option>
                        <option value="10-20">INR 10 - 20 Lakhs</option>
                        <option value="20-40">INR 20 - 40 Lakhs</option>
                        <option value="40-60">INR 40 - 60 Lakhs</option>
                        <option value="60-80">INR 60 - 80 Lakhs</option>
                        <option value="80+">INR 80+ Lakhs</option>
                      </select>
                    </div>
                    <div className="flex gap-3">
                      <button onClick={() => setStep(2)} className="btn-outline flex-1 text-sm py-2.5"><ChevronLeft className="w-4 h-4" /> Back</button>
                      <button onClick={() => setStep(4)} disabled={!formData.email || !formData.country || !formData.loanAmount} className="btn-primary flex-1 text-sm py-2.5 disabled:opacity-40 disabled:cursor-not-allowed">Submit Application</button>
                    </div>
                  </motion.div>
                )}

                {step === 4 && (
                  <motion.div key="step4" initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} className="text-center py-6">
                    <motion.div initial={{ scale: 0 }} animate={{ scale: 1 }} transition={{ type: 'spring', damping: 12, delay: 0.1 }} className="w-16 h-16 bg-accent-50 rounded-full flex items-center justify-center mx-auto mb-5">
                      <CheckCircle2 className="w-8 h-8 text-accent-500" />
                    </motion.div>
                    <h3 className="text-xl font-bold text-brand-900 mb-2">Application Received!</h3>
                    <p className="text-sm text-slate-600 mb-6 max-w-xs mx-auto">Our loan advisors will review your profile and contact you within 24 hours with personalized loan options.</p>
                    <div className="flex items-center justify-center gap-2 text-xs text-slate-500 mb-6">
                      <Shield className="w-3.5 h-3.5 text-accent-500" />
                      Your data is encrypted and secure
                    </div>
                    <button onClick={closeModal} className="btn-secondary text-sm">Done</button>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
