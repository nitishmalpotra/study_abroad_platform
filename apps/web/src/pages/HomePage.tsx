import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import {
  ChevronRight,
  Calculator,
  FileText,
  CheckSquare,
  ArrowRight,
  Shield,
  TrendingUp,
  Users,
  Star,
} from 'lucide-react';
import { useModal } from '../context/ModalContext';
import { countries } from '../data/countries';
import JourneySteps from '../components/home/JourneySteps';
import Testimonials from '../components/home/Testimonials';
import FAQ from '../components/home/FAQ';
import PartnerLogos from '../components/home/PartnerLogos';

const fadeUp = {
  hidden: { opacity: 0, y: 30 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: { delay: i * 0.1, duration: 0.5, ease: 'easeOut' as const },
  }),
};

const stats = [
  { icon: Users, value: '50,000+', label: 'Students Assisted' },
  { icon: TrendingUp, value: 'INR 2,500 Cr+', label: 'Loans Facilitated' },
  { icon: Star, value: '4.8/5', label: 'Student Rating' },
  { icon: Shield, value: '25+', label: 'Bank Partners' },
];

const tools = [
  {
    icon: Calculator,
    title: 'EMI Calculator',
    desc: 'Calculate your monthly payments instantly with real-time breakdowns of principal and interest.',
    path: '/tools/emi-calculator',
    color: 'bg-blue-50 text-blue-600',
  },
  {
    icon: FileText,
    title: 'AI SOP Review',
    desc: 'Get instant AI-powered feedback on your Statement of Purpose with grammar, structure, and impact scores.',
    path: '/tools/sop-review',
    color: 'bg-emerald-50 text-emerald-600',
  },
  {
    icon: CheckSquare,
    title: 'Planning Resources',
    desc: 'Download comprehensive checklists for visa timelines, cost estimation, and test preparation.',
    path: '/tools/resources',
    color: 'bg-amber-50 text-amber-600',
  },
];

export default function HomePage() {
  const { openModal } = useModal();

  return (
    <>
      <section className="relative bg-brand-900 overflow-hidden">
        <div className="absolute inset-0">
          <div className="absolute inset-0 bg-gradient-to-br from-brand-950 via-brand-900 to-brand-800" />
          <div className="absolute top-0 right-0 w-[600px] h-[600px] bg-accent-600/5 rounded-full blur-3xl" />
          <div className="absolute bottom-0 left-0 w-[400px] h-[400px] bg-brand-400/10 rounded-full blur-3xl" />
        </div>

        <div className="relative container-max mx-auto px-4 sm:px-6 lg:px-8 pt-32 pb-20 lg:pt-40 lg:pb-28">
          <div className="max-w-3xl">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              className="inline-flex items-center gap-2 px-4 py-1.5 bg-white/10 backdrop-blur-sm rounded-full border border-white/10 text-sm text-accent-300 mb-6"
            >
              <Shield className="w-3.5 h-3.5" />
              Trusted by 50,000+ Indian students
            </motion.div>

            <motion.h1
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.1 }}
              className="text-4xl sm:text-5xl lg:text-6xl font-bold text-white leading-[1.1] mb-6"
            >
              Fund Your Global
              <br />
              Dreams with{' '}
              <span className="text-accent-400">Confidence</span>
            </motion.h1>

            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="text-lg text-brand-200 max-w-xl mb-8 leading-relaxed"
            >
              Compare education loans from 25+ RBI-approved banks, explore top universities across 6 countries,
              and plan every step of your study abroad journey -- all in one place.
            </motion.p>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.3 }}
              className="flex flex-col sm:flex-row gap-4"
            >
              <button onClick={openModal} className="btn-primary text-base px-8 py-4">
                Check Loan Eligibility
                <ChevronRight className="w-5 h-5" />
              </button>
              <Link to="/tools" className="btn-outline border-white/30 text-white hover:bg-white hover:text-brand-900 text-base px-8 py-4">
                Explore Free Tools
              </Link>
            </motion.div>
          </div>
        </div>
      </section>

      <section className="bg-slate-50 border-b border-slate-200">
        <div className="container-max mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 lg:gap-8">
            {stats.map((stat, i) => (
              <motion.div
                key={stat.label}
                custom={i}
                variants={fadeUp}
                initial="hidden"
                whileInView="visible"
                viewport={{ once: true }}
                className="text-center"
              >
                <stat.icon className="w-5 h-5 text-accent-600 mx-auto mb-2" />
                <p className="text-2xl lg:text-3xl font-bold text-brand-900">{stat.value}</p>
                <p className="text-sm text-slate-500 mt-1">{stat.label}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      <PartnerLogos />

      <section className="section-padding bg-white">
        <div className="container-max mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-12"
          >
            <h2 className="text-3xl lg:text-4xl font-bold text-brand-900 mb-4">
              Free Tools to Plan Smarter
            </h2>
            <p className="text-slate-500 max-w-lg mx-auto">
              Make informed decisions with our suite of free planning tools built specifically for study abroad students.
            </p>
          </motion.div>

          <div className="grid md:grid-cols-3 gap-6">
            {tools.map((tool, i) => (
              <motion.div
                key={tool.title}
                custom={i}
                variants={fadeUp}
                initial="hidden"
                whileInView="visible"
                viewport={{ once: true }}
              >
                <Link to={tool.path} className="card block p-6 h-full group">
                  <div className={`w-12 h-12 rounded-xl ${tool.color} flex items-center justify-center mb-4`}>
                    <tool.icon className="w-6 h-6" />
                  </div>
                  <h3 className="text-lg font-semibold text-brand-900 mb-2 group-hover:text-accent-700 transition-colors">
                    {tool.title}
                  </h3>
                  <p className="text-sm text-slate-500 leading-relaxed mb-4">
                    {tool.desc}
                  </p>
                  <span className="inline-flex items-center gap-1 text-sm font-medium text-brand-700 group-hover:text-accent-600 transition-colors">
                    Try Now
                    <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                  </span>
                </Link>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      <JourneySteps />

      <section className="section-padding bg-slate-50">
        <div className="container-max mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="flex flex-col sm:flex-row items-start sm:items-end justify-between mb-12 gap-4"
          >
            <div>
              <h2 className="text-3xl lg:text-4xl font-bold text-brand-900 mb-4">
                Popular Destinations
              </h2>
              <p className="text-slate-500 max-w-lg">
                Explore detailed guides for the most popular study abroad destinations among Indian students.
              </p>
            </div>
            <Link
              to="/destinations"
              className="inline-flex items-center gap-1 text-sm font-medium text-brand-700 hover:text-accent-600 transition-colors whitespace-nowrap"
            >
              View All Destinations
              <ArrowRight className="w-4 h-4" />
            </Link>
          </motion.div>

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
                <Link to={`/destinations/${country.id}`} className="card block overflow-hidden group">
                  <div className="relative h-44 overflow-hidden">
                    <img
                      src={country.heroImage}
                      alt={country.name}
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent" />
                    <div className="absolute bottom-4 left-4">
                      <h3 className="text-lg font-bold text-white">{country.name}</h3>
                    </div>
                  </div>
                  <div className="p-5">
                    <p className="text-sm text-slate-500 leading-relaxed mb-4 line-clamp-2">
                      {country.tagline}
                    </p>
                    <div className="flex items-center justify-between text-xs text-slate-400">
                      <span>Tuition: {country.avgTuition}</span>
                      <ArrowRight className="w-4 h-4 text-brand-400 group-hover:translate-x-1 transition-transform" />
                    </div>
                  </div>
                </Link>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      <Testimonials />

      <FAQ />

      <section className="section-padding bg-brand-900">
        <div className="container-max mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <h2 className="text-3xl lg:text-4xl font-bold text-white mb-4">
              Ready to Start Your Journey?
            </h2>
            <p className="text-brand-300 max-w-lg mx-auto mb-8">
              Get personalized loan options from 25+ banks in under 2 minutes. No impact on your credit score.
            </p>
            <button onClick={openModal} className="btn-primary text-base px-8 py-4">
              Check Loan Eligibility -- It's Free
              <ChevronRight className="w-5 h-5" />
            </button>
            <div className="flex items-center justify-center gap-6 mt-6 text-xs text-brand-400">
              <span className="flex items-center gap-1.5">
                <Shield className="w-3.5 h-3.5 text-accent-500" />
                No credit score impact
              </span>
              <span className="flex items-center gap-1.5">
                <Shield className="w-3.5 h-3.5 text-accent-500" />
                100% free service
              </span>
            </div>
          </motion.div>
        </div>
      </section>
    </>
  );
}
