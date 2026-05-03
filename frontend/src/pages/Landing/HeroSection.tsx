import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import GrainOverlay from '@/components/editorial/GrainOverlay'
import RevealText from '@/components/editorial/RevealText'
import FxTicker from '@/components/domain/FxTicker'

export default function HeroSection() {
  return (
    <section
      className="relative min-h-screen flex flex-col justify-end overflow-hidden"
      style={{ background: '#0D0D0D' }}
    >
      <GrainOverlay opacity={0.05} />

      <div className="relative z-20 max-w-[1440px] mx-auto px-8 md:px-16 xl:px-24 pb-24 pt-32">
        <h1
          className="font-display font-light text-parchment leading-[0.9] tracking-[-0.03em] mb-8"
          style={{ fontSize: 'clamp(4rem, 8vw, 9rem)' }}
        >
          <RevealText text="Kapadokya'nın" />
          <br />
          <RevealText text="Ham Değerini" delay={0.1} />
          <br />
          <span
            className="inline-block"
            style={{ color: '#C8973A' }}
          >
            <RevealText text="Gerçek Kâra" delay={0.2} />
          </span>
          <br />
          <RevealText text="Dönüştürün." delay={0.3} />
        </h1>

        <motion.p
          className="font-body text-stone-300 max-w-lg mb-12 leading-relaxed"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.9, duration: 0.6 }}
        >
          Pomza, perlit ve kabak çekirdeği için en kârlı işleme rotasını,
          beklenen kârı ve alıcı eşleşmesini yapay zeka ile hesaplayın.
        </motion.p>

        <motion.div
          className="flex items-center gap-6"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.1, duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
        >
          <Link
            to="/register"
            className="font-body text-sm px-8 py-4 bg-amber text-white hover:bg-amber-dark transition-colors duration-150"
          >
            Ücretsiz Başla
          </Link>
          <Link
            to="/evidence"
            className="font-body text-sm text-stone-300 hover:text-parchment transition-colors duration-150"
          >
            Model Kanıtları →
          </Link>
        </motion.div>

        <motion.div
          className="mt-16 pt-8 border-t border-white/10"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.4, duration: 0.5 }}
        >
          <FxTicker dark />
        </motion.div>
      </div>
    </section>
  )
}
