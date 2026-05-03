import { useAuth } from '@/hooks/useAuth'

export default function Settings() {
  const { user, logout } = useAuth()

  return (
    <div className="max-w-3xl mx-auto px-8 py-12">
      <div className="mb-12">
        <p className="font-body text-sm font-semibold text-amber-600 uppercase tracking-widest mb-3">Ayarlar</p>
        <h1 className="font-display font-black text-slate-900 text-4xl">Hesap Bilgileri</h1>
      </div>

      {user ? (
        <div className="bg-white rounded-[2rem] shadow-xl shadow-slate-200/50 border border-slate-100 p-8 md:p-12">
          <div className="flex flex-col gap-8">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div className="bg-slate-50 p-6 rounded-2xl border border-slate-100">
                <label className="font-body text-xs font-bold text-slate-400 uppercase tracking-widest block mb-2">Ad Soyad</label>
                <p className="font-body text-lg font-semibold text-slate-900">{user.full_name ?? '—'}</p>
              </div>
              <div className="bg-slate-50 p-6 rounded-2xl border border-slate-100">
                <label className="font-body text-xs font-bold text-slate-400 uppercase tracking-widest block mb-2">E-posta</label>
                <p className="font-body text-lg font-semibold text-slate-900">{user.email}</p>
              </div>
            </div>
            
            <div className="bg-amber-50 p-6 rounded-2xl border border-amber-100/50 inline-block w-full md:w-1/2">
              <label className="font-body text-xs font-bold text-amber-600/70 uppercase tracking-widest block mb-2">Rol</label>
              <div className="inline-flex items-center gap-2">
                <span className="flex h-2 w-2 rounded-full bg-amber-500"></span>
                <p className="font-body text-lg font-bold text-amber-900 capitalize">{user.role}</p>
              </div>
            </div>

            <div className="pt-8 border-t border-slate-100 mt-4 flex items-center justify-between">
              <p className="font-body text-sm text-slate-500">Tüm cihazlardan çıkış yapabilirsiniz.</p>
              <button
                onClick={logout}
                className="font-body font-semibold text-sm px-8 py-3 rounded-full bg-red-50 text-red-600 hover:bg-red-100 hover:text-red-700 transition-all duration-200"
              >
                Çıkış Yap
              </button>
            </div>
          </div>
        </div>
      ) : (
        <div className="bg-white rounded-[2rem] shadow-xl shadow-slate-200/50 border border-slate-100 p-8 flex justify-center items-center">
          <p className="font-body text-sm font-medium text-slate-400 animate-pulse">Kullanıcı bilgileri yükleniyor…</p>
        </div>
      )}
    </div>
  )
}
