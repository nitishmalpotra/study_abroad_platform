import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ArrowRight, MapPin } from 'lucide-react';
import { countries } from '../data/countries';

const fadeUp = {
  hidden: { opacity: 0, y: 30 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: { delay: i * 0.08, duration: 0.5, ease: 'easeOut' as const },
  }),
};

export default function DestinationsPage() {
  return (
    <>
      <section className="bg-brand-900 pt-28 pb-16 lg:pt-36 lg:pb-20">
        <div className="container-max mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="max-w-2xl"
          >
            <h1 className="text-3xl lg:text-5xl font-bold text-white mb-4">
              Study Abroad Destinations
            </h1>
            <p className="text-lg text-brand-300">
              Detailed guides covering tuition costs, visa processes, living expenses, and top universities
              for the most popular study destinations.
            </p>
          </motion.div>
        </div>
      </section>

      <section className="section-padding bg-white">
        <div className="container-max mx-auto">
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {countries.map((country, i) => (
              <motion.div
                key={country.id}
                custom={i}
                variants={fadeUp}
                initial="hidden"
                whileInView="visible"
                viewport={{ once: true }}
              >
                <Link to={`/destinations/${country.id}`} className="card block overflow-hidden group h-full">
                  <div className="relative h-40 sm:h-52 overflow-hidden">
                    <img
                      src={country.heroImage}
                      alt={country.name}
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-black/20 to-transparent" />
                    <div className="absolute bottom-4 left-4 right-4">
                      <h3 className="text-xl font-bold text-white mb-1">{country.name}</h3>
                      <div className="flex items-center gap-1 text-sm text-white/70">
                        <MapPin className="w-3.5 h-3.5" />
                        {country.topUniversities.length} Top Universities
                      </div>
                    </div>
                  </div>
                  <div className="p-5">
                    <p className="text-sm text-slate-500 leading-relaxed mb-4">
                      {country.tagline}
                    </p>
                    <div className="space-y-2 mb-5">
                      <div className="flex justify-between text-sm">
                        <span className="text-slate-400">Avg. Tuition</span>
                        <span className="font-medium text-brand-800">{country.avgTuition}</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-slate-400">Avg. Living Cost</span>
                        <span className="font-medium text-brand-800">{country.avgLiving}</span>
                      </div>
                    </div>
                    <div className="flex flex-wrap gap-1.5">
                      {country.popularCourses.slice(0, 3).map((course) => (
                        <span
                          key={course}
                          className="text-xs px-2.5 py-1 bg-slate-100 text-slate-600 rounded-full"
                        >
                          {course}
                        </span>
                      ))}
                    </div>
                    <div className="mt-5 pt-4 border-t border-slate-100">
                      <span className="inline-flex items-center gap-1.5 text-sm font-medium text-brand-700 group-hover:text-accent-600 transition-colors">
                        Explore {country.name}
                        <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                      </span>
                    </div>
                  </div>
                </Link>
              </motion.div>
            ))}
          </div>
        </div>
      </section>
    </>
  );
}
