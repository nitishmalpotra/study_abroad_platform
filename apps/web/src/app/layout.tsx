import type { Metadata } from 'next';
import '../index.css';
import SiteShell from '../components/layout/SiteShell';

export const metadata: Metadata = {
  title: 'KlassFin',
  description: 'Study abroad planning tools, destinations, universities, and education loan guidance.',
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <SiteShell>{children}</SiteShell>
      </body>
    </html>
  );
}
