import { useState } from 'react';
import {
  ChevronRight, RefreshCcw, TrendingUp, TrendingDown,
  CheckCircle2, ChevronDown, ChevronUp, Info, ArrowRight,
  Zap, BarChart2, AlertTriangle,
} from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, LineChart, Line } from 'recharts';
import { analyze, whatif } from '../lib/api';
import { useAnalysis } from '../contexts/AnalysisContext';
import type {
  RawMaterial, Quality, TransportMode, TargetCountry, Priority,
  AnalyzeRequest, WhatIfResultRow,
} from '../lib/types';

// ── Labels ────────────────────────────────────────────────────────────────
const MAT: Record<RawMaterial, string>    = { pomza: 'Pomza (Pumice)', perlit: 'Perlit', kabak_cekirdegi: 'Kabak Çekirdeği' };
const QUA: Record<Quality, string>        = { A: 'A Sınıfı (Yüksek)', B: 'B Sınıfı (Orta)', C: 'C Sınıfı (Düşük)', unknown: 'Bilinmiyor' };
const TRA: Record<TransportMode, string>  = { kara: 'Karayolu', deniz: 'Denizyolu', demiryolu: 'Demiryolu', hava: 'Havayolu' };
const COU: Record<TargetCountry, string>  = { TR: 'Türkiye', DE: 'Almanya', NL: 'Hollanda' };
const PRI: Record<Priority, string>       = { max_profit: 'Maksimum Kâr', low_carbon: 'Düşük Karbon', fast_delivery: 'Hızlı Teslimat' };

// ── Helper UI ─────────────────────────────────────────────────────────────
function SelectField<T extends string>({ label, value, options, onChange }: {
  label: string; value: T; options: Record<T, string>; onChange: (v: T) => void;
}) {
  return (
    <div>
      <label className="text-xs font-semibold text-r2v-charcoal/70 block mb-2">{label}</label>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value as T)}
        className="w-full bg-white border border-r2v-line rounded-xl px-3.5 py-2.5 text-sm font-medium text-r2v-charcoal outline-none cursor-pointer appearance-none focus:border-r2v-charcoal/40 focus:ring-2 focus:ring-r2v-charcoal/8 transition-all"
      >
        {(Object.entries(options) as [T, string][]).map(([k, v]) => (
          <option key={k} value={k}>{v}</option>
        ))}
      </select>
    </div>
  );
}

function InputField({ label, value, onChange, type = 'text', suffix = '', placeholder = '' }: {
  label: string; value: string | number; onChange: (v: string) => void;
  type?: string; suffix?: string; placeholder?: string;
}) {
  return (
    <div>
      <label className="text-xs font-semibold text-r2v-charcoal/70 block mb-2">{label}</label>
      <div className="flex items-center bg-white border border-r2v-line rounded-xl px-3.5 py-2.5 focus-within:border-r2v-charcoal/40 focus-within:ring-2 focus-within:ring-r2v-charcoal/8 transition-all">
        <input
          type={type}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          className="flex-1 bg-transparent border-none focus:ring-0 p-0 text-sm font-medium text-r2v-charcoal placeholder:text-r2v-muted/70 outline-none"
        />
        {suffix && <span className="text-xs font-semibold text-r2v-muted ml-1.5">{suffix}</span>}
      </div>
    </div>
  );
}

function KpiCard({ label, value, sub, accent }: { label: string; value: string; sub?: string; accent?: boolean }) {
  return (
    <div className={`p-5 rounded-2xl border ${accent ? 'border-r2v-green/30 bg-r2v-green/5' : 'border-r2v-line bg-white'}`}>
      <p className="text-xs font-semibold uppercase tracking-wide text-r2v-muted mb-2">{label}</p>
      <p className={`text-2xl font-semibold tracking-tight ${accent ? 'text-r2v-green' : 'text-r2v-charcoal'}`}>{value}</p>
      {sub && <p className="text-xs font-medium text-r2v-muted mt-1.5">{sub}</p>}
    </div>
  );
}

// ── Main Component ─────────────────────────────────────────────────────────
export default function UnifiedDashboard() {
  const { request, result, setAnalysis } = useAnalysis();

  // Form state
  const [rawMaterial, setRawMaterial] = useState<RawMaterial>('pomza');
  const [tonnage, setTonnage]         = useState('100');
  const [quality, setQuality]         = useState<Quality>('A');
  const [originCity, setOriginCity]   = useState('Nevşehir');
  const [targetCountry, setTargetCountry] = useState<TargetCountry>('DE');
  const [transportMode, setTransportMode] = useState<TransportMode>('deniz');
  const [priority, setPriority]       = useState<Priority>('max_profit');
  const [moisturePct, setMoisturePct] = useState('');
  const [purityPct, setPurityPct]     = useState('');
  const [particleSize, setParticleSize] = useState('');
  const [showAdvanced, setShowAdvanced] = useState(false);

  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analyzeError, setAnalyzeError] = useState<string | null>(null);
  const [showDetails, setShowDetails] = useState(false);

  // What-if state
  const [wfName, setWfName]           = useState('Senaryo 1');
  const [wfFxPct, setWfFxPct]         = useState(0);
  const [wfTonnage, setWfTonnage]     = useState('');
  const [wfTransport, setWfTransport] = useState<TransportMode | ''>('');
  const [wfResults, setWfResults]     = useState<WhatIfResultRow[]>([]);
  const [isRunning, setIsRunning]     = useState(false);
  const [wfError, setWfError]         = useState<string | null>(null);

  // ── Handlers ────────────────────────────────────────────────────────────
  const handleAnalyze = async () => {
    const t = parseFloat(tonnage);
    if (!originCity.trim() || isNaN(t) || t <= 0) {
      setAnalyzeError('Menşei şehir ve geçerli bir tonaj giriniz.'); return;
    }
    setAnalyzeError(null);
    setIsAnalyzing(true);
    const payload: AnalyzeRequest = {
      raw_material: rawMaterial, tonnage: t, quality, origin_city: originCity.trim(),
      target_country: targetCountry, transport_mode: transportMode, priority,
      input_mode: moisturePct || purityPct || particleSize ? 'advanced' : 'basic',
      ...(moisturePct ? { moisture_pct: parseFloat(moisturePct) } : {}),
      ...(purityPct   ? { purity_pct: parseFloat(purityPct) }     : {}),
      ...(particleSize ? { particle_size_class: particleSize }     : {}),
    };
    try {
      const res = await analyze(payload);
      setAnalysis(payload, res);
      setShowDetails(false);
      setWfResults([]);
    } catch (e) {
      setAnalyzeError(e instanceof Error ? e.message : 'Analiz hatası');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleWhatIf = async () => {
    if (!request) return;
    setWfError(null);
    setIsRunning(true);
    try {
      const res = await whatif({
        base_payload: request,
        scenarios: [{
          name: wfName,
          fx_scenario_pct: wfFxPct,
          ...(wfTonnage ? { tonnage_override: parseFloat(wfTonnage) } : {}),
          ...(wfTransport ? { transport_mode_override: wfTransport as TransportMode } : {}),
        }],
      });
      setWfResults((prev) => [res.results[0], ...prev].slice(0, 8));
      setWfName(`Senaryo ${wfResults.length + 2}`);
    } catch (e) {
      setWfError(e instanceof Error ? e.message : 'Hata');
    } finally {
      setIsRunning(false);
    }
  };

  const applyPreset = (name: string, fx: number, ton: string, tr: TransportMode | '') => {
    setWfName(name); setWfFxPct(fx); setWfTonnage(ton); setWfTransport(tr);
  };

  const baseProfit = result?.expected_profit_try ?? 0;
  const shapData   = result?.feature_importance.slice(0, 6) ?? [];
  const chartData  = wfResults.map((r) => ({ name: r.scenario, kar: Math.round(r.expected_profit_try / 1000) }));

  // ── Render ───────────────────────────────────────────────────────────────
  return (
    <div className="flex h-[calc(100vh-64px)] overflow-hidden bg-r2v-soft">

      {/* ═══════════ LEFT: FORM PANEL ═══════════ */}
      <aside className="w-80 xl:w-[340px] shrink-0 flex flex-col border-r border-r2v-line bg-white overflow-y-auto">
        <div className="p-6 border-b border-r2v-line">
          <div className="flex items-center gap-2 mb-1">
            <div className="w-7 h-7 rounded-lg bg-r2v-terracotta/10 flex items-center justify-center">
              <Zap className="w-4 h-4 text-r2v-terracotta" />
            </div>
            <h2 className="text-base font-semibold text-r2v-charcoal tracking-tight">Analiz Girişi</h2>
          </div>
          <p className="text-sm text-r2v-muted">Hammadde ve lojistik parametrelerini girin.</p>
        </div>

        <div className="flex-1 p-6 space-y-5">
          <SelectField label="Hammadde Tipi" value={rawMaterial} options={MAT} onChange={setRawMaterial} />
          <InputField  label="Menşei Şehir"  value={originCity}  onChange={setOriginCity}  placeholder="Nevşehir" />
          <InputField  label="Parti Tonajı"  value={tonnage}     onChange={setTonnage}     type="number" suffix="ton" placeholder="100" />
          <SelectField label="Kalite Sınıfı" value={quality}     options={QUA} onChange={setQuality} />
          <SelectField label="Hedef Ülke"    value={targetCountry} options={COU} onChange={setTargetCountry} />
          <SelectField label="Taşıma Modu"   value={transportMode} options={TRA} onChange={setTransportMode} />
          <SelectField label="Öncelik"       value={priority}    options={PRI} onChange={setPriority} />

          {/* Advanced toggle */}
          <button
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="w-full text-left text-xs font-semibold text-r2v-muted hover:text-r2v-charcoal flex items-center gap-1.5 transition-colors pt-3 border-t border-r2v-line"
          >
            {showAdvanced ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
            Fiziksel Parametreler (Opsiyonel)
          </button>

          {showAdvanced && (
            <div className="space-y-4 pt-1">
              <InputField label="Nem Oranı"   value={moisturePct}  onChange={setMoisturePct}  type="number" suffix="%" placeholder="12" />
              <InputField label="Saflık"       value={purityPct}    onChange={setPurityPct}    type="number" suffix="%" placeholder="95" />
              <InputField label="Tane Sınıfı"  value={particleSize} onChange={setParticleSize} placeholder="mikronize, 0-5mm..." />
            </div>
          )}
        </div>

        {analyzeError && (
          <div className="mx-6 mb-4 p-3.5 bg-r2v-terracotta/8 border border-r2v-terracotta/25 rounded-xl text-sm text-r2v-terracotta font-medium">
            {analyzeError}
          </div>
        )}

        <div className="p-6 border-t border-r2v-line bg-r2v-soft">
          <button
            onClick={handleAnalyze}
            disabled={isAnalyzing}
            className="w-full bg-r2v-charcoal text-white h-12 rounded-full flex items-center justify-center gap-2 hover:bg-r2v-terracotta transition-colors disabled:opacity-60 text-sm font-semibold shadow-sm"
          >
            {isAnalyzing ? (
              <><div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" /> AI Analiz Çalışıyor...</>
            ) : (
              <><ChevronRight className="w-4 h-4" /> Analizi Başlat</>
            )}
          </button>
          <p className="text-xs font-mono text-center text-r2v-muted mt-3">
            3 AI modeli · CatBoost · mock-v1.0
          </p>
        </div>
      </aside>

      {/* ═══════════ RIGHT: RESULTS + WHATIF ═══════════ */}
      <main className="flex-1 overflow-y-auto">

        {/* ── COCKPIT SECTION ── */}
        {!result ? (
          <div className="flex flex-col items-center justify-center h-full gap-5 text-center px-8">
            <div className="w-20 h-20 rounded-3xl bg-white border border-r2v-line flex items-center justify-center shadow-sm">
              <BarChart2 className="w-9 h-9 text-r2v-muted" />
            </div>
            <div>
              <p className="text-r2v-charcoal text-base font-semibold mb-1">
                Analize Hazır
              </p>
              <p className="text-r2v-muted text-sm max-w-sm leading-relaxed">
                Soldaki formu doldurun ve <strong className="font-semibold text-r2v-charcoal">"Analizi Başlat"</strong>'a basın.
                Pomza, perlit ve kabak çekirdeği için rota optimizasyonu yapılacak.
              </p>
            </div>
          </div>
        ) : (
          <div className="p-8 space-y-6 max-w-[1400px] mx-auto">

            {/* Breadcrumb */}
            <div className="flex items-center gap-2 text-sm font-medium text-r2v-muted flex-wrap">
              <span className="text-r2v-charcoal font-semibold">{MAT[request!.raw_material]}</span>
              <ArrowRight className="w-3.5 h-3.5" />
              <span>{request!.origin_city}</span>
              <ArrowRight className="w-3.5 h-3.5" />
              <span>{COU[request!.target_country]}</span>
              <span className="ml-auto text-xs font-mono text-r2v-muted">
                {result.duration_ms}ms · {result.model_version}
              </span>
            </div>

            {/* Warnings */}
            {result.confidence.warnings.map((w, i) => (
              <div key={i} className="flex items-start gap-2.5 p-4 bg-r2v-terracotta/8 border border-r2v-terracotta/25 rounded-2xl text-sm text-r2v-charcoal">
                <AlertTriangle className="w-4 h-4 text-r2v-terracotta shrink-0 mt-0.5" />
                <span>{w}</span>
              </div>
            ))}

            {/* Hero result */}
            <div className="bg-white border border-r2v-line rounded-3xl p-7 shadow-sm">
              <div className="flex items-start justify-between gap-6 mb-7 flex-wrap">
                <div>
                  <div className="flex items-center gap-2 text-r2v-green text-xs font-bold uppercase tracking-wider mb-3">
                    <CheckCircle2 className="w-4 h-4" /> AI Önerisi Onaylandı
                  </div>
                  <h2 className="text-2xl md:text-3xl font-semibold text-r2v-charcoal tracking-tight leading-tight">
                    {result.recommended_route}
                  </h2>
                </div>
                <div className="text-right shrink-0">
                  <p className="text-xs font-semibold uppercase tracking-wider text-r2v-muted mb-1.5">AI Güveni</p>
                  <p className="text-4xl font-semibold tracking-tight text-r2v-charcoal">
                    {Math.round(result.confidence.overall * 100)}<span className="text-xl text-r2v-muted">/100</span>
                  </p>
                  <p className={`text-xs font-bold uppercase tracking-wider mt-1 ${result.confidence.overall >= 0.8 ? 'text-r2v-green' : 'text-r2v-muted'}`}>
                    {result.confidence.overall >= 0.8 ? 'Yüksek Kesinlik' : 'Orta Kesinlik'}
                  </p>
                </div>
              </div>

              {/* KPIs */}
              <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                <KpiCard label="Net Kâr (TL)" value={result.expected_profit_try.toLocaleString('tr-TR', { maximumFractionDigits: 0 })} accent />
                <KpiCard label="Değer Artışı" value={`+%${result.value_uplift_pct.toFixed(1)}`} sub="ham satışa göre" />
                <KpiCard label="Toplam CO₂" value={`${result.co2_kg.toLocaleString('tr-TR', { maximumFractionDigits: 0 })} kg`} />
                <KpiCard label="EUR/TRY (TCMB)" value={result.fx_used.eur_try.toFixed(2)} sub={`USD: ${result.fx_used.usd_try.toFixed(2)}`} />
              </div>

              {/* Toggle details */}
              <button
                onClick={() => setShowDetails(!showDetails)}
                className="mt-5 inline-flex items-center gap-1.5 text-sm font-semibold text-r2v-charcoal hover:text-r2v-terracotta transition-colors px-4 py-2 rounded-full border border-r2v-line hover:border-r2v-terracotta/40"
              >
                {showDetails ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                {showDetails ? 'Detayları Gizle' : 'Detayları Gör (Faktörler · Rotalar · Alıcılar)'}
              </button>
            </div>

            {/* Details expanded */}
            {showDetails && (
              <div className="grid grid-cols-1 xl:grid-cols-12 gap-6">

                {/* Feature Importance */}
                <div className="xl:col-span-5 bg-white border border-r2v-line rounded-3xl p-6 shadow-sm">
                  <h3 className="text-sm font-semibold uppercase tracking-wide text-r2v-muted mb-5">
                    Karar Faktörleri (Feature Importance)
                  </h3>
                  <div className="h-44">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={shapData} layout="vertical" margin={{ top: 0, right: 8, left: 0, bottom: 0 }}>
                        <XAxis type="number" hide />
                        <YAxis dataKey="feature" type="category" axisLine={false} tickLine={false}
                          tick={{ fontSize: 12, fill: '#2D323A' }} width={170} />
                        <Tooltip cursor={{ fill: 'rgba(45,50,58,0.04)' }}
                          contentStyle={{ border: '1px solid #E6E3DD', borderRadius: 12, fontSize: 12, fontFamily: 'Inter' }} />
                        <Bar dataKey="importance" fill="#6B8E78" barSize={14} radius={[0, 6, 6, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>

                  {/* Reason codes */}
                  {result.reason_codes.length > 0 && (
                    <div className="mt-6 pt-5 border-t border-r2v-line space-y-3">
                      <p className="text-sm font-semibold uppercase tracking-wide text-r2v-muted">Karar Gerekçeleri</p>
                      {result.reason_codes.map((r, i) => (
                        <div key={i} className="flex gap-3">
                          <span className="text-r2v-terracotta font-mono text-xs font-bold shrink-0 mt-0.5 w-5">0{i + 1}</span>
                          <p className="text-sm text-r2v-charcoal/85 leading-relaxed">{r.text}</p>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {/* Route Alternatives */}
                <div className="xl:col-span-4 bg-white border border-r2v-line rounded-3xl p-6 shadow-sm">
                  <h3 className="text-sm font-semibold uppercase tracking-wide text-r2v-muted mb-5">Tüm Rotalar</h3>
                  <div className="space-y-1">
                    {result.route_alternatives.map((r) => {
                      const isRec = r.route === result.recommended_route;
                      return (
                        <div key={r.route} className={`p-3 rounded-2xl ${isRec ? 'bg-r2v-green/8 border border-r2v-green/25' : 'bg-r2v-soft/60 hover:bg-r2v-soft'} transition-colors`}>
                          <div className="flex items-start justify-between gap-2">
                            <div className="flex items-center gap-2 min-w-0">
                              <div className={`w-2.5 h-2.5 rounded-full shrink-0 mt-1.5 ${isRec ? 'bg-r2v-green' : 'bg-r2v-muted/40'}`} />
                              <span className={`text-sm leading-snug ${isRec ? 'font-bold text-r2v-charcoal' : 'font-medium text-r2v-charcoal/80'}`}>{r.route}</span>
                            </div>
                            {isRec && <span className="text-[10px] font-bold text-r2v-green uppercase tracking-wider shrink-0 px-2 py-0.5 rounded-full bg-r2v-green/15">✓ Önerilen</span>}
                          </div>
                          <div className="flex gap-3 mt-2 ml-5 text-xs font-mono text-r2v-muted flex-wrap">
                            <span className="font-semibold text-r2v-charcoal/75">{r.profit_try.toLocaleString('tr-TR', { maximumFractionDigits: 0 })} TL</span>
                            <span>+%{r.value_uplift_pct.toFixed(0)}</span>
                            <span>{r.co2_kg.toLocaleString('tr-TR', { maximumFractionDigits: 0 })} kg CO₂</span>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>

                {/* Buyer Matches */}
                <div className="xl:col-span-3 bg-white border border-r2v-line rounded-3xl p-6 shadow-sm">
                  <div className="flex items-center justify-between mb-5">
                    <h3 className="text-sm font-semibold uppercase tracking-wide text-r2v-muted">Alıcı Eşleşmeleri</h3>
                    <span className="text-[10px] font-bold text-r2v-terracotta uppercase tracking-wider px-2 py-1 rounded-full bg-r2v-terracotta/10">
                      {COU[request!.target_country]}
                    </span>
                  </div>
                  <div className="space-y-1">
                    {result.match_results.slice(0, 5).map((m, i) => (
                      <div key={i} className="p-3 rounded-2xl hover:bg-r2v-soft transition-colors flex items-center justify-between gap-2">
                        <div className="min-w-0">
                          <p className="text-sm font-semibold text-r2v-charcoal truncate">{m.buyer}</p>
                          <p className="text-xs text-r2v-muted truncate">{m.processor}</p>
                        </div>
                        <span className={`text-sm font-mono font-bold shrink-0 px-2 py-1 rounded-lg ${m.score >= 0.85 ? 'text-r2v-green bg-r2v-green/10' : 'text-r2v-charcoal/70 bg-r2v-soft'}`}>
                          %{(m.score * 100).toFixed(0)}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* ── WHAT-IF SECTION ── */}
            <div className="bg-white border border-r2v-line rounded-3xl shadow-sm">
              <div className="flex items-center justify-between gap-4 p-6 border-b border-r2v-line flex-wrap">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <div className="w-7 h-7 rounded-lg bg-r2v-charcoal/8 flex items-center justify-center">
                      <BarChart2 className="w-4 h-4 text-r2v-charcoal" />
                    </div>
                    <h3 className="text-base font-semibold text-r2v-charcoal tracking-tight">What-if Simülatör</h3>
                  </div>
                  <p className="text-sm text-r2v-muted">Kur, tonaj ve taşıma değişimi etkisi — baz: <span className="font-medium text-r2v-charcoal/80">{result.recommended_route}</span></p>
                </div>
                <div className="flex items-center gap-1.5 text-xs font-semibold text-r2v-muted">
                  <span>{wfResults.length} senaryo çalıştı</span>
                </div>
              </div>

              <div className="p-6">
                {/* Controls */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-5 mb-6">
                  {/* FX slider */}
                  <div className="md:col-span-1">
                    <div className="flex justify-between items-end mb-2">
                      <label className="text-xs font-semibold text-r2v-charcoal/70 flex items-center gap-1">
                        Kur Değişimi <Info className="w-3.5 h-3.5 opacity-50" />
                      </label>
                      <span className={`text-sm font-mono font-bold ${wfFxPct > 0 ? 'text-r2v-green' : wfFxPct < 0 ? 'text-r2v-terracotta' : 'text-r2v-muted'}`}>
                        {wfFxPct > 0 ? '+' : ''}{(wfFxPct * 100).toFixed(0)}%
                      </span>
                    </div>
                    <input
                      type="range" min={-20} max={20} step={1}
                      value={wfFxPct * 100}
                      onChange={(e) => setWfFxPct(Number(e.target.value) / 100)}
                      className="w-full h-1.5 bg-r2v-line rounded-full appearance-none cursor-pointer accent-r2v-charcoal"
                    />
                    <div className="flex justify-between text-[10px] font-mono text-r2v-muted mt-1.5"><span>-20%</span><span>+20%</span></div>
                  </div>

                  {/* Tonnage */}
                  <div>
                    <label className="text-xs font-semibold text-r2v-charcoal/70 block mb-2">Tonaj Override</label>
                    <div className="flex items-center bg-white border border-r2v-line rounded-xl px-3 py-2 focus-within:border-r2v-charcoal/40 transition-colors">
                      <input
                        type="number" value={wfTonnage}
                        onChange={(e) => setWfTonnage(e.target.value)}
                        placeholder={`Mevcut: ${request!.tonnage}`}
                        className="flex-1 bg-transparent border-none focus:ring-0 p-0 text-sm font-medium text-r2v-charcoal outline-none placeholder:text-r2v-muted/70"
                      />
                      <span className="text-xs font-semibold text-r2v-muted ml-1">ton</span>
                    </div>
                  </div>

                  {/* Transport */}
                  <div>
                    <label className="text-xs font-semibold text-r2v-charcoal/70 block mb-2">Taşıma Modu</label>
                    <select
                      value={wfTransport}
                      onChange={(e) => setWfTransport(e.target.value as TransportMode | '')}
                      className="w-full bg-white border border-r2v-line rounded-xl px-3 py-2.5 text-sm font-medium text-r2v-charcoal outline-none cursor-pointer focus:border-r2v-charcoal/40 transition-colors"
                    >
                      <option value="">— Mevcut —</option>
                      {(Object.entries(TRA) as [TransportMode, string][]).map(([k, v]) => (
                        <option key={k} value={k}>{v}</option>
                      ))}
                    </select>
                  </div>

                  {/* Name + Run */}
                  <div className="flex flex-col justify-between">
                    <div>
                      <label className="text-xs font-semibold text-r2v-charcoal/70 block mb-2">Senaryo Adı</label>
                      <input
                        type="text" value={wfName} maxLength={30}
                        onChange={(e) => setWfName(e.target.value)}
                        className="w-full bg-white border border-r2v-line rounded-xl px-3 py-2 text-sm font-semibold text-r2v-charcoal outline-none focus:border-r2v-charcoal/40 transition-colors"
                      />
                    </div>
                    <button
                      onClick={handleWhatIf}
                      disabled={isRunning}
                      className="mt-3 w-full bg-r2v-charcoal text-white h-10 rounded-full flex items-center justify-center gap-1.5 hover:bg-r2v-terracotta transition-colors disabled:opacity-60 text-sm font-semibold"
                    >
                      {isRunning ? <><div className="w-3.5 h-3.5 border border-white border-t-transparent rounded-full animate-spin" /> Hesaplanıyor</> : 'Çalıştır ▶'}
                    </button>
                  </div>
                </div>

                {/* Presets */}
                <div className="flex flex-wrap items-center gap-2 mb-6">
                  <span className="text-xs font-semibold text-r2v-muted mr-1">Hazır:</span>
                  {[
                    { label: 'Baz',       fx: 0,    ton: '',                          tr: '' },
                    { label: 'Kur +10%',  fx: 0.10, ton: '',                          tr: '' },
                    { label: 'Kur -10%',  fx:-0.10, ton: '',                          tr: '' },
                    { label: 'Tonaj ×2',  fx: 0,    ton: String(request!.tonnage * 2), tr: '' },
                    { label: 'Havayolu',  fx: 0,    ton: '',                          tr: 'hava' },
                    { label: 'Demiryolu', fx: 0,    ton: '',                          tr: 'demiryolu' },
                  ].map((p) => (
                    <button key={p.label}
                      onClick={() => applyPreset(p.label, p.fx, p.ton, p.tr as TransportMode | '')}
                      className="px-3.5 py-1.5 bg-r2v-soft border border-r2v-line text-xs font-semibold text-r2v-charcoal/80 hover:bg-r2v-charcoal hover:text-white hover:border-r2v-charcoal rounded-full transition-colors"
                    >
                      {p.label}
                    </button>
                  ))}
                  {wfResults.length > 0 && (
                    <button onClick={() => setWfResults([])} className="ml-auto inline-flex items-center gap-1.5 text-xs font-semibold text-r2v-muted hover:text-r2v-terracotta transition-colors">
                      <RefreshCcw className="w-3.5 h-3.5" /> Sıfırla
                    </button>
                  )}
                </div>

                {wfError && (
                  <div className="mb-5 p-3.5 bg-r2v-terracotta/8 border border-r2v-terracotta/25 rounded-xl text-sm text-r2v-terracotta">{wfError}</div>
                )}

                {/* Results */}
                {wfResults.length === 0 ? (
                  <div className="flex items-center justify-center py-12 text-center bg-r2v-soft/50 rounded-2xl border border-dashed border-r2v-line">
                    <p className="text-sm text-r2v-muted">
                      Parametre seçin → <strong className="text-r2v-charcoal/80">Çalıştır</strong> butonuna basın → Sonuçlar burada görünür
                    </p>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
                    {/* Table */}
                    <div className="overflow-x-auto rounded-2xl border border-r2v-line">
                      <table className="w-full text-left border-collapse">
                        <thead className="bg-r2v-soft">
                          <tr className="text-xs font-semibold uppercase tracking-wide text-r2v-muted">
                            <th className="py-3 px-4">Senaryo</th>
                            <th className="py-3 px-4 text-right">Kâr (TL)</th>
                            <th className="py-3 px-4 text-right">CO₂ (kg)</th>
                            <th className="py-3 px-4">Rota</th>
                            <th className="py-3 px-4 text-center">∆</th>
                          </tr>
                        </thead>
                        <tbody className="bg-white">
                          {/* Base row */}
                          <tr className="border-t border-r2v-line bg-r2v-soft/50">
                            <td className="py-3 px-4 text-sm font-semibold text-r2v-muted">Baz Analiz</td>
                            <td className="py-3 px-4 text-right font-mono text-sm text-r2v-muted">{baseProfit.toLocaleString('tr-TR', { maximumFractionDigits: 0 })}</td>
                            <td className="py-3 px-4 text-right font-mono text-sm text-r2v-muted">{result.co2_kg.toLocaleString('tr-TR', { maximumFractionDigits: 0 })}</td>
                            <td className="py-3 px-4 text-xs text-r2v-muted">{result.recommended_route.split('(')[0].trim()}</td>
                            <td className="py-3 px-4 text-center text-r2v-muted/50 text-xs">—</td>
                          </tr>
                          {wfResults.map((row, i) => (
                            <tr key={i} className="border-t border-r2v-line hover:bg-r2v-soft transition-colors">
                              <td className="py-3 px-4 text-sm font-semibold text-r2v-charcoal">{row.scenario}</td>
                              <td className={`py-3 px-4 text-right font-mono text-sm font-bold ${row.expected_profit_try > baseProfit ? 'text-r2v-green' : 'text-r2v-terracotta'}`}>
                                {row.expected_profit_try.toLocaleString('tr-TR', { maximumFractionDigits: 0 })}
                              </td>
                              <td className={`py-3 px-4 text-right font-mono text-sm ${row.co2_kg < result.co2_kg ? 'text-r2v-green' : 'text-r2v-terracotta'}`}>
                                {row.co2_kg.toLocaleString('tr-TR', { maximumFractionDigits: 0 })}
                              </td>
                              <td className="py-3 px-4 text-xs text-r2v-charcoal/75">{row.recommended_route.split('(')[0].trim()}</td>
                              <td className="py-3 px-4 text-center">
                                {row.expected_profit_try > baseProfit
                                  ? <TrendingUp className="w-4 h-4 text-r2v-green mx-auto" />
                                  : <TrendingDown className="w-4 h-4 text-r2v-terracotta mx-auto" />}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>

                    {/* Chart */}
                    {wfResults.length >= 2 && (
                      <div>
                        <p className="text-xs font-semibold uppercase tracking-wide text-r2v-muted mb-3">Kâr Karşılaştırması (bin TL)</p>
                        <div className="h-52 bg-r2v-soft/40 rounded-2xl border border-r2v-line p-3">
                          <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={[{ name: 'Baz', kar: Math.round(baseProfit / 1000) }, ...chartData]}
                              margin={{ top: 0, right: 0, left: 0, bottom: 0 }}>
                              <XAxis dataKey="name" axisLine={false} tickLine={false}
                                tick={{ fontSize: 11, fontFamily: 'Inter', fill: '#2D323A' }} />
                              <YAxis axisLine={false} tickLine={false}
                                tick={{ fontSize: 11, fontFamily: 'Inter', fill: '#6B6F76' }} width={32} />
                              <Tooltip cursor={{ fill: 'rgba(45,50,58,0.04)' }}
                                contentStyle={{ border: '1px solid #E6E3DD', borderRadius: 12, fontSize: 12, fontFamily: 'Inter' }} />
                              <Bar dataKey="kar" fill="#2D323A" fillOpacity={0.85} barSize={26} radius={[8, 8, 0, 0]} />
                            </BarChart>
                          </ResponsiveContainer>
                        </div>
                        {/* Line chart: profit trend */}
                        {wfResults.length >= 3 && (
                          <div className="mt-4">
                            <p className="text-xs font-semibold uppercase tracking-wide text-r2v-muted mb-3">Senaryo Kâr Trendi</p>
                            <div className="h-36 bg-r2v-soft/40 rounded-2xl border border-r2v-line p-3">
                              <ResponsiveContainer width="100%" height="100%">
                                <LineChart data={chartData} margin={{ top: 0, right: 0, left: 0, bottom: 0 }}>
                                  <XAxis dataKey="name" axisLine={false} tickLine={false}
                                    tick={{ fontSize: 11, fontFamily: 'Inter', fill: '#6B6F76' }} />
                                  <YAxis axisLine={false} tickLine={false}
                                    tick={{ fontSize: 11, fontFamily: 'Inter', fill: '#6B6F76' }} width={32} />
                                  <Tooltip cursor={{ stroke: '#E6E3DD', strokeWidth: 1 }}
                                    contentStyle={{ border: '1px solid #E6E3DD', borderRadius: 12, fontSize: 12, fontFamily: 'Inter' }} />
                                  <Line type="monotone" dataKey="kar" stroke="#6B8E78" strokeWidth={2.5} dot={{ r: 4, fill: '#6B8E78' }} />
                                </LineChart>
                              </ResponsiveContainer>
                            </div>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
