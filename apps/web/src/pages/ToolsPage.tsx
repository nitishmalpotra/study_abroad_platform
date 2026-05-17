import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Calculator, FileText, CheckSquare, ArrowRight, Target } from 'lucide-react';

const tools = [
  {
    icon: Calculator,
    title: 'EMI Calculator',
    desc: 'Calculate your monthly EMI, total interest payable, and get a complete amortization breakdown for your education loan.',
    path: '/tools/emi-calculator',
    color: 'bg-blue-50 text-blue-600',
    features: ['Real-time EMI calculation', 'Total interest breakdown', 'Adjustable sliders for loan parameters'],
  },
  {
    icon: FileText,
    title: 'AI SOP Review',
    desc: 'Paste your Statement of Purpose and get instant AI-powered feedback on grammar, structure, and impact with actionable suggestions.',
    path: '/tools/sop-review',
    color: 'bg-emerald-50 text-emerald-600',
    features: ['Grammar & clarity scoring', 'Structure analysis', 'Personalized improvement tips'],
  },
  {
    icon: CheckSquare,
    title: 'Planning Resources',
    desc: 'Access comprehensive checklists and planning guides for every stage of your study abroad journey.',
    path: '/tools/resources',
    color: 'bg-amber-50 text-amber-600',
    features: ['Visa timeline checklist', 'Cost of living estimator', 'GRE/GMAT prep checklist'],
  },
  {
    icon: Target,
    title: 'Admit Predictor',
    desc: 'Enter your academic profile and get a data-driven prediction of your admission chances at top universities worldwide.',
    path: '',
    color: 'bg-rose-50 text-rose-600',
    features: ['Profile-based predictions', 'University match scoring', 'Recommendations to improve odds'],
    comingSoon: true,
  },
];

const fadeUp = {
  hidden: { opacity: 0, y: 30 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: { delay: i * 0.1, duration: 0.5, ease: 'easeOut' as const },
  }),
};

export default function ToolsPage() {
  return (
    <>
      <section className="bg-brand-900 pt-28 pb-16 lg:pt-36 lg:pb-20">
        <div className="container-max mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="max-w-2xl">
            <h1 className="text-3xl lg:text-5xl font-bold text-white mb-4">Free Planning Tools</h1>
            <p className="text-lg text-brand-300">
              Make smarter decisions with our suite of free tools designed to help Indian students
              plan their study abroad journey with confidence.
            </p>
          </motion.div>
        </div>
      </section>

      <section className="section-padding bg-white">
        <div className="container-max mx-auto">
          <div className="grid md:grid-cols-2 gap-8">
            {tools.map((tool, i) => {
              const isComingSoon = 'comingSoon' in tool && tool.comingSoon;
              const Wrapper = isComingSoon ? 'div' : Link;
              const wrapperProps = isComingSoon
                ? { className: 'card block p-6 h-full group relative overflow-hidden cursor-default' }
                : { to: tool.path, className: 'card block p-6 h-full group' };

              return (
                <motion.div
                  key={tool.title}
                  custom={i}
                  variants={fadeUp}
                  initial="hidden"
                  whileInView="visible"
                  viewport={{ once: true }}
                >
                  {/* @ts-expect-error dynamic wrapper */}
                  <Wrapper {...wrapperProps}>
                    {isComingSoon && (
                      <div className="absolute top-4 right-4 px-3 py-1 bg-brand-900 text-white text-xs font-semibold rounded-full">
                        Coming Soon
                      </div>
                    )}
                    <div className={`w-14 h-14 rounded-2xl ${tool.color} flex items-center justify-center mb-5`}>
                      <tool.icon className="w-7 h-7" />
                    </div>
                    <h3 className="text-xl font-bold text-brand-900 mb-2 group-hover:text-accent-700 transition-colors">
                      {tool.title}
                    </h3>
                    <p className="text-sm text-slate-500 leading-relaxed mb-5">{tool.desc}</p>
                    <ul className="space-y-2 mb-6">
                      {tool.features.map((f) => (
                        <li key={f} className="flex items-center gap-2 text-sm text-slate-600">
                          <div className="w-1.5 h-1.5 bg-accent-500 rounded-full shrink-0" />
                          {f}
                        </li>
                      ))}
                    </ul>
                    {isComingSoon ? (
                      <span className="inline-flex items-center gap-1.5 text-sm font-semibold text-slate-400">
                        Launching Soon
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1.5 text-sm font-semibold text-brand-700 group-hover:text-accent-600 transition-colors">
                        Open Tool
                        <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                      </span>
                    )}
                  {/* @ts-expect-error dynamic wrapper */}
                  </Wrapper>
                </motion.div>
              );
            })}
          </div>
        </div>
      </section>
    </>
  );
}
