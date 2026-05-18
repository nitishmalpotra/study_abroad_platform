'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import { Menu, X, ChevronRight } from 'lucide-react';
import { useModal } from '../../context/ModalContext';

const navLinks = [
  { name: 'Destinations', path: '/destinations' },
  { name: 'Universities', path: '/universities' },
  { name: 'Resources', path: '/tools' },
  { name: 'Blog', path: '/blog' },
];

export default function Navbar() {
  const [isScrolled, setIsScrolled] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const { openModal } = useModal();
  const pathname = usePathname() ?? '';

  useEffect(() => {
    const handleScroll = () => setIsScrolled(window.scrollY > 10);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  useEffect(() => {
    setMobileOpen(false);
  }, [pathname]);

  return (
    <nav
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        isScrolled
          ? 'bg-white/95 backdrop-blur-md shadow-sm border-b border-slate-100'
          : 'bg-transparent'
      }`}
    >
      <div className="container-max mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16 lg:h-20">
          <Link href="/" className="flex items-center gap-2">
            <img src="/logo.png" alt="KlassFin" className="h-9 lg:h-10 w-auto" />
          </Link>

          <div className="hidden lg:flex items-center gap-1">
            {navLinks.map((link) => (
              <Link
                key={link.path}
                href={link.path}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  pathname.startsWith(link.path)
                    ? isScrolled
                      ? 'text-brand-700 bg-brand-50'
                      : 'text-white bg-white/15'
                    : isScrolled
                    ? 'text-slate-600 hover:text-brand-700 hover:bg-slate-50'
                    : 'text-white/80 hover:text-white hover:bg-white/10'
                }`}
              >
                {link.name}
              </Link>
            ))}
          </div>

          <div className="hidden lg:flex items-center gap-3">
            <button
              onClick={openModal}
              className="btn-primary text-sm py-2.5"
            >
              Check Loan Eligibility
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>

          <button
            onClick={() => setMobileOpen(!mobileOpen)}
            className={`lg:hidden p-2 rounded-lg ${isScrolled ? 'text-brand-900' : 'text-white'}`}
          >
            {mobileOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>
      </div>

      <AnimatePresence>
        {mobileOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="lg:hidden bg-white border-b border-slate-200 overflow-hidden"
          >
            <div className="px-4 py-4 space-y-1">
              {navLinks.map((link) => (
                <Link
                  key={link.path}
                  href={link.path}
                  className={`block px-4 py-3 rounded-lg text-sm font-medium transition-colors ${
                    pathname.startsWith(link.path)
                      ? 'text-brand-700 bg-brand-50'
                      : 'text-slate-600 hover:text-brand-700 hover:bg-slate-50'
                  }`}
                >
                  {link.name}
                </Link>
              ))}
              <button
                onClick={openModal}
                className="btn-primary w-full text-sm py-3 mt-3"
              >
                Check Loan Eligibility
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </nav>
  );
}
