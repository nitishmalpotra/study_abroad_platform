import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown } from 'lucide-react';

const faqs = [
  {
    question: 'How does KlassFin help with education loans?',
    answer:
      'KlassFin partners with 25+ RBI-approved banks and NBFCs to bring you pre-negotiated education loan offers. We compare interest rates, processing fees, and repayment terms across lenders so you can choose the best option -- all from a single platform. We guide you through the entire process from eligibility check to disbursement.',
  },
  {
    question: 'Does KlassFin charge any fees for its services?',
    answer:
      'No. KlassFin is completely free for students. We do not charge any service fees, processing fees, or hidden costs. Our revenue comes from our banking partners, so you never pay a single rupee for using our loan comparison, tools, or planning resources.',
  },
  {
    question: 'What is KlassFin and what do you offer?',
    answer:
      'KlassFin is an all-in-one study abroad platform for Indian students. Beyond education loan comparison, we provide free tools like an EMI calculator, AI-powered SOP review, and downloadable planning resources -- covering everything from university shortlisting to visa preparation.',
  },
  {
    question: 'How do education loans for studying abroad work?',
    answer:
      'Education loans cover tuition fees, living expenses, travel, and other costs. Most banks offer loans up to INR 1 crore for top-ranked universities. You typically start repaying after a moratorium period (course duration + 6-12 months). Interest rates range from 8% to 13% depending on the bank, collateral, and university ranking.',
  },
  {
    question: 'Do I need collateral for an education loan?',
    answer:
      'It depends on the loan amount and the lender. Loans up to INR 7.5 lakhs are generally collateral-free. For higher amounts, banks may require property or fixed deposits as security. Some NBFCs offer collateral-free loans up to INR 40-75 lakhs for admits from top-ranked universities.',
  },
  {
    question: 'Will checking my loan eligibility on KlassFin affect my credit score?',
    answer:
      'No. Our eligibility check is a soft inquiry that does not impact your credit score in any way. A hard credit check only happens once you formally apply with a specific bank, and we always inform you before that step.',
  },
  {
    question: 'How long does it take to get a loan sanctioned?',
    answer:
      'Once you submit your documents, most banks process education loan applications within 7 to 15 working days. KlassFin helps speed this up by ensuring your application is complete and error-free before submission, avoiding common delays.',
  },
];

export default function FAQ() {
  const [openIndex, setOpenIndex] = useState<number | null>(null);

  const toggle = (i: number) => {
    setOpenIndex(openIndex === i ? null : i);
  };

  return (
    <section className="section-padding bg-slate-50">
      <div className="container-max mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-14"
        >
          <span className="inline-block text-xs font-semibold text-accent-600 uppercase tracking-widest mb-3">
            Common Questions
          </span>
          <h2 className="text-3xl lg:text-4xl font-bold text-brand-900 mb-4">
            Frequently Asked Questions
          </h2>
          <p className="text-slate-500 max-w-lg mx-auto">
            Everything you need to know about education loans, our platform, and how we can help you.
          </p>
        </motion.div>

        <div className="max-w-3xl mx-auto space-y-3">
          {faqs.map((faq, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.04, duration: 0.35 }}
            >
              <button
                onClick={() => toggle(i)}
                className={`w-full flex items-center justify-between text-left p-5 rounded-xl transition-all duration-200 ${
                  openIndex === i
                    ? 'bg-white shadow-md ring-1 ring-slate-200'
                    : 'bg-white shadow-sm hover:shadow-md ring-1 ring-slate-100 hover:ring-slate-200'
                }`}
              >
                <span className="text-sm font-semibold text-brand-900 pr-6">{faq.question}</span>
                <ChevronDown
                  className={`w-5 h-5 text-slate-400 shrink-0 transition-transform duration-200 ${
                    openIndex === i ? 'rotate-180' : ''
                  }`}
                />
              </button>
              <AnimatePresence initial={false}>
                {openIndex === i && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.25, ease: 'easeInOut' }}
                    className="overflow-hidden"
                  >
                    <div className="px-5 pb-5 pt-2">
                      <p className="text-sm text-slate-600 leading-relaxed">{faq.answer}</p>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
