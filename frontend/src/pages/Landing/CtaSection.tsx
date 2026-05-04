import { Link } from 'react-router-dom'

export default function CtaSection() {
  return (
    <section className="bg-white py-40 relative overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-t from-slate-50 to-white z-0" />
      <div className="max-w-[1440px] mx-auto px-8 md:px-16 xl:px-24 text-center relative z-10">
        <p className="font-body text-sm font-semibold text-amber-600 uppercase tracking-widest mb-8">Başlayın</p>
        <h2
          className="font-display font-black text-slate-900 leading-tight mx-auto max-w-3xl mb-12 drop-shadow-sm"
          style={{ fontSize: 'clamp(3rem, 5vw, 5rem)' }}
        >
          Ham Maddeyi Gerçek Değere Dönüştürün
        </h2>
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
          <Link
            to="/register"
            className="font-body font-semibold text-lg px-12 py-5 rounded-full bg-slate-900 text-white hover:bg-slate-800 shadow-xl shadow-slate-900/20 hover:-translate-y-1 transition-all duration-300"
          >
            Ücretsiz Başla
          </Link>
          <Link
            to="/evidence"
            className="font-body font-semibold text-lg px-12 py-5 rounded-full bg-white text-slate-900 border border-slate-200 hover:bg-slate-50 hover:shadow-lg hover:-translate-y-1 transition-all duration-300"
          >
            Model Kanıtları
          </Link>
        </div>
        <p className="font-body text-sm font-medium text-slate-400 mt-12">
          Hackathon Kapadokya 2026 — Raw2Value AI
        </p>
      </div>
    </section>
  )
}
