import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import RevealText from '@/components/editorial/RevealText'
import FxTicker from '@/components/domain/FxTicker'

export default function HeroSection() {
  return (
    <section className="relative min-h-screen flex flex-col justify-end overflow-hidden">
      {/* Full Width Background Image */}
      <div className="absolute inset-0 z-0">
        <img 
          src="/image.jpeg" 
          alt="Kapadokya Platform Background" 
          className="w-full h-full object-cover"
          onError={(e) => {
            (e.target as HTMLImageElement).src = 'https://images.unsplash.com/photo-1627885408713-33230bdf310e?q=80&w=2500&auto=format&fit=crop';
          }}
        />
        {/* Subtle white overlay only at the very bottom to blend into the next section */}
        <div className="absolute inset-0 bg-gradient-to-t from-white via-white/40 to-transparent h-full" />
      </div>

      <div className="relative z-10 max-w-[1440px] mx-auto px-8 md:px-16 xl:px-24 pb-24 pt-48 w-full">
        
        <motion.div 
          className="mb-8 inline-flex items-center gap-2 rounded-full border border-slate-200/50 bg-white/60 px-5 py-2.5 text-sm font-semibold text-slate-900 shadow-md backdrop-blur-md"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <span className="flex h-2 w-2 rounded-full bg-amber-500 animate-pulse"></span>
          Yeni Nesil Değerleme Platformu
        </motion.div>

        <h1
          className="font-display font-black leading-tight tracking-tight mb-8"
          style={{ 
            fontSize: 'clamp(3rem, 6vw, 6.5rem)',
            textShadow: '0 4px 24px rgba(255,255,255,0.8)'
          }}
        >
          <div className="text-slate-900 block overflow-hidden">
            <RevealText text="Kapadokya'nın" />
          </div>
          <div className="text-slate-900 block overflow-hidden">
            <RevealText text="Ham Değerini" delay={0.1} />
          </div>
          <div className="text-amber-600 drop-shadow-sm block overflow-hidden">
            <RevealText text="Gerçek Kâra" delay={0.2} />
          </div>
          <div className="text-slate-900 block overflow-hidden">
            <RevealText text="Dönüştürün." delay={0.3} />
          </div>
        </h1>

        <motion.p
          className="font-body text-slate-800 max-w-2xl text-xl leading-relaxed mb-12 font-bold"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.9, duration: 0.6 }}
          style={{ textShadow: '0 2px 10px rgba(255,255,255,0.9)' }}
        >
          Pomza, perlit ve kabak çekirdeği için en kârlı işleme rotasını,
          beklenen kârı ve alıcı eşleşmesini yapay zeka ile hesaplayın.
        </motion.p>

        <motion.div
          className="flex items-center gap-4"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.1, duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
        >
          <Link
            to="/register"
            className="font-body font-semibold text-lg px-10 py-5 rounded-full bg-slate-900 text-white hover:bg-slate-800 shadow-xl shadow-slate-900/20 hover:-translate-y-1 transition-all duration-300"
          >
            Ücretsiz Başla
          </Link>
          <Link
            to="/evidence"
            className="font-body font-semibold text-lg px-10 py-5 rounded-full bg-white/90 backdrop-blur-sm text-slate-900 border border-slate-200 hover:bg-white hover:shadow-lg hover:-translate-y-1 transition-all duration-300"
          >
            Model Kanıtları →
          </Link>
        </motion.div>

        <motion.div
          className="mt-16 pt-8 border-t border-slate-300/50 w-full backdrop-blur-sm bg-white/10 rounded-3xl p-4"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.4, duration: 0.5 }}
        >
          <FxTicker />
        </motion.div>
      </div>
    </section>
  )
}
