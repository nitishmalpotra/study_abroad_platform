'use client';

import { useState, useMemo } from 'react';
import { motion } from 'framer-motion';
import Link from 'next/link';
import { ChevronRight, IndianRupee, Percent, Clock, TrendingUp, ChevronDown, ChevronUp } from 'lucide-react';
import { useModal } from '../context/ModalContext';

function formatINR(num: number): string {
  return num.toLocaleString('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 });
}

export default function EMICalculatorPage() {
  const { openModal } = useModal();
  const [loanAmount, setLoanAmount] = useState(2000000);
  const [interestRate, setInterestRate] = useState(9.5);
  const [tenure, setTenure] = useState(10);
  const [showSchedule, setShowSchedule] = useState(false);

  const result = useMemo(() => {
    const p = loanAmount;
    const r = interestRate / 12 / 100;
    const n = tenure * 12;
    const emi = (p * r * Math.pow(1 + r, n)) / (Math.pow(1 + r, n) - 1);
    const totalPayable = emi * n;
    const totalInterest = totalPayable - p;

    const schedule: { year: number; principal: number; interest: number; balance: number }[] = [];
    let balance = p;
    for (let year = 1; year <= tenure; year++) {
      let yearPrincipal = 0;
      let yearInterest = 0;
      for (let month = 0; month < 12; month++) {
        const monthInterest = balance * r;
        const monthPrincipal = emi - monthInterest;
        yearPrincipal += monthPrincipal;
        yearInterest += monthInterest;
        balance -= monthPrincipal;
      }
      schedule.push({
        year,
        principal: Math.round(yearPrincipal),
        interest: Math.round(yearInterest),
        balance: Math.max(0, Math.round(balance)),
      });
    }

    return {
      emi: Math.round(emi),
      totalPayable: Math.round(totalPayable),
      totalInterest: Math.round(totalInterest),
      principalPercent: Math.round((p / totalPayable) * 100),
      interestPercent: Math.round((totalInterest / totalPayable) * 100),
      schedule,
    };
  }, [loanAmount, interestRate, tenure]);

  return (
    <>
      <section className="bg-brand-900 pt-28 pb-16 lg:pt-36 lg:pb-20">
        <div className="container-max mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="max-w-2xl">
            <div className="flex items-center gap-2 text-sm text-brand-300 mb-4">
              <Link href="/tools" className="hover:text-white transition-colors">Tools</Link>
              <ChevronRight className="w-4 h-4" />
              <span className="text-white">EMI Calculator</span>
            </div>
            <h1 className="text-3xl lg:text-5xl font-bold text-white mb-4">EMI Calculator</h1>
            <p className="text-lg text-brand-300">
              Calculate your monthly education loan EMI and understand the complete cost of borrowing.
            </p>
          </motion.div>
        </div>
      </section>

      <section className="section-padding bg-slate-50">
        <div className="container-max mx-auto">
          <div className="grid lg:grid-cols-5 gap-8">
            <div className="lg:col-span-3 space-y-6">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="card p-6"
              >
                <div className="space-y-8">
                  <div>
                    <div className="flex items-center justify-between mb-3">
                      <label className="flex items-center gap-2 text-sm font-medium text-slate-700">
                        <IndianRupee className="w-4 h-4 text-slate-400" />
                        Loan Amount
                      </label>
                      <span className="text-sm font-bold text-brand-800">{formatINR(loanAmount)}</span>
                    </div>
                    <input
                      type="range"
                      min={100000}
                      max={10000000}
                      step={100000}
                      value={loanAmount}
                      onChange={(e) => setLoanAmount(Number(e.target.value))}
                      className="w-full h-2 bg-slate-200 rounded-full appearance-none cursor-pointer accent-brand-800"
                    />
                    <div className="flex justify-between text-xs text-slate-400 mt-1">
                      <span>INR 1L</span>
                      <span>INR 1Cr</span>
                    </div>
                  </div>

                  <div>
                    <div className="flex items-center justify-between mb-3">
                      <label className="flex items-center gap-2 text-sm font-medium text-slate-700">
                        <Percent className="w-4 h-4 text-slate-400" />
                        Interest Rate (per annum)
                      </label>
                      <span className="text-sm font-bold text-brand-800">{interestRate}%</span>
                    </div>
                    <input
                      type="range"
                      min={5}
                      max={18}
                      step={0.1}
                      value={interestRate}
                      onChange={(e) => setInterestRate(Number(e.target.value))}
                      className="w-full h-2 bg-slate-200 rounded-full appearance-none cursor-pointer accent-brand-800"
                    />
                    <div className="flex justify-between text-xs text-slate-400 mt-1">
                      <span>5%</span>
                      <span>18%</span>
                    </div>
                  </div>

                  <div>
                    <div className="flex items-center justify-between mb-3">
                      <label className="flex items-center gap-2 text-sm font-medium text-slate-700">
                        <Clock className="w-4 h-4 text-slate-400" />
                        Loan Tenure
                      </label>
                      <span className="text-sm font-bold text-brand-800">{tenure} years</span>
                    </div>
                    <input
                      type="range"
                      min={1}
                      max={20}
                      step={1}
                      value={tenure}
                      onChange={(e) => setTenure(Number(e.target.value))}
                      className="w-full h-2 bg-slate-200 rounded-full appearance-none cursor-pointer accent-brand-800"
                    />
                    <div className="flex justify-between text-xs text-slate-400 mt-1">
                      <span>1 year</span>
                      <span>20 years</span>
                    </div>
                  </div>
                </div>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
              >
                <button
                  onClick={() => setShowSchedule(!showSchedule)}
                  className="flex items-center gap-2 text-sm font-medium text-brand-700 hover:text-brand-900 mb-4"
                >
                  {showSchedule ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                  {showSchedule ? 'Hide' : 'Show'} Year-wise Breakdown
                </button>

                {showSchedule && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    className="card overflow-hidden"
                  >
                    <div className="grid grid-cols-4 text-xs font-medium text-slate-500 px-5 py-3 bg-slate-50 border-b border-slate-200">
                      <span>Year</span>
                      <span>Principal</span>
                      <span>Interest</span>
                      <span>Balance</span>
                    </div>
                    {result.schedule.map((row) => (
                      <div
                        key={row.year}
                        className="grid grid-cols-4 text-sm px-5 py-3 border-b border-slate-50 last:border-0"
                      >
                        <span className="font-medium text-brand-800">Year {row.year}</span>
                        <span className="text-slate-600">{formatINR(row.principal)}</span>
                        <span className="text-slate-600">{formatINR(row.interest)}</span>
                        <span className="text-slate-600">{formatINR(row.balance)}</span>
                      </div>
                    ))}
                  </motion.div>
                )}
              </motion.div>
            </div>

            <div className="lg:col-span-2">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.15 }}
                className="card p-6 sticky top-24"
              >
                <h3 className="text-lg font-bold text-brand-900 mb-6">Your Loan Summary</h3>

                <div className="bg-brand-800 rounded-xl p-5 mb-6">
                  <p className="text-sm text-brand-200 mb-1">Monthly EMI</p>
                  <p className="text-3xl font-bold text-white">{formatINR(result.emi)}</p>
                </div>

                <div className="space-y-4 mb-6">
                  <div className="flex items-center justify-between py-3 border-b border-slate-100">
                    <span className="text-sm text-slate-500">Principal Amount</span>
                    <span className="text-sm font-semibold text-brand-800">{formatINR(loanAmount)}</span>
                  </div>
                  <div className="flex items-center justify-between py-3 border-b border-slate-100">
                    <span className="text-sm text-slate-500">Total Interest</span>
                    <span className="text-sm font-semibold text-brand-800">{formatINR(result.totalInterest)}</span>
                  </div>
                  <div className="flex items-center justify-between py-3">
                    <span className="text-sm font-medium text-slate-700">Total Payable</span>
                    <span className="text-sm font-bold text-brand-900">{formatINR(result.totalPayable)}</span>
                  </div>
                </div>

                <div className="mb-6">
                  <div className="flex items-center gap-4 text-xs mb-2">
                    <div className="flex items-center gap-1.5">
                      <div className="w-3 h-3 bg-brand-800 rounded-sm" />
                      <span className="text-slate-500">Principal ({result.principalPercent}%)</span>
                    </div>
                    <div className="flex items-center gap-1.5">
                      <div className="w-3 h-3 bg-accent-400 rounded-sm" />
                      <span className="text-slate-500">Interest ({result.interestPercent}%)</span>
                    </div>
                  </div>
                  <div className="h-4 bg-slate-100 rounded-full overflow-hidden flex">
                    <div
                      className="bg-brand-800 h-full transition-all duration-500"
                      style={{ width: `${result.principalPercent}%` }}
                    />
                    <div
                      className="bg-accent-400 h-full transition-all duration-500"
                      style={{ width: `${result.interestPercent}%` }}
                    />
                  </div>
                </div>

                <button onClick={openModal} className="btn-primary w-full text-sm">
                  <TrendingUp className="w-4 h-4" />
                  Get Best Loan Rates
                </button>
              </motion.div>
            </div>
          </div>
        </div>
      </section>
    </>
  );
}
