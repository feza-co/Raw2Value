import { motion } from 'framer-motion'
import DiagonalDivider from '@/components/editorial/DiagonalDivider'
import RevealText from '@/components/editorial/RevealText'

export default function VideoSection() {
  return (
    <>
      <DiagonalDivider fromColor="#0D0D0D" toColor="#F8F7F5" />
      <section className="bg-parchment py-24">
        <div className="max-w-[1440px] mx-auto px-8 md:px-16 xl:px-24">
          <div className="grid grid-cols-1 lg:grid-cols-[55fr_45fr] gap-16 items-center">
            <motion.div
              className="aspect-video bg-ink overflow-hidden"
              initial={{ opacity: 0, x: -40 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true, amount: 0.3 }}
              transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
            >
              {/* Demo videosunu buraya koyun: public/demo-video.mp4 */}
              <video
                className="w-full h-full object-cover"
                autoPlay
                muted
                loop
                playsInline
                src="/demo-video.mp4"
              >
                <div className="flex items-center justify-center h-full">
                  <p className="font-body text-stone-300 text-sm">Demo video yükleniyor…</p>
                </div>
              </video>
            </motion.div>

            <div>
              <p className="font-body text-xs text-stone-300 uppercase tracking-widest mb-6">
                Canlı Demo
              </p>
              <h2
                className="font-display font-light text-ink leading-tight mb-6"
                style={{ fontSize: 'clamp(2rem, 4vw, 3.5rem)' }}
              >
                <RevealText text="Motoru Çalışırken Görün" />
              </h2>
              <p className="font-body text-stone-300 leading-relaxed mb-8">
                Gerçek Kapadokya verileri üzerinde eğitilmiş CatBoost modelleri
                saniyeler içinde en kârlı rotayı, CO₂ ayak izini ve B2B alıcı
                eşleşmelerini hesaplar.
              </p>
              <a
                href="mailto:demo@raw2value.ai"
                className="font-body text-sm px-6 py-3 border border-amber text-amber hover:bg-amber hover:text-white transition-all duration-150 inline-block"
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
