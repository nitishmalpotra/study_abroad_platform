import { useState } from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import {
  ChevronRight,
  Download,
  Plane,
  DollarSign,
  BookOpen,
  Calendar,
  FileCheck,
  ClipboardList,
} from 'lucide-react';
import ResourceLeadModal from '../components/ResourceLeadModal';

const resources = [
  {
    icon: DollarSign,
    title: 'Cost of Living Estimator',
    desc: 'A comprehensive spreadsheet to estimate your monthly and yearly living expenses across 6 countries, including accommodation, food, transport, and insurance.',
    category: 'Financial Planning',
    color: 'bg-emerald-50 text-emerald-600',
  },
  {
    icon: Plane,
    title: 'Visa Application Timeline',
    desc: 'A detailed week-by-week checklist covering document preparation, application submission, biometrics, and interview scheduling for all major student visas.',
    category: 'Visa',
    color: 'bg-blue-50 text-blue-600',
  },
  {
    icon: BookOpen,
    title: 'GRE Preparation Checklist',
    desc: 'A 90-day structured study plan with daily targets, practice test schedules, and recommended resources for achieving a 320+ GRE score.',
    category: 'Test Prep',
    color: 'bg-amber-50 text-amber-600',
  },
  {
    icon: ClipboardList,
    title: 'GMAT Study Plan',
    desc: 'Complete 12-week preparation guide for the GMAT with section-wise strategies, time management tips, and links to free practice resources.',
    category: 'Test Prep',
    color: 'bg-rose-50 text-rose-600',
  },
  {
    icon: FileCheck,
    title: 'University Application Tracker',
    desc: 'Organize your applications to multiple universities with deadline tracking, document status, and application fee management in one spreadsheet.',
    category: 'Admissions',
    color: 'bg-cyan-50 text-cyan-600',
  },
  {
    icon: Calendar,
    title: 'Pre-Departure Checklist',
    desc: 'Everything you need to do before leaving India: from forex cards and travel insurance to accommodation booking and airport essentials.',
    category: 'Planning',
    color: 'bg-orange-50 text-orange-600',
  },
];

const fadeUp = {
  hidden: { opacity: 0, y: 20 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: { delay: i * 0.08, duration: 0.4, ease: 'easeOut' as const },
  }),
};

export default function ResourcesPage() {
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedResource, setSelectedResource] = useState('');

  const handleDownloadClick = (title: string) => {
    setSelectedResource(title);
    setModalOpen(true);
  };

  return (
    <>
      <section className="bg-brand-900 pt-28 pb-16 lg:pt-36 lg:pb-20">
        <div className="container-max mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="max-w-2xl">
            <div className="flex items-center gap-2 text-sm text-brand-300 mb-4">
              <Link to="/tools" className="hover:text-white transition-colors">Resources</Link>
              <ChevronRight className="w-4 h-4" />
              <span className="text-white">Planning Resources</span>
            </div>
            <h1 className="text-3xl lg:text-5xl font-bold text-white mb-4">Planning Resources</h1>
            <p className="text-lg text-brand-300">
              Download free checklists, planners, and guides to stay organized throughout your study abroad journey.
            </p>
          </motion.div>
        </div>
      </section>

      <section className="section-padding bg-white">
        <div className="container-max mx-auto">
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {resources.map((resource, i) => (
              <motion.div
                key={resource.title}
                custom={i}
                variants={fadeUp}
                initial="hidden"
                whileInView="visible"
                viewport={{ once: true }}
                className="card p-6 flex flex-col"
              >
                <div className="flex items-start gap-4 mb-4">
                  <div className={`w-12 h-12 rounded-xl ${resource.color} flex items-center justify-center shrink-0`}>
                    <resource.icon className="w-6 h-6" />
                  </div>
                  <div>
                    <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">
                      {resource.category}
                    </span>
                    <h3 className="text-base font-semibold text-brand-900 mt-0.5">{resource.title}</h3>
                  </div>
                </div>
                <p className="text-sm text-slate-500 leading-relaxed mb-5 flex-1">
                  {resource.desc}
                </p>
                <button
                  onClick={() => handleDownloadClick(resource.title)}
                  className="btn-outline w-full text-sm py-2.5 border-slate-200 text-slate-700 hover:bg-brand-700 hover:border-brand-700"
                >
                  <Download className="w-4 h-4" />
                  Download Checklist
                </button>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      <ResourceLeadModal
        isOpen={modalOpen}
        resourceName={selectedResource}
        onClose={() => setModalOpen(false)}
      />
    </>
  );
}
