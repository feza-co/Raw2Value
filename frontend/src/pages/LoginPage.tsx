import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useForm } from 'react-hook-form';
import { useQuery } from '@tanstack/react-query';
import { useAuth } from '../lib/auth';
import { useToast } from '../components/Toast';
import { FxStrip } from '../components/FxStrip';
import { external, WEATHER_ICON } from '../lib/external';
import { api } from '../lib/api';

type Tab = 'login' | 'register';
type LoginForm = { email: string; password: string };
type RegisterForm = { full_name: string; email: string; password: string };

export function LoginPage() {
  const { login, register: doRegister } = useAuth();
  const toast = useToast();
  const [tab, setTab] = useState<Tab>('login');
  const [busy, setBusy] = useState(false);

  const lf = useForm<LoginForm>({ defaultValues: { email: '', password: '' } });
  const rf = useForm<RegisterForm>({ defaultValues: { full_name: '', email: '', password: '' } });

  const health = useQuery({ queryKey: ['health'], queryFn: api.health, retry: 0 });
  const wx = useQuery({ queryKey: ['cappadocia-weather'], queryFn: external.cappadociaWeather, retry: 0, staleTime: 5 * 60_000 });

  const onLogin = lf.handleSubmit(async (v) => {
    setBusy(true);
    try {
      await login(v.email, v.password);
      toast.push('Giriş başarılı, atölyeye yönlendiriliyorsunuz', 'ok', 1500);
    } catch (e: any) {
      toast.push(e?.message || 'Giriş başarısız', 'error');
    } finally { setBusy(false); }
  });

  const onRegister = rf.handleSubmit(async (v) => {
    setBusy(true);
    try {
      await doRegister(v);
      toast.push('Hesap oluşturuldu, hoş geldiniz', 'ok');
    } catch (e: any) {
      toast.push(e?.message || 'Kayıt başarısız', 'error');
    } finally { setBusy(false); }
  });

  // ⌘/Ctrl + Enter shortcut
  useEffect(() => {
    const h = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
        if (tab === 'login') onLogin(); else onRegister();
      }
    };
    window.addEventListener('keydown', h);
    return () => window.removeEventListener('keydown', h);
  }, [tab, onLogin, onRegister]);

  const fillDemo = () => {
    lf.setValue('email', 'admin@raw2value.local');
    lf.setValue('password', 'admin123');
  };

  return (
    <main style={{
      minHeight: '100vh',
      display: 'grid',
      gridTemplateColumns: '1.05fr 0.95fr',
    }} className="login-page">
      <style>{`
        @media (max-width: 1024px) { .login-page { grid-template-columns: 1fr !important; } }
        .login-hero {
          position: relative; padding: 36px 56px; display: flex; flex-direction: column;
          border-right: 1px solid var(--hairline);
          background: linear-gradient(180deg, var(--bone) 0%, var(--bone-deep) 100%);
          overflow: hidden;
        }
        .login-hero::before {
          content: ''; position: absolute; inset: 0; pointer-events: none;
          background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 800 600'><g fill='none' stroke='%231B2A3A' stroke-width='0.4' opacity='0.13'><path d='M0,420 C120,380 200,440 320,400 C440,360 520,460 660,420 C740,400 800,440 800,440 L800,600 L0,600 Z'/><path d='M0,460 C100,430 220,480 360,450 C480,420 580,500 700,470 C760,455 800,490 800,490'/><path d='M0,500 C140,470 240,520 380,490 C520,460 600,540 720,510 C780,495 800,530 800,530'/><path d='M0,540 C100,510 220,560 360,530 C480,500 580,580 700,550 C760,535 800,570 800,570'/></g><g fill='%23C8553D' opacity='0.18'><circle cx='180' cy='420' r='3'/><circle cx='320' cy='400' r='3'/><circle cx='520' cy='460' r='3'/><circle cx='660' cy='420' r='3'/></g></svg>");
          background-size: cover; background-position: center bottom;
        }
        .login-form-side {
          background: var(--paper); padding: 48px 56px;
          display: flex; flex-direction: column; justify-content: space-between; position: relative;
        }
        .scale-ruler {
          position: absolute; left: 56px; bottom: 28px; width: 200px;
          font-family: var(--mono); font-size: 9px; letter-spacing: 0.18em;
          color: var(--ink-faded); text-transform: uppercase;
        }
        .scale-ruler-bar {
          height: 3px; margin-top: 4px;
          background: linear-gradient(to right, var(--ink) 0 25%, var(--bone) 25% 50%, var(--ink) 50% 75%, var(--bone) 75% 100%);
          border: 1px solid var(--ink);
        }
        @media (max-width: 1024px) {
          .login-hero { padding: 28px 24px 80px; min-height: 480px; }
          .login-form-side { padding: 32px 24px; }
          .scale-ruler { display: none; }
        }
      `}</style>

      <section className="login-hero">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', position: 'relative', zIndex: 2 }}>
          <div className="brand">
            <span className="brand-mark" />
            <span className="brand-name" style={{ fontSize: 20 }}>raw<em>2</em>value</span>
          </div>
          <div className="numerals" style={{ fontSize: 10, letterSpacing: '0.18em', color: 'var(--ink-faded)', textTransform: 'uppercase' }}>
            38° 37′ N · 34° 54′ E · <strong style={{ color: 'var(--ink)', fontWeight: 500 }}>NEVŞEHİR · KAPADOKYA</strong>
          </div>
        </div>

        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center', padding: '60px 0', position: 'relative', zIndex: 2 }}>
          <motion.div initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.7 }}>
            <span className="eyebrow with-rule tuff">Hammadde · Karar Motoru · 2026</span>
          </motion.div>

          <motion.h1
            className="display-xl"
            style={{ marginTop: 18 }}
            initial={{ opacity: 0, y: 22 }} animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.9, delay: 0.1, ease: [0.2, 0.7, 0.3, 1] }}
          >
            <span className="stroke">Pomza,</span><br />
            Perlit, <em className="tuff-em">kabak</em><br />
            çekirdeği —<br />
            <em className="tuff-em">en kârlı</em> rota.
          </motion.h1>

          <motion.p className="lede" style={{ marginTop: 28, maxWidth: 480 }}
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.8, delay: 0.4 }}>
            Üç hammadde, on beş işleme rotası, üç ihracat hedefi.
            Augmented holdout'ta <strong style={{ fontStyle: 'normal', color: 'var(--ink)' }}>R²&nbsp;0.95</strong> profit ve
            <strong style={{ fontStyle: 'normal', color: 'var(--ink)' }}>&nbsp;macro-F1&nbsp;0.78</strong> rota tahmini.
          </motion.p>

          <div style={{ marginTop: 50, display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 26, maxWidth: 540 }}>
            {[
              { label: 'Hammadde', value: '3', em: true, foot: 'pomza · perlit · kabak ç.' },
              { label: 'İşleme Rotası', value: '15', em: false, foot: '10 trained · 5 expansion' },
              { label: 'Hedef Ülke', value: '3', em: true, foot: 'DE · NL · TR' },
            ].map((m, i) => (
              <motion.div key={m.label}
                style={{ borderTop: '1px solid var(--ink)', paddingTop: 12 }}
                initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.6 + i * 0.08, duration: 0.6 }}>
                <div className="numerals" style={{ fontSize: 9, letterSpacing: '0.18em', textTransform: 'uppercase', color: 'var(--ink-faded)' }}>{m.label}</div>
                <div style={{ fontFamily: 'var(--display)', fontSize: 38, fontWeight: 500, lineHeight: 1, marginTop: 6 }}>
                  {m.em ? <em className="tuff-em">{m.value}</em> : m.value}
                </div>
                <div style={{ fontSize: 12, color: 'var(--ink-soft)', marginTop: 6 }}>{m.foot}</div>
              </motion.div>
            ))}
          </div>
        </div>

        <div style={{ display: 'flex', justifyContent: 'space-between', gap: 18, flexWrap: 'wrap', position: 'relative', zIndex: 2 }}>
          <FxStrip />
          {wx.data ? (
            <span className="fx-pill">
              <span style={{ fontSize: 14 }}>{WEATHER_ICON[wx.data.current.weather_code] ?? '·'}</span>
              <span className="fx-pill-val">Nevşehir · {Math.round(wx.data.current.temperature_2m)}°C</span>
              <span className="fx-pill-label">rüzgar {Math.round(wx.data.current.wind_speed_10m)} km/sa</span>
            </span>
          ) : (
            <span className="fx-pill"><span className="fx-pill-label">Open-Meteo</span><span className="fx-pill-val">…</span></span>
          )}
        </div>

        <div className="scale-ruler">
          Ölçek · 0—500 km
          <div className="scale-ruler-bar" />
        </div>
      </section>

      <section className="login-form-side">
        <div />

        <div style={{ maxWidth: 460, width: '100%', alignSelf: 'center', margin: 'auto 0' }}>
          <div style={{ display: 'inline-flex', borderBottom: '1px solid var(--hairline-strong)', marginBottom: 36, gap: 24 }}>
            {(['login', 'register'] as const).map(t => (
              <button
                key={t}
                onClick={() => setTab(t)}
                style={{
                  background: 'none', border: 'none', cursor: 'pointer',
                  fontFamily: 'var(--mono)', fontSize: 11, letterSpacing: '0.18em', textTransform: 'uppercase',
                  padding: '10px 0', color: tab === t ? 'var(--ink)' : 'var(--ink-faded)',
                  borderBottom: tab === t ? '2px solid var(--tuff)' : '2px solid transparent',
                  marginBottom: -1, transition: 'all 200ms ease',
                }}
              >
                {t === 'login' ? 'Giriş' : 'Yeni Hesap'}
              </button>
            ))}
          </div>

          <div className="numerals" style={{ fontSize: 10, letterSpacing: '0.18em', textTransform: 'uppercase', color: 'var(--ink-faded)', marginBottom: 28 }}>
            § 01 — Kimlik Doğrulama
          </div>

          <AnimatePresence mode="wait">
            {tab === 'login' ? (
              <motion.form key="login" onSubmit={onLogin} style={{ display: 'flex', flexDirection: 'column', gap: 22 }}
                initial={{ opacity: 0, x: -8 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: 8 }} transition={{ duration: 0.25 }}>
                <h2 style={{ fontFamily: 'var(--display)', fontWeight: 500, fontSize: 38, lineHeight: 1.05, letterSpacing: '-0.02em' }}>
                  <em className="tuff-em">Atlas'a</em> giriş yap.
                </h2>
                <p className="lede" style={{ marginBottom: 12 }}>JWT token ile oturum, 60 dakika geçerli.</p>

                <div className="field">
                  <label className="field-label" htmlFor="email">E-posta</label>
                  <input className="field-input" id="email" type="email" autoComplete="email" placeholder="admin@raw2value.local"
                    {...lf.register('email', { required: true })} />
                </div>
                <div className="field">
                  <label className="field-label" htmlFor="password">Parola</label>
                  <input className="field-input" id="password" type="password" autoComplete="current-password" placeholder="••••••••"
                    {...lf.register('password', { required: true })} />
                </div>

                <div style={{ display: 'flex', gap: 12, alignItems: 'center', marginTop: 12 }}>
                  <button type="submit" className="btn btn-primary btn-arrow" disabled={busy}>
                    {busy ? <><span className="atlas-loader" /><span>Doğrulanıyor</span></> : <span>Giriş yap</span>}
                  </button>
                  <span className="numerals" style={{ fontSize: 10, color: 'var(--ink-faded)', letterSpacing: '0.16em', textTransform: 'uppercase' }}>⌘ + ↵</span>
                </div>

                <div style={{ marginTop: 6, display: 'flex', gap: 8, alignItems: 'center', flexWrap: 'wrap',
                  fontFamily: 'var(--mono)', fontSize: 10, letterSpacing: '0.1em', color: 'var(--ink-faded)' }}>
                  <span>Demo:</span>
                  <button type="button" onClick={fillDemo}
                    style={{ background: 'var(--bone-deep)', border: '1px solid transparent', padding: '5px 9px', borderRadius: 3, cursor: 'pointer',
                             fontFamily: 'var(--mono)', fontSize: 10, letterSpacing: '0.06em', color: 'var(--ink)' }}>
                    admin@raw2value.local
                  </button>
                </div>
              </motion.form>
            ) : (
              <motion.form key="register" onSubmit={onRegister} style={{ display: 'flex', flexDirection: 'column', gap: 22 }}
                initial={{ opacity: 0, x: 8 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -8 }} transition={{ duration: 0.25 }}>
                <h2 style={{ fontFamily: 'var(--display)', fontWeight: 500, fontSize: 38, lineHeight: 1.05, letterSpacing: '-0.02em' }}>
                  <em className="tuff-em">Yeni</em> kayıt.
                </h2>
                <p className="lede" style={{ marginBottom: 12 }}>Üretici, işleyici veya alıcı kuruluş için hesap aç.</p>

                <div className="field">
                  <label className="field-label">Ad Soyad</label>
                  <input className="field-input" type="text" placeholder="Mehmet Yıldız" {...rf.register('full_name', { required: true, minLength: 2 })} />
                </div>
                <div className="field">
                  <label className="field-label">E-posta</label>
                  <input className="field-input" type="email" placeholder="ornek@kuruluş.com" {...rf.register('email', { required: true })} />
                </div>
                <div className="field">
                  <label className="field-label">Parola (≥10 karakter)</label>
                  <input className="field-input" type="password" placeholder="••••••••••" {...rf.register('password', { required: true, minLength: 10 })} />
                  {rf.formState.errors.password && <span className="field-error">En az 10 karakter olmalı</span>}
                </div>

                <div style={{ display: 'flex', gap: 12, alignItems: 'center', marginTop: 12 }}>
                  <button type="submit" className="btn btn-tuff btn-arrow" disabled={busy}>
                    {busy ? <><span className="atlas-loader" /><span>Oluşturuluyor</span></> : <span>Hesap oluştur</span>}
                  </button>
                </div>
              </motion.form>
            )}
          </AnimatePresence>
        </div>

        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontFamily: 'var(--mono)', fontSize: 10, letterSpacing: '0.1em',
                      color: 'var(--ink-faded)', textTransform: 'uppercase', paddingTop: 24, borderTop: '1px solid var(--hairline)' }}>
          <span>RAW2VALUE · v0.1.0 · 2026</span>
          {health.isLoading
            ? <span>api · sınanıyor…</span>
            : health.data
              ? <span style={{ color: 'var(--co2-green)' }}>API · ONLINE · uptime {health.data.uptime_sec}s</span>
              : <span style={{ color: 'var(--co2-red)' }}>API · OFFLINE · localhost:8000 erişilemiyor</span>}
        </div>
      </section>
    </main>
  );
}
