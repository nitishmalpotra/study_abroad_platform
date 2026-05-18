'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import Link from 'next/link';
import { Clock, ArrowRight, User, Search } from 'lucide-react';
import { blogPosts } from '../data/blog';

const fadeUp = {
  hidden: { opacity: 0, y: 20 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: { delay: i * 0.06, duration: 0.4, ease: 'easeOut' as const },
  }),
};

const categoryColors: Record<string, string> = {
  Loans: 'bg-emerald-50 text-emerald-700',
  Universities: 'bg-blue-50 text-blue-700',
  Visa: 'bg-amber-50 text-amber-700',
  'Test Prep': 'bg-rose-50 text-rose-700',
  Scholarships: 'bg-cyan-50 text-cyan-700',
  Admissions: 'bg-orange-50 text-orange-700',
  Destinations: 'bg-slate-100 text-slate-700',
};

const categories = ['All', ...Object.keys(categoryColors)];

export default function BlogPage() {
  const [activeCategory, setActiveCategory] = useState('All');
  const [searchQuery, setSearchQuery] = useState('');

  const filtered = blogPosts.filter((post) => {
    const matchesCategory = activeCategory === 'All' || post.category === activeCategory;
    const matchesSearch =
      searchQuery === '' ||
      post.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      post.excerpt.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  const featured = filtered[0];
  const rest = filtered.slice(1);

  return (
    <>
      <section className="bg-brand-900 pt-28 pb-16 lg:pt-36 lg:pb-20">
        <div className="container-max mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="max-w-2xl">
            <h1 className="text-3xl lg:text-5xl font-bold text-white mb-4">Blog & Guides</h1>
            <p className="text-lg text-brand-300">
              Expert advice on education loans, visa processes, test preparation, and everything you need
              to know about studying abroad from India.
            </p>
          </motion.div>
        </div>
      </section>

      <section className="section-padding bg-white">
        <div className="container-max mx-auto">
          <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4 mb-10">
            <div className="flex flex-wrap items-center gap-2">
              {categories.map((cat) => (
                <button
                  key={cat}
                  onClick={() => setActiveCategory(cat)}
                  className={`px-4 py-2 rounded-full text-sm font-medium transition-all duration-200 ${
                    activeCategory === cat
                      ? 'bg-brand-900 text-white shadow-sm'
                      : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                  }`}
                >
                  {cat}
                </button>
              ))}
            </div>
            <div className="relative w-full lg:w-72">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
              <input
                type="text"
                placeholder="Search articles..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2.5 rounded-lg border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 transition-all"
              />
            </div>
          </div>

          {filtered.length === 0 && (
            <div className="text-center py-20">
              <p className="text-slate-400 text-lg">No articles found matching your criteria.</p>
            </div>
          )}

          {featured && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              className="mb-12"
            >
              <Link href={`/blog/${featured.id}`} className="card overflow-hidden block group">
                <div className="grid md:grid-cols-2">
                  <div className="relative h-64 md:h-80 overflow-hidden">
                    <img
                      src={featured.image}
                      alt={featured.title}
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-700"
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent md:hidden" />
                  </div>
                  <div className="p-6 md:p-10 flex flex-col justify-center">
                    <span className={`inline-block text-xs font-medium px-2.5 py-1 rounded-full mb-4 w-fit ${categoryColors[featured.category] || 'bg-slate-100 text-slate-700'}`}>
                      {featured.category}
                    </span>
                    <h2 className="text-xl md:text-2xl lg:text-3xl font-bold text-brand-900 mb-3 leading-snug group-hover:text-accent-700 transition-colors">
                      {featured.title}
                    </h2>
                    <p className="text-sm text-slate-500 leading-relaxed mb-6 line-clamp-3">{featured.excerpt}</p>
                    <div className="flex items-center gap-4 text-xs text-slate-400">
                      <span className="flex items-center gap-1.5">
                        <User className="w-3.5 h-3.5" />
                        {featured.author}
                      </span>
                      <span>{featured.date}</span>
                      <span className="flex items-center gap-1.5">
                        <Clock className="w-3.5 h-3.5" />
                        {featured.readTime}
                      </span>
                    </div>
                  </div>
                </div>
              </Link>
            </motion.div>
          )}

          {rest.length > 0 && (
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {rest.map((post, i) => (
                <motion.article
                  key={post.id}
                  custom={i}
                  variants={fadeUp}
                  initial="hidden"
                  whileInView="visible"
                  viewport={{ once: true }}
                >
                  <Link href={`/blog/${post.id}`} className="card overflow-hidden group block h-full">
                    <div className="relative h-44 overflow-hidden">
                      <img
                        src={post.image}
                        alt={post.title}
                        className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                      />
                      <span className={`absolute top-3 left-3 text-xs font-medium px-2.5 py-1 rounded-full ${categoryColors[post.category] || 'bg-slate-100 text-slate-700'}`}>
                        {post.category}
                      </span>
                    </div>
                    <div className="p-5">
                      <h3 className="text-base font-semibold text-brand-900 mb-2 leading-snug group-hover:text-accent-700 transition-colors line-clamp-2">
                        {post.title}
                      </h3>
                      <p className="text-sm text-slate-500 leading-relaxed mb-4 line-clamp-2">
                        {post.excerpt}
                      </p>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3 text-xs text-slate-400">
                          <span>{post.date}</span>
                          <span className="flex items-center gap-1">
                            <Clock className="w-3 h-3" />
                            {post.readTime}
                          </span>
                        </div>
                        <ArrowRight className="w-4 h-4 text-slate-300 group-hover:text-accent-600 group-hover:translate-x-1 transition-all" />
                      </div>
                    </div>
                  </Link>
                </motion.article>
              ))}
            </div>
          )}
        </div>
      </section>
    </>
  );
}
