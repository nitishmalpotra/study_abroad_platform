import { Link } from 'react-router-dom';
import { Shield, Building2, Lock, Mail, Phone, Instagram, Twitter, Linkedin, Youtube } from 'lucide-react';

const footerLinks = {
  'Destinations': [
    { name: 'United States', path: '/destinations/usa' },
    { name: 'United Kingdom', path: '/destinations/uk' },
    { name: 'Canada', path: '/destinations/canada' },
    { name: 'Australia', path: '/destinations/australia' },
    { name: 'Ireland', path: '/destinations/ireland' },
    { name: 'New Zealand', path: '/destinations/new-zealand' },
  ],
  'Resources': [
    { name: 'EMI Calculator', path: '/tools/emi-calculator' },
    { name: 'SOP Review', path: '/tools/sop-review' },
    { name: 'Planning Resources', path: '/tools/resources' },
  ],
  'Company': [
    { name: 'Blog', path: '/blog' },
    { name: 'Universities', path: '/universities' },
    { name: 'Privacy Policy', path: '#' },
    { name: 'Terms of Service', path: '#' },
  ],
};

export default function Footer() {
  return (
    <footer className="bg-brand-900 text-white">
      <div className="container-max mx-auto px-4 sm:px-6 lg:px-8">
        <div className="py-12 lg:py-16 border-b border-brand-700">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-10">
            <div className="lg:col-span-2">
              <Link to="/" className="flex items-center gap-2.5 mb-5">
                <img src="/logo.png" alt="KlassFin" className="h-9 w-auto brightness-0 invert" />
              </Link>
              <p className="text-brand-300 text-sm leading-relaxed max-w-sm mb-6">
                India's trusted study abroad platform. We help students find the right university,
                secure education loans, and plan every step of their international education journey.
              </p>
              <div className="space-y-2">
                <a href="mailto:hello@klassfin.com" className="flex items-center gap-2 text-sm text-brand-300 hover:text-white transition-colors">
                  <Mail className="w-4 h-4" />
                  hello@klassfin.com
                </a>
                <a href="tel:+911800123456" className="flex items-center gap-2 text-sm text-brand-300 hover:text-white transition-colors">
                  <Phone className="w-4 h-4" />
                  1800-123-456 (Toll Free)
                </a>
              </div>
              <div className="flex items-center gap-3 mt-6">
                {[
                  { icon: Instagram, href: '#', label: 'Instagram' },
                  { icon: Twitter, href: '#', label: 'Twitter' },
                  { icon: Linkedin, href: '#', label: 'LinkedIn' },
                  { icon: Youtube, href: '#', label: 'YouTube' },
                ].map((social) => (
                  <a
                    key={social.label}
                    href={social.href}
                    aria-label={social.label}
                    className="w-9 h-9 rounded-lg bg-brand-800 flex items-center justify-center text-brand-300 hover:bg-accent-600 hover:text-white transition-colors"
                  >
                    <social.icon className="w-4 h-4" />
                  </a>
                ))}
              </div>
            </div>

            {Object.entries(footerLinks).map(([title, links]) => (
              <div key={title}>
                <h4 className="text-sm font-semibold text-white mb-4 uppercase tracking-wider">{title}</h4>
                <ul className="space-y-2.5">
                  {links.map((link) => (
                    <li key={link.name}>
                      <Link
                        to={link.path}
                        className="text-sm text-brand-300 hover:text-white transition-colors"
                      >
                        {link.name}
                      </Link>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>

        <div className="py-8">
          <div className="flex flex-col md:flex-row items-center justify-between gap-6">
            <div className="flex flex-wrap items-center justify-center gap-6">
              <div className="flex items-center gap-2 text-sm text-brand-400">
                <Lock className="w-4 h-4 text-accent-400" />
                Secure 256-bit Encryption
              </div>
              <div className="flex items-center gap-2 text-sm text-brand-400">
                <Building2 className="w-4 h-4 text-accent-400" />
                RBI-Approved Bank Partners
              </div>
              <div className="flex items-center gap-2 text-sm text-brand-400">
                <Shield className="w-4 h-4 text-accent-400" />
                Data Protection Compliant
              </div>
            </div>
            <p className="text-sm text-brand-500">
              &copy; {new Date().getFullYear()} KlassFin. All rights reserved.
            </p>
          </div>
        </div>
      </div>
    </footer>
  );
}
