'use client';

import Link from 'next/link';
import { motion } from 'framer-motion';
import { ArrowLeft, Clock, User, Calendar, Tag, ChevronRight } from 'lucide-react';
import { blogPosts } from '../data/blog';
import { useModal } from '../context/ModalContext';

const categoryColors: Record<string, string> = {
  Loans: 'bg-emerald-50 text-emerald-700',
  Universities: 'bg-blue-50 text-blue-700',
  Visa: 'bg-amber-50 text-amber-700',
  'Test Prep': 'bg-rose-50 text-rose-700',
  Scholarships: 'bg-cyan-50 text-cyan-700',
  Admissions: 'bg-orange-50 text-orange-700',
  Destinations: 'bg-slate-100 text-slate-700',
};

export default function BlogPostPage({ id }: { id: string }) {
  const { openModal } = useModal();
  const post = blogPosts.find((p) => p.id === id)!;

  const relatedPosts = blogPosts
    .filter((p) => p.id !== post.id && (p.category === post.category || p.tags.some((t) => post.tags.includes(t))))
    .slice(0, 3);

  return (
    <>
      <section className="bg-brand-900 pt-28 pb-12 lg:pt-36 lg:pb-16">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
            <Link
              href="/blog"
              className="inline-flex items-center gap-1.5 text-sm text-brand-300 hover:text-white transition-colors mb-6"
            >
              <ArrowLeft className="w-4 h-4" />
              Back to Blog
            </Link>

            <span className={`inline-block text-xs font-medium px-3 py-1 rounded-full mb-4 ${categoryColors[post.category] || 'bg-slate-100 text-slate-700'}`}>
              {post.category}
            </span>

            <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold text-white leading-tight mb-6">
              {post.title}
            </h1>

            <div className="flex flex-wrap items-center gap-x-5 gap-y-2 text-sm text-brand-300">
              <span className="flex items-center gap-1.5">
                <User className="w-4 h-4" />
                {post.author}
                <span className="text-brand-500 ml-1">{post.authorRole}</span>
              </span>
              <span className="flex items-center gap-1.5">
                <Calendar className="w-4 h-4" />
                {post.date}
              </span>
              <span className="flex items-center gap-1.5">
                <Clock className="w-4 h-4" />
                {post.readTime}
              </span>
            </div>
          </motion.div>
        </div>
      </section>

      <section className="bg-white">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="relative -mt-2"
          >
            <div className="rounded-xl overflow-hidden shadow-lg mb-10">
              <img
                src={post.image}
                alt={post.title}
                className="w-full h-64 sm:h-80 lg:h-96 object-cover"
              />
            </div>
          </motion.div>
        </div>
      </section>

      <section className="bg-white pb-16 lg:pb-24">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.article
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
            className="prose-article"
            dangerouslySetInnerHTML={{ __html: post.content }}
          />

          <div className="flex flex-wrap items-center gap-2 mt-10 pt-8 border-t border-slate-200">
            <Tag className="w-4 h-4 text-slate-400" />
            {post.tags.map((tag) => (
              <span
                key={tag}
                className="px-3 py-1 bg-slate-100 text-slate-600 text-xs font-medium rounded-full"
              >
                {tag}
              </span>
            ))}
          </div>

          <div className="mt-10 p-6 sm:p-8 rounded-xl bg-brand-900 text-center">
            <h3 className="text-xl font-bold text-white mb-2">Need Help Financing Your Education?</h3>
            <p className="text-brand-300 text-sm mb-5 max-w-md mx-auto">
              Compare loan offers from 25+ banks in under 2 minutes. No impact on your credit score.
            </p>
            <button onClick={openModal} className="btn-primary text-sm">
              Check Loan Eligibility
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </section>

      {relatedPosts.length > 0 && (
        <section className="bg-slate-50 section-padding">
          <div className="container-max mx-auto">
            <h2 className="text-2xl font-bold text-brand-900 mb-8">Related Articles</h2>
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {relatedPosts.map((related) => (
                <Link
                  key={related.id}
                  href={`/blog/${related.id}`}
                  className="card overflow-hidden group block"
                >
                  <div className="relative h-40 overflow-hidden">
                    <img
                      src={related.image}
                      alt={related.title}
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                    />
                    <span className={`absolute top-3 left-3 text-xs font-medium px-2.5 py-1 rounded-full ${categoryColors[related.category] || 'bg-slate-100 text-slate-700'}`}>
                      {related.category}
                    </span>
                  </div>
                  <div className="p-5">
                    <h3 className="text-sm font-semibold text-brand-900 mb-2 leading-snug group-hover:text-accent-700 transition-colors line-clamp-2">
                      {related.title}
                    </h3>
                    <div className="flex items-center gap-3 text-xs text-slate-400">
                      <span>{related.date}</span>
                      <span className="flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        {related.readTime}
                      </span>
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          </div>
        </section>
      )}
    </>
  );
}
