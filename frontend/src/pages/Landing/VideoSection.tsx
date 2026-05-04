import { motion } from 'framer-motion'
import DiagonalDivider from '@/components/editorial/DiagonalDivider'
import RevealText from '@/components/editorial/RevealText'

export default function VideoSection() {
  return (
    <>
      <DiagonalDivider fromColor="#ffffff" toColor="#f8fafc" />
      <section className="bg-slate-50 py-32">
        <div className="max-w-[1440px] mx-auto px-8 md:px-16 xl:px-24">
          <div className="grid grid-cols-1 lg:grid-cols-[55fr_45fr] gap-16 items-center">
            <motion.div
              className="aspect-video bg-slate-900 overflow-hidden rounded-3xl shadow-2xl shadow-slate-200"
              initial={{ opacity: 0, x: -40 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true, amount: 0.3 }}
              transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
            >
              <video
                className="w-full h-full object-cover"
                autoPlay
                muted
                loop
                playsInline
                src="/demo-video.mp4"
              >
                <div className="flex items-center justify-center h-full">
                  <p className="font-body text-slate-400 text-sm">Demo video yükleniyor…</p>
                </div>
              </video>
            </motion.div>

            <div>
              <p className="font-body text-sm font-semibold text-amber-600 uppercase tracking-widest mb-6">
                Canlı Demo
              </p>
              <h2
                className="font-display font-black text-slate-900 leading-tight mb-6"
                style={{ fontSize: 'clamp(2.5rem, 4vw, 4rem)' }}
              >
                <RevealText text="Motoru Çalışırken Görün" />
              </h2>
              <p className="font-body text-slate-600 text-lg leading-relaxed mb-8">
                Gerçek Kapadokya verileri üzerinde eğitilmiş yapay zeka modelleri,
                saniyeler içinde en kârlı rotayı, CO₂ ayak izini ve B2B alıcı
                eşleşmelerini hesaplar.
              </p>
              <a
                href="mailto:demo@raw2value.ai"
                className="font-body font-semibold text-lg px-8 py-4 bg-amber-500 text-white rounded-full shadow-xl shadow-amber-500/20 hover:bg-amber-600 hover:-translate-y-1 transition-all duration-300 inline-block"
              >
                Canlı Demo Talep Et
              </a>
            </div>
          </div>
        </div>
      </section>
    </>
  )
}
