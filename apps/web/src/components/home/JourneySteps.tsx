'use client';

import { motion } from 'framer-motion';
import Link from 'next/link';
import {
  Globe,
  BookOpen,
  FileText,
  Landmark,
  Stamp,
  Plane,
  ArrowRight,
} from 'lucide-react';

const steps = [
  {
    icon: Globe,
    number: '01',
    title: 'Explore',
    desc: 'Discover top destinations and universities that align with your academic goals, budget, and career aspirations.',
    color: 'bg-blue-50 text-blue-600 border-blue-100',
  },
  {
    icon: BookOpen,
    number: '02',
    title: 'Prepare',
    desc: 'Get ready for standardized tests like GRE, GMAT, IELTS, or TOEFL with structured study plans and curated resources.',
    color: 'bg-amber-50 text-amber-600 border-amber-100',
  },
  {
    icon: FileText,
    number: '03',
    title: 'Apply',
    desc: 'Craft a compelling SOP, gather your documents, and submit polished applications to your shortlisted universities.',
    color: 'bg-emerald-50 text-emerald-600 border-emerald-100',
  },
  {
    icon: Landmark,
    number: '04',
    title: 'Finance',
    desc: 'Compare education loan offers from 25+ RBI-approved banks and secure the best rates with zero service charges.',
    color: 'bg-cyan-50 text-cyan-600 border-cyan-100',
  },
  {
    icon: Stamp,
    number: '05',
    title: 'Visa',
    desc: 'Navigate the visa application process confidently with step-by-step timelines and document checklists.',
    color: 'bg-rose-50 text-rose-600 border-rose-100',
  },
  {
    icon: Plane,
    number: '06',
    title: 'Fly',
    desc: 'Finalize accommodation, complete your pre-departure checklist, and get ready to start your new chapter abroad.',
    color: 'bg-orange-50 text-orange-600 border-orange-100',
  },
];

const fadeUp = {
  hidden: { opacity: 0, y: 30 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: { delay: i * 0.08, duration: 0.45, ease: 'easeOut' as const },
  }),
};

export default function JourneySteps() {
  return (
    <section className="section-padding bg-white">
      <div className="container-max mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-14"
        >
          <span className="inline-block text-xs font-semibold text-accent-600 uppercase tracking-widest mb-3">
            Step-by-Step Guide
          </span>
          <h2 className="text-3xl lg:text-4xl font-bold text-brand-900 mb-4">
            Your Study Abroad Journey
          </h2>
          <p className="text-slate-500 max-w-xl mx-auto">
            From your first search to landing in your dream country -- here's every milestone mapped out for you.
          </p>
        </motion.div>

        <div className="relative">
          <div className="hidden lg:block absolute top-24 left-0 right-0 h-px bg-gradient-to-r from-transparent via-slate-200 to-transparent" />

          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6 lg:gap-8">
            {steps.map((step, i) => (
              <motion.div
                key={step.number}
                custom={i}
                variants={fadeUp}
                initial="hidden"
                whileInView="visible"
                viewport={{ once: true }}
                className="relative"
              >
                <div className="card p-6 h-full flex flex-col group hover:shadow-lg transition-shadow duration-300">
                  <div className="flex items-center gap-4 mb-4">
                    <div className={`w-12 h-12 rounded-xl border ${step.color} flex items-center justify-center shrink-0`}>
                      <step.icon className="w-6 h-6" />
                    </div>
                    <span className="text-3xl font-bold text-slate-100">{step.number}</span>
                  </div>

                  <h3 className="text-lg font-semibold text-brand-900 mb-2">{step.title}</h3>
                  <p className="text-sm text-slate-500 leading-relaxed flex-1">{step.desc}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>

        <motion.div
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mt-12"
        >
          <Link
            href="/tools/resources"
            className="btn-primary text-base px-8 py-4 inline-flex items-center gap-2"
          >
            Explore Planning Resources
            <ArrowRight className="w-5 h-5" />
          </Link>
        </motion.div>
      </div>
    </section>
  );
}
