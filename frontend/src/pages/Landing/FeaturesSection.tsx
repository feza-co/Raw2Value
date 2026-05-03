import DiagonalDivider from '@/components/editorial/DiagonalDivider'
import RevealText from '@/components/editorial/RevealText'

const FEATURES = [
  {
    title: 'ML Rota Optimizasyonu',
    desc: 'CatBoost modelleri 39 özellikle kâr ve rota tahmin eder. Macro-F1: 0.78.',
  },
  {
    title: 'Gerçek Zamanlı Kur',
    desc: 'TCMB EVDS entegrasyonu. USD/TRY ve EUR/TRY anlık güncelleme.',
  },
  {
    title: 'CO₂ Ayak İzi',
    desc: 'Hackathon standartlarına uygun karbonlama: kara, deniz, hava, demiryolu.',
  },
  {
    title: 'B2B Alıcı Eşleşmesi',
    desc: '3 profil: max kâr, düşük karbon, hızlı teslimat. Deterministik skor.',
  },
  {
    title: 'What-If Simülatör',
    desc: '10\'a kadar paralel senaryo: kur değişimi, tonaj, taşıma modu.',
  },
  {
    title: 'Model Şeffaflığı',
    desc: 'Ablasyon deltalı model kanıtları herkese açık. Güven skoru her yanıtta.',
  },
]

export default function FeaturesSection() {
  return (
    <>
      <DiagonalDivider fromColor="#1A1A1A" toColor="#F8F7F5" />
      <section className="bg-parchment py-32">
        <div className="max-w-[1440px] mx-auto px-8 md:px-16 xl:px-24">
          <div className="grid grid-cols-1 lg:grid-cols-[2fr_3fr] gap-24 items-start">
            <div className="lg:sticky lg:top-32">
              <p className="font-body text-xs text-stone-300 uppercase tracking-widest mb-6">Özellikler</p>
              <h2
                className="font-display font-light text-ink leading-tight"
                style={{ fontSize: 'clamp(2.5rem, 5vw, 5rem)' }}
              >
                <RevealText text="Veri Odaklı Karar Motoru" />
              </h2>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-x-12 gap-y-12">
              {FEATURES.map((f) => (
                <div key={f.title}>
                  <div className="w-8 h-px bg-amber mb-4" />
                  <h3 className="font-body text-sm font-medium text-charcoal mb-2">{f.title}</h3>
                  <p className="font-body text-sm text-stone-300 leading-relaxed">{f.desc}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>
    </>
  )
}
