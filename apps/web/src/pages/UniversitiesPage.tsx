import { useState, useMemo } from 'react';
import { motion } from 'framer-motion';
import { Search, SlidersHorizontal, MapPin, Trophy, ChevronRight, X } from 'lucide-react';
import { universities } from '../data/universities';
import { useModal } from '../context/ModalContext';

const countryFilters = ['All', 'United States', 'United Kingdom', 'Canada', 'Australia', 'Ireland', 'New Zealand'];
const tuitionRanges = [
  { label: 'All Ranges', min: 0, max: Infinity },
  { label: 'Under $25,000', min: 0, max: 25000 },
  { label: '$25,000 - $40,000', min: 25000, max: 40000 },
  { label: '$40,000 - $55,000', min: 40000, max: 55000 },
  { label: 'Above $55,000', min: 55000, max: Infinity },
];

const fadeUp = {
  hidden: { opacity: 0, y: 20 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: { delay: i * 0.05, duration: 0.4, ease: 'easeOut' as const },
  }),
};

export default function UniversitiesPage() {
  const { openModal } = useModal();
  const [search, setSearch] = useState('');
  const [countryFilter, setCountryFilter] = useState('All');
  const [tuitionIdx, setTuitionIdx] = useState(0);
  const [showFilters, setShowFilters] = useState(false);

  const filtered = useMemo(() => {
    const range = tuitionRanges[tuitionIdx];
    return universities.filter((uni) => {
      const matchSearch = uni.name.toLowerCase().includes(search.toLowerCase()) ||
        uni.city.toLowerCase().includes(search.toLowerCase());
      const matchCountry = countryFilter === 'All' || uni.country === countryFilter;
      const matchTuition = uni.avgTuition >= range.min && uni.avgTuition < range.max;
      return matchSearch && matchCountry && matchTuition;
    });
  }, [search, countryFilter, tuitionIdx]);

  const activeFilters = (countryFilter !== 'All' ? 1 : 0) + (tuitionIdx !== 0 ? 1 : 0);

  return (
    <>
      <section className="bg-brand-900 pt-28 pb-16 lg:pt-36 lg:pb-20">
        <div className="container-max mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="max-w-2xl">
            <h1 className="text-3xl lg:text-5xl font-bold text-white mb-4">University Directory</h1>
            <p className="text-lg text-brand-300">
              Browse top universities worldwide. Compare tuition, rankings, and discover your best-fit institution.
            </p>
          </motion.div>
        </div>
      </section>

      <section className="section-padding bg-slate-50">
        <div className="container-max mx-auto">
          <div className="flex flex-col md:flex-row gap-4 mb-8">
            <div className="relative flex-1">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search universities or cities..."
                className="w-full pl-11 pr-4 py-3 bg-white border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent"
              />
            </div>
            <button
              onClick={() => setShowFilters(!showFilters)}
              className={`inline-flex items-center gap-2 px-5 py-3 rounded-xl border text-sm font-medium transition-colors ${
                showFilters || activeFilters > 0
                  ? 'bg-brand-800 text-white border-brand-800'
                  : 'bg-white text-slate-700 border-slate-200 hover:border-slate-300'
              }`}
            >
              <SlidersHorizontal className="w-4 h-4" />
              Filters
              {activeFilters > 0 && (
                <span className="w-5 h-5 bg-accent-500 text-white text-xs rounded-full flex items-center justify-center">
                  {activeFilters}
                </span>
              )}
            </button>
          </div>

          {showFilters && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="bg-white rounded-xl border border-slate-200 p-5 mb-8"
            >
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-semibold text-brand-800">Filters</h3>
                {activeFilters > 0 && (
                  <button
                    onClick={() => { setCountryFilter('All'); setTuitionIdx(0); }}
                    className="text-xs text-slate-500 hover:text-brand-700 flex items-center gap-1"
                  >
                    <X className="w-3 h-3" /> Clear all
                  </button>
                )}
              </div>
              <div className="space-y-4">
                <div>
                  <label className="text-xs font-medium text-slate-500 mb-2 block">Country</label>
                  <div className="flex flex-wrap gap-2">
                    {countryFilters.map((c) => (
                      <button
                        key={c}
                        onClick={() => setCountryFilter(c)}
                        className={`text-xs px-3 py-1.5 rounded-lg border transition-colors ${
                          countryFilter === c
                            ? 'bg-brand-800 text-white border-brand-800'
                            : 'bg-white text-slate-600 border-slate-200 hover:border-slate-300'
                        }`}
                      >
                        {c}
                      </button>
                    ))}
                  </div>
                </div>
                <div>
                  <label className="text-xs font-medium text-slate-500 mb-2 block">Tuition Range (USD equivalent)</label>
                  <div className="flex flex-wrap gap-2">
                    {tuitionRanges.map((r, i) => (
                      <button
                        key={r.label}
                        onClick={() => setTuitionIdx(i)}
                        className={`text-xs px-3 py-1.5 rounded-lg border transition-colors ${
                          tuitionIdx === i
                            ? 'bg-brand-800 text-white border-brand-800'
                            : 'bg-white text-slate-600 border-slate-200 hover:border-slate-300'
                        }`}
                      >
                        {r.label}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </motion.div>
          )}

          <p className="text-sm text-slate-500 mb-6">{filtered.length} universities found</p>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filtered.map((uni, i) => (
              <motion.div
                key={uni.id}
                custom={i}
                variants={fadeUp}
                initial="hidden"
                whileInView="visible"
                viewport={{ once: true }}
                className="card overflow-hidden group"
              >
                <div className="relative h-40 overflow-hidden">
                  <img
                    src={uni.image}
                    alt={uni.name}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                  />
                  <div className="absolute top-3 right-3 flex items-center gap-1 bg-white/90 backdrop-blur-sm px-2.5 py-1 rounded-lg">
                    <Trophy className="w-3.5 h-3.5 text-gold-500" />
                    <span className="text-xs font-semibold text-brand-800">#{uni.ranking}</span>
                  </div>
                </div>
                <div className="p-5">
                  <h3 className="text-base font-semibold text-brand-900 mb-1.5 group-hover:text-accent-700 transition-colors line-clamp-1">
                    {uni.name}
                  </h3>
                  <div className="flex items-center gap-1.5 text-sm text-slate-500 mb-3">
                    <MapPin className="w-3.5 h-3.5" />
                    {uni.city}, {uni.country}
                  </div>
                  <div className="flex items-center justify-between text-sm mb-4">
                    <div>
                      <p className="text-xs text-slate-400">Avg. Tuition</p>
                      <p className="font-semibold text-brand-800">{uni.tuitionDisplay}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-xs text-slate-400">Acceptance</p>
                      <p className="font-semibold text-brand-800">{uni.acceptanceRate}</p>
                    </div>
                  </div>
                  <div className="flex flex-wrap gap-1.5 mb-4">
                    {uni.programs.slice(0, 3).map((p) => (
                      <span key={p} className="text-xs px-2 py-0.5 bg-slate-100 text-slate-600 rounded">
                        {p}
                      </span>
                    ))}
                  </div>
                  <button
                    onClick={openModal}
                    className="btn-primary w-full text-sm py-2.5"
                  >
                    Check Loan Eligibility
                    <ChevronRight className="w-4 h-4" />
                  </button>
                </div>
              </motion.div>
            ))}
          </div>

          {filtered.length === 0 && (
            <div className="text-center py-16">
              <p className="text-lg font-medium text-slate-400">No universities match your filters.</p>
              <p className="text-sm text-slate-400 mt-1">Try adjusting your search or filter criteria.</p>
            </div>
          )}
        </div>
      </section>
    </>
  );
}
