import { Link } from 'react-router-dom'

export default function CtaSection() {
  return (
    <section className="bg-white py-32">
      <div className="max-w-[1440px] mx-auto px-8 md:px-16 xl:px-24 text-center">
        <p className="font-body text-xs text-stone-300 uppercase tracking-widest mb-8">Başlayın</p>
        <h2
          className="font-display font-light text-ink leading-tight mx-auto max-w-3xl mb-12"
          style={{ fontSize: 'clamp(2.5rem, 5vw, 5rem)' }}
        >
          Ham Maddeyi Gerçek Değere Dönüştürün
        </h2>
        <div className="flex items-center justify-center gap-6">
          <Link
            to="/register"
            className="font-body text-sm px-10 py-4 bg-amber text-white hover:bg-amber-dark transition-colors duration-150"
          >
            Ücretsiz Başla
          </Link>
          <Link
            to="/evidence"
            className="font-body text-sm px-10 py-4 border border-charcoal text-charcoal hover:bg-charcoal hover:text-parchment transition-all duration-150"
          >
            Model Kanıtları
          </Link>
        </div>
        <p className="font-body text-xs text-stone-300 mt-8">
          Hackathon Kapadokya 2026 — Raw2Value AI
        </p>
      </div>
    </section>
  )
}
