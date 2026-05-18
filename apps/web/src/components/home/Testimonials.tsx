'use client';

import { motion } from 'framer-motion';
import { Star, Quote } from 'lucide-react';

const testimonials = [
  {
    name: 'Priya Sharma',
    university: 'University of Toronto',
    country: 'Canada',
    course: 'MS Data Science',
    image: 'https://images.pexels.com/photos/3769021/pexels-photo-3769021.jpeg?auto=compress&cs=tinysrgb&w=150&h=150&fit=crop',
    quote: 'KlassFin made my entire study abroad journey incredibly smooth. I compared offers from 8 banks and saved over INR 2 lakhs in interest. The EMI calculator helped me plan my finances perfectly.',
    rating: 5,
  },
  {
    name: 'Arjun Mehta',
    university: 'Georgia Tech',
    country: 'United States',
    course: 'MS Computer Science',
    image: 'https://images.pexels.com/photos/2379004/pexels-photo-2379004.jpeg?auto=compress&cs=tinysrgb&w=150&h=150&fit=crop',
    quote: 'The SOP review tool gave me actionable feedback that genuinely improved my application. I got admits from 4 out of 5 universities I applied to. Highly recommend the planning resources!',
    rating: 5,
  },
  {
    name: 'Sneha Reddy',
    university: 'University of Melbourne',
    country: 'Australia',
    course: 'MBA',
    image: 'https://images.pexels.com/photos/3756679/pexels-photo-3756679.jpeg?auto=compress&cs=tinysrgb&w=150&h=150&fit=crop',
    quote: 'From shortlisting universities to getting my visa stamped, KlassFin was with me at every step. The visa timeline checklist alone saved me weeks of confusion and stress.',
    rating: 5,
  },
  {
    name: 'Rahul Patel',
    university: 'Trinity College Dublin',
    country: 'Ireland',
    course: 'MS Finance',
    image: 'https://images.pexels.com/photos/1222271/pexels-photo-1222271.jpeg?auto=compress&cs=tinysrgb&w=150&h=150&fit=crop',
    quote: 'I was confused about education loans until I found KlassFin. They helped me find the best rates when other platforms were quoting much higher. The process was completely transparent.',
    rating: 5,
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

export default function Testimonials() {
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
            Student Stories
          </span>
          <h2 className="text-3xl lg:text-4xl font-bold text-brand-900 mb-4">
            Trusted by Thousands of Students
          </h2>
          <p className="text-slate-500 max-w-lg mx-auto">
            Hear from students who successfully navigated their study abroad journey with KlassFin.
          </p>
        </motion.div>

        <div className="grid md:grid-cols-2 gap-6 lg:gap-8">
          {testimonials.map((t, i) => (
            <motion.div
              key={t.name}
              custom={i}
              variants={fadeUp}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true }}
              className="card p-6 lg:p-8 relative group hover:shadow-lg transition-shadow duration-300"
            >
              <Quote className="absolute top-6 right-6 w-8 h-8 text-slate-100 group-hover:text-accent-100 transition-colors" />

              <div className="flex items-center gap-1 mb-4">
                {Array.from({ length: t.rating }).map((_, idx) => (
                  <Star key={idx} className="w-4 h-4 fill-amber-400 text-amber-400" />
                ))}
              </div>

              <p className="text-sm text-slate-600 leading-relaxed mb-6 relative z-10">
                "{t.quote}"
              </p>

              <div className="flex items-center gap-4 pt-5 border-t border-slate-100">
                <img
                  src={t.image}
                  alt={t.name}
                  className="w-12 h-12 rounded-full object-cover ring-2 ring-white shadow-sm"
                />
                <div className="min-w-0">
                  <p className="text-sm font-semibold text-brand-900">{t.name}</p>
                  <p className="text-xs text-slate-500 truncate">{t.course}, {t.university}</p>
                  <p className="text-xs text-slate-400 truncate">{t.country}</p>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
