import type { Metadata } from 'next';
import { Poppins } from 'next/font/google';
import '../index.css';
import SiteShell from '../components/layout/SiteShell';

const poppins = Poppins({
  subsets: ['latin'],
  weight: ['300', '400', '500', '600', '700', '800'],
  variable: '--font-poppins',
  display: 'swap',
});

export const metadata: Metadata = {
  title: 'KlassFin',
  description: 'Study abroad planning tools, destinations, universities, and education loan guidance.',
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className={poppins.variable}>
      <body>
        <SiteShell>{children}</SiteShell>
      </body>
    </html>
  );
}
