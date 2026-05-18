'use client';

import { useEffect } from 'react';
import { usePathname } from 'next/navigation';
import { ModalProvider } from '../../context/ModalContext';
import Navbar from './Navbar';
import Footer from './Footer';
import LeadModal from '../LeadModal';

export default function SiteShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  useEffect(() => {
    window.scrollTo(0, 0);
  }, [pathname]);

  return (
    <ModalProvider>
      <div className="min-h-screen flex flex-col">
        <Navbar />
        <main className="flex-1">{children}</main>
        <Footer />
        <LeadModal />
      </div>
    </ModalProvider>
  );
}
