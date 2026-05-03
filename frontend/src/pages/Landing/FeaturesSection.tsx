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
      <DiagonalDivider fromColor="#ffffff" toColor="#f8fafc" />
      <section className="bg-slate-50 py-32">
        <div className="max-w-[1440px] mx-auto px-8 md:px-16 xl:px-24">
          <div className="grid grid-cols-1 lg:grid-cols-[2fr_3fr] gap-24 items-start">
            <div className="lg:sticky lg:top-32">
              <p className="font-body text-sm font-semibold text-amber-600 uppercase tracking-widest mb-6">Özellikler</p>
              <h2
                className="font-display font-black text-slate-900 leading-tight"
                style={{ fontSize: 'clamp(3rem, 5vw, 5rem)' }}
              >
                <RevealText text="Veri Odaklı Karar Motoru" />
              </h2>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-x-12 gap-y-12">
              {FEATURES.map((f) => (
                <div key={f.title} className="bg-white p-8 rounded-[2rem] shadow-lg shadow-slate-200/50 border border-slate-100 hover:shadow-xl hover:-translate-y-1 transition-all duration-300">
                  <div className="w-12 h-1 bg-amber-500 mb-6 rounded-full" />
                  <h3 className="font-body text-xl font-bold text-slate-900 mb-3">{f.title}</h3>
                  <p className="font-body text-slate-600 leading-relaxed font-medium">{f.desc}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>
    </>
  )
}
