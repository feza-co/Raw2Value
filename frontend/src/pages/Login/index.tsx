import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { useNavigate, Link } from 'react-router-dom'
import { toast } from 'react-hot-toast'
import { loginSchema, type LoginFormValues } from '@/utils/validators'
import { useAuth } from '@/hooks/useAuth'

export default function Login() {
  const navigate = useNavigate()
  const { login } = useAuth()
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
  })

  const onSubmit = async (values: LoginFormValues) => {
    try {
      await login(values.email, values.password)
      navigate('/cockpit', { replace: true })
    } catch {
      toast.error('E-posta veya şifre hatalı.')
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-8 bg-slate-50 relative overflow-hidden">
      {/* Premium Background */}
      <div className="absolute inset-0 bg-[radial-gradient(#e5e7eb_1px,transparent_1px)] [background-size:32px_32px] opacity-40 pointer-events-none" />
      <div className="absolute top-0 right-0 w-[600px] h-[600px] bg-gradient-to-br from-amber-100/40 to-amber-500/10 blur-[100px] rounded-full z-0 pointer-events-none" />
      
      <div className="w-full max-w-md relative z-10">
        <div className="bg-white p-10 md:p-12 rounded-[2.5rem] shadow-2xl shadow-slate-200/50 border border-slate-100">
          <p className="font-body text-sm font-semibold text-amber-600 uppercase tracking-widest mb-4">Giriş</p>
          <h1 className="font-display font-black text-slate-900 text-4xl mb-10 drop-shadow-sm">Hesabınıza girin</h1>
          
          <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-6">
            <div>
              <label className="font-body text-xs font-bold text-slate-500 uppercase tracking-widest block mb-2">
                E-posta
              </label>
              <input
                {...register('email')}
                type="email"
                className="w-full border border-slate-200 bg-slate-50 px-5 py-4 rounded-xl font-body text-sm text-slate-900 focus:outline-none focus:border-amber-500 focus:ring-4 focus:ring-amber-500/10 transition-all duration-300"
                placeholder="ad@sirket.com"
              />
              {errors.email && <p className="font-body text-xs text-red-500 font-medium mt-2">{errors.email.message}</p>}
            </div>
            <div>
              <label className="font-body text-xs font-bold text-slate-500 uppercase tracking-widest block mb-2">
                Şifre
              </label>
              <input
                {...register('password')}
                type="password"
                className="w-full border border-slate-200 bg-slate-50 px-5 py-4 rounded-xl font-body text-sm text-slate-900 focus:outline-none focus:border-amber-500 focus:ring-4 focus:ring-amber-500/10 transition-all duration-300"
                placeholder="••••••••"
              />
              {errors.password && <p className="font-body text-xs text-red-500 font-medium mt-2">{errors.password.message}</p>}
            </div>
            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full py-4 mt-4 bg-slate-900 text-white rounded-xl font-body font-semibold text-lg hover:bg-slate-800 shadow-xl shadow-slate-900/20 hover:-translate-y-1 transition-all duration-300 disabled:opacity-50 disabled:hover:translate-y-0"
            >
              {isSubmitting ? 'Giriş yapılıyor…' : 'Giriş Yap'}
            </button>
          </form>
          
          <p className="font-body text-sm font-medium text-slate-500 mt-8 text-center">
            Hesabınız yok mu?{' '}
            <Link to="/register" className="text-amber-600 font-bold hover:text-amber-700 transition-colors duration-150">
              Kayıt olun
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}
