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
    accent: '#C4BDB0',
  },
  {
    name: 'Perlit',
    tagline: 'Genleşir. Hafifler. Değer Kazanır.',
    stat: 5700000000,
    statSuffix: ' ton',
    statLabel: 'Türkiye rezervi',
    description: 'İnşaat, tarım ve endüstriyel uygulamalarda küresel talep artışı süruyor.',
    accent: '#3D7A4E',
  },
  {
    name: 'Kabak Çekirdeği',
    tagline: 'Protein Zengini. Pazar Büyüyor.',
    stat: 1140000000,
    statSuffix: '$',
    statLabel: 'Küresel pazar',
    description: 'Sağlıklı atıştırmalık trendleri ile Avrupa ve Asya talebinde güçlü büyüme.',
    accent: '#C8973A',
  },
]

export default function MaterialsSection() {
  return (
    <>
      <DiagonalDivider fromColor="#F8F7F5" toColor="#1A1A1A" flip />
      <section className="bg-charcoal py-32">
        <div className="max-w-[1440px] mx-auto px-8 md:px-16 xl:px-24">
          <p className="font-body text-xs text-stone-300 uppercase tracking-widest mb-16">
            Hammaddeler
          </p>
          <div className="flex flex-col gap-0">
            {MATERIALS.map((m, i) => (
              <div
                key={m.name}
                className="grid grid-cols-1 lg:grid-cols-[1fr_2fr_1fr] gap-8 py-16 border-b border-white/10 items-center"
                style={{ flexDirection: i % 2 === 1 ? 'row-reverse' : 'row' }}
              >
                <div>
                  <p className="font-body text-xs uppercase tracking-widest mb-2" style={{ color: m.accent }}>
                    {String(i + 1).padStart(2, '0')}
                  </p>
                  <h3 className="font-display font-light text-parchment text-5xl mb-3">{m.name}</h3>
                  <p className="font-body text-sm text-stone-300 italic">{m.tagline}</p>
                </div>
                <p className="font-body text-stone-300 leading-relaxed lg:px-12">{m.description}</p>
                <div className="text-right">
                  <p
                    className="font-display font-light leading-none"
                    style={{ fontSize: 'clamp(2rem, 4vw, 3.5rem)', color: m.accent }}
                  >
                    <RunningNumber target={m.stat} suffix={m.statSuffix} />
                  </p>
                  <p className="font-body text-xs text-stone-300 mt-2">{m.statLabel}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>
    </>
  )
}
