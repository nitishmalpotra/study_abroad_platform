'use client';

import Link from 'next/link';
import { motion } from 'framer-motion';
import {
  DollarSign,
  GraduationCap,
  Plane,
  ChevronRight,
  MapPin,
  BookOpen,
  BadgeCheck,
} from 'lucide-react';
import { countries } from '../data/countries';
import { useModal } from '../context/ModalContext';

const fadeUp = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.5, ease: 'easeOut' as const } },
};

export default function CountryDetailPage({ id }: { id: string }) {
  const { openModal } = useModal();
  const country = countries.find((c) => c.id === id)!;

  return (
    <>
      <section className="relative bg-brand-900 pt-28 pb-16 lg:pt-36 lg:pb-20 overflow-hidden">
        <div className="absolute inset-0">
          <img
            src={country.heroImage}
            alt={country.name}
            className="w-full h-full object-cover opacity-20"
          />
          <div className="absolute inset-0 bg-gradient-to-r from-brand-900 via-brand-900/95 to-brand-900/70" />
        </div>
        <div className="relative container-max mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="max-w-2xl">
            <div className="flex items-center gap-2 text-sm text-brand-300 mb-4">
              <Link href="/destinations" className="hover:text-white transition-colors">Destinations</Link>
              <ChevronRight className="w-4 h-4" />
              <span className="text-white">{country.name}</span>
            </div>
            <h1 className="text-3xl lg:text-5xl font-bold text-white mb-4">
              Study in {country.name}
            </h1>
            <p className="text-lg text-brand-200 mb-6">{country.tagline}</p>
            <div className="flex flex-wrap gap-3">
              <button onClick={openModal} className="btn-primary">
                Check Loan Eligibility
                <ChevronRight className="w-4 h-4" />
              </button>
              <Link href="/universities" className="btn-outline border-white/30 text-white hover:bg-white hover:text-brand-900">
                Browse Universities
              </Link>
            </div>
          </motion.div>
        </div>
      </section>

      <section className="section-padding bg-white">
        <div className="container-max mx-auto">
          <div className="grid lg:grid-cols-3 gap-8">
            <div className="lg:col-span-2 space-y-12">
              <motion.div variants={fadeUp} initial="hidden" whileInView="visible" viewport={{ once: true }}>
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 bg-blue-50 rounded-xl flex items-center justify-center">
                    <BookOpen className="w-5 h-5 text-blue-600" />
                  </div>
                  <h2 className="text-2xl font-bold text-brand-900">Overview</h2>
                </div>
                <p className="text-slate-600 leading-relaxed">{country.overview}</p>
              </motion.div>

              <motion.div variants={fadeUp} initial="hidden" whileInView="visible" viewport={{ once: true }}>
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 bg-emerald-50 rounded-xl flex items-center justify-center">
                    <DollarSign className="w-5 h-5 text-emerald-600" />
                  </div>
                  <h2 className="text-2xl font-bold text-brand-900">Cost of Living</h2>
                </div>
                <div className="card overflow-hidden">
                  <div className="grid grid-cols-2 bg-slate-50 text-sm font-medium text-slate-500 px-5 py-3 border-b border-slate-200">
                    <span>Expense Category</span>
                    <span>Estimated Cost</span>
                  </div>
                  {country.costBreakdown.map((item, i) => (
                    <div
                      key={item.item}
                      className={`grid grid-cols-2 px-5 py-3.5 text-sm ${
                        i !== country.costBreakdown.length - 1 ? 'border-b border-slate-100' : ''
                      }`}
                    >
                      <span className="text-slate-600">{item.item}</span>
                      <span className="font-medium text-brand-800">{item.cost}</span>
                    </div>
                  ))}
                </div>
              </motion.div>

              <motion.div variants={fadeUp} initial="hidden" whileInView="visible" viewport={{ once: true }}>
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 bg-amber-50 rounded-xl flex items-center justify-center">
                    <Plane className="w-5 h-5 text-amber-600" />
                  </div>
                  <h2 className="text-2xl font-bold text-brand-900">Visa Process Highlights</h2>
                </div>
                <div className="space-y-3">
                  {country.visaHighlights.map((item) => (
                    <div key={item} className="flex items-start gap-3 p-4 bg-slate-50 rounded-xl">
                      <BadgeCheck className="w-5 h-5 text-accent-600 mt-0.5 shrink-0" />
                      <p className="text-sm text-slate-700">{item}</p>
                    </div>
                  ))}
                </div>
              </motion.div>

              <motion.div variants={fadeUp} initial="hidden" whileInView="visible" viewport={{ once: true }}>
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 bg-rose-50 rounded-xl flex items-center justify-center">
                    <GraduationCap className="w-5 h-5 text-rose-600" />
                  </div>
                  <h2 className="text-2xl font-bold text-brand-900">Top Universities</h2>
                </div>
                <div className="grid sm:grid-cols-2 gap-3">
                  {country.topUniversities.map((uni, i) => (
                    <div key={uni} className="flex items-center gap-3 p-4 card">
                      <div className="w-8 h-8 bg-brand-50 rounded-lg flex items-center justify-center text-sm font-bold text-brand-700">
                        {i + 1}
                      </div>
                      <span className="text-sm font-medium text-brand-800">{uni}</span>
                    </div>
                  ))}
                </div>
              </motion.div>
            </div>

            <div className="space-y-6">
              <motion.div
                variants={fadeUp}
                initial="hidden"
                whileInView="visible"
                viewport={{ once: true }}
                className="card p-6 sticky top-24"
              >
                <h3 className="text-lg font-bold text-brand-900 mb-4">Quick Facts</h3>
                <div className="space-y-4">
                  <div className="flex items-center gap-3 pb-4 border-b border-slate-100">
                    <MapPin className="w-4 h-4 text-slate-400" />
                    <div>
                      <p className="text-xs text-slate-400">Currency</p>
                      <p className="text-sm font-medium text-brand-800">{country.currency}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3 pb-4 border-b border-slate-100">
                    <DollarSign className="w-4 h-4 text-slate-400" />
                    <div>
                      <p className="text-xs text-slate-400">Avg. Tuition</p>
                      <p className="text-sm font-medium text-brand-800">{country.avgTuition}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3 pb-4 border-b border-slate-100">
                    <DollarSign className="w-4 h-4 text-slate-400" />
                    <div>
                      <p className="text-xs text-slate-400">Avg. Living Cost</p>
                      <p className="text-sm font-medium text-brand-800">{country.avgLiving}</p>
                    </div>
                  </div>
                </div>

                <div className="mt-6">
                  <h4 className="text-sm font-semibold text-brand-800 mb-3">Popular Courses</h4>
                  <div className="flex flex-wrap gap-1.5">
                    {country.popularCourses.map((course) => (
                      <span
                        key={course}
                        className="text-xs px-2.5 py-1 bg-brand-50 text-brand-700 rounded-full"
                      >
                        {course}
                      </span>
                    ))}
                  </div>
                </div>

                <button
                  onClick={openModal}
                  className="btn-primary w-full mt-6 text-sm"
                >
                  Check Loan Eligibility
                  <ChevronRight className="w-4 h-4" />
                </button>
              </motion.div>
            </div>
          </div>
        </div>
      </section>
    </>
  );
}
