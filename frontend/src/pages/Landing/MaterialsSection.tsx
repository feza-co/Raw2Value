import DiagonalDivider from '@/components/editorial/DiagonalDivider'
import RunningNumber from '@/components/editorial/RunningNumber'

const MATERIALS = [
  {
    name: 'Pomza',
    tagline: 'Hafif. Gözenekli. İhracat Lideri.',
    stat: 8200000,
    statSuffix: ' ton/yıl',
    statLabel: 'Türkiye üretimi',
    description: 'Dünya pomza rezervlerinin %75\'i Anadolu\'da. Kapadokya ocakları birinci kalite hammadde sunar.',
    accent: '#d97706', // amber-600
  },
  {
    name: 'Perlit',
    tagline: 'Genleşir. Hafifler. Değer Kazanır.',
    stat: 5700000000,
    statSuffix: ' ton',
    statLabel: 'Türkiye rezervi',
    description: 'İnşaat, tarım ve endüstriyel uygulamalarda küresel talep artışı sürüyor.',
    accent: '#059669', // emerald-600
  },
  {
    name: 'Kabak Çekirdeği',
    tagline: 'Protein Zengini. Pazar Büyüyor.',
    stat: 1140000000,
    statSuffix: '$',
    statLabel: 'Küresel pazar',
    description: 'Sağlıklı atıştırmalık trendleri ile Avrupa ve Asya talebinde güçlü büyüme.',
    accent: '#b45309', // amber-700
  },
]

export default function MaterialsSection() {
  return (
    <>
      <DiagonalDivider fromColor="#f8fafc" toColor="#ffffff" flip />
      <section className="bg-white py-32">
        <div className="max-w-[1440px] mx-auto px-8 md:px-16 xl:px-24">
          <p className="font-body text-sm font-semibold text-amber-600 uppercase tracking-widest mb-16">
            Hammaddeler
          </p>
          <div className="flex flex-col gap-0">
            {MATERIALS.map((m, i) => (
              <div
                key={m.name}
                className="grid grid-cols-1 lg:grid-cols-[1fr_2fr_1fr] gap-8 py-16 border-b border-slate-100 items-center group hover:bg-slate-50 transition-colors duration-300 rounded-3xl px-8 -mx-8"
                style={{ flexDirection: i % 2 === 1 ? 'row-reverse' : 'row' }}
              >
                <div>
                  <p className="font-body text-sm font-bold uppercase tracking-widest mb-3" style={{ color: m.accent }}>
                    {String(i + 1).padStart(2, '0')}
                  </p>
                  <h3 className="font-display font-black text-slate-900 text-5xl mb-4 group-hover:-translate-y-1 transition-transform">{m.name}</h3>
                  <p className="font-body text-slate-500 italic font-medium">{m.tagline}</p>
                </div>
                <p className="font-body text-slate-600 text-lg leading-relaxed lg:px-12">{m.description}</p>
                <div className="text-right">
                  <p
                    className="font-display font-black leading-none drop-shadow-sm"
                    style={{ fontSize: 'clamp(2.5rem, 4vw, 4rem)', color: m.accent }}
                  >
                    <RunningNumber target={m.stat} suffix={m.statSuffix} />
                  </p>
                  <p className="font-body text-sm font-medium text-slate-500 mt-3">{m.statLabel}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>
    </>
  )
}
