import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { useNavigate } from 'react-router-dom'
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
    <div className="min-h-screen flex items-center justify-center px-8 pt-16">
      <div className="w-full max-w-sm">
        <p className="font-body text-xs text-stone-300 uppercase tracking-widest mb-8">Giriş</p>
        <h1 className="font-display font-light text-ink text-4xl mb-12">Hesabınıza girin</h1>
        <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-6">
          <div>
            <label className="font-body text-xs text-stone-300 uppercase tracking-widest block mb-2">
              E-posta
            </label>
            <input
              {...register('email')}
              type="email"
              className="w-full border border-stone-100 bg-white px-4 py-3 font-body text-sm text-charcoal focus:outline-none focus:border-amber transition-colors duration-150"
              placeholder="ad@sirket.com"
            />
            {errors.email && <p className="font-body text-xs text-danger mt-1">{errors.email.message}</p>}
          </div>
          <div>
            <label className="font-body text-xs text-stone-300 uppercase tracking-widest block mb-2">
              Şifre
            </label>
            <input
              {...register('password')}
              type="password"
              className="w-full border border-stone-100 bg-white px-4 py-3 font-body text-sm text-charcoal focus:outline-none focus:border-amber transition-colors duration-150"
              placeholder="••••••••"
            />
            {errors.password && <p className="font-body text-xs text-danger mt-1">{errors.password.message}</p>}
          </div>
          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full py-4 bg-amber text-white font-body text-sm hover:bg-amber-dark transition-colors duration-150 disabled:opacity-50"
          >
            {isSubmitting ? 'Giriş yapılıyor…' : 'Giriş Yap'}
          </button>
        </form>
        <p className="font-body text-sm text-stone-300 mt-8">
          Hesabınız yok mu?{' '}
          <a href="/register" className="text-amber hover:text-amber-dark transition-colors duration-150">
            Kayıt olun
          </a>
        </p>
      </div>
    </div>
  )
}
