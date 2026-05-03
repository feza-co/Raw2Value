import { useAuth } from '@/hooks/useAuth'

export default function Settings() {
  const { user, logout } = useAuth()

  return (
    <div className="max-w-xl mx-auto px-8 py-12">
      <p className="font-body text-xs text-stone-300 uppercase tracking-widest mb-6">Ayarlar</p>
      <h1 className="font-display font-light text-ink text-4xl mb-12">Hesap</h1>

      {user && (
        <div className="flex flex-col gap-6">
          <div>
            <label className="font-body text-xs text-stone-300 uppercase tracking-widest block mb-1">Ad Soyad</label>
            <p className="font-body text-sm text-charcoal">{user.full_name ?? '—'}</p>
          </div>
          <div>
            <label className="font-body text-xs text-stone-300 uppercase tracking-widest block mb-1">E-posta</label>
            <p className="font-body text-sm text-charcoal">{user.email}</p>
          </div>
          <div>
            <label className="font-body text-xs text-stone-300 uppercase tracking-widest block mb-1">Rol</label>
            <p className="font-body text-sm text-charcoal">{user.role}</p>
          </div>
          <div className="pt-6 border-t border-stone-100">
            <button
              onClick={logout}
              className="font-body text-sm text-danger hover:underline"
            >
              Çıkış Yap
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
