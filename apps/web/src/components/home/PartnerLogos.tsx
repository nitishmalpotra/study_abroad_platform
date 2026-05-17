import { motion } from 'framer-motion';

const partners = [
  {
    name: 'SBI',
    fullName: 'State Bank of India',
    color: '#1a4d8f',
    weight: 800,
    size: 'text-2xl',
  },
  {
    name: 'HDFC Credila',
    fullName: 'HDFC Credila',
    color: '#004b87',
    weight: 700,
    size: 'text-xl',
  },
  {
    name: 'ICICI Bank',
    fullName: 'ICICI Bank',
    color: '#f37b20',
    weight: 700,
    size: 'text-xl',
  },
  {
    name: 'Axis Bank',
    fullName: 'Axis Bank',
    color: '#97144d',
    weight: 700,
    size: 'text-xl',
  },
  {
    name: 'Bank of Baroda',
    fullName: 'Bank of Baroda',
    color: '#f26522',
    weight: 700,
    size: 'text-lg',
  },
  {
    name: 'PNB',
    fullName: 'Punjab National Bank',
    color: '#1d2951',
    weight: 800,
    size: 'text-2xl',
  },
  {
    name: 'Prodigy Finance',
    fullName: 'Prodigy Finance',
    color: '#00b2a9',
    weight: 600,
    size: 'text-lg',
  },
  {
    name: 'Avanse',
    fullName: 'Avanse Financial',
    color: '#e8392c',
    weight: 700,
    size: 'text-xl',
  },
];

export default function PartnerLogos() {
  return (
    <section className="bg-white border-b border-slate-100">
      <div className="container-max mx-auto px-4 sm:px-6 lg:px-8 py-10 lg:py-12">
        <motion.p
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          className="text-center text-xs font-medium text-slate-400 uppercase tracking-widest mb-8"
        >
          Partnered with leading banks & institutions
        </motion.p>

        <div className="relative overflow-hidden">
          <div className="absolute left-0 top-0 bottom-0 w-16 bg-gradient-to-r from-white to-transparent z-10 pointer-events-none" />
          <div className="absolute right-0 top-0 bottom-0 w-16 bg-gradient-to-l from-white to-transparent z-10 pointer-events-none" />

          <motion.div
            className="flex items-center gap-12 lg:gap-16"
            animate={{ x: ['0%', '-50%'] }}
            transition={{
              x: {
                repeat: Infinity,
                repeatType: 'loop',
                duration: 25,
                ease: 'linear',
              },
            }}
          >
            {[...partners, ...partners].map((partner, i) => (
              <div
                key={`${partner.name}-${i}`}
                className="flex-shrink-0 flex items-center justify-center h-12 px-2 opacity-40 hover:opacity-70 transition-opacity duration-300 cursor-default select-none"
                title={partner.fullName}
              >
                <span
                  className={`${partner.size} whitespace-nowrap tracking-tight`}
                  style={{
                    fontWeight: partner.weight,
                    color: partner.color,
                    fontFamily: "'Poppins', sans-serif",
                  }}
                >
                  {partner.name}
                </span>
              </div>
            ))}
          </motion.div>
        </div>
      </div>
    </section>
  );
}
