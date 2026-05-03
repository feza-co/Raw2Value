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
      <label className="text-[9px] font-bold uppercase tracking-widest text-r2v-charcoal/40 block mb-1">{label}</label>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value as T)}
        className="w-full bg-transparent border-b border-r2v-charcoal/15 pb-1.5 text-sm font-medium text-r2v-charcoal outline-none cursor-pointer appearance-none focus:border-r2v-charcoal/50 transition-colors"
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
      <label className="text-[9px] font-bold uppercase tracking-widest text-r2v-charcoal/40 block mb-1">{label}</label>
      <div className="flex items-center border-b border-r2v-charcoal/15 pb-1.5 focus-within:border-r2v-charcoal/50 transition-colors">
        <input
          type={type}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          className="flex-1 bg-transparent border-none focus:ring-0 p-0 text-sm font-medium text-r2v-charcoal placeholder:text-r2v-charcoal/20 outline-none"
        />
        {suffix && <span className="text-[9px] font-bold text-r2v-charcoal/30 uppercase tracking-widest ml-1">{suffix}</span>}
      </div>
    </div>
  );
}

function KpiCard({ label, value, sub, accent }: { label: string; value: string; sub?: string; accent?: boolean }) {
  return (
    <div className={`p-4 border ${accent ? 'border-r2v-green/30 bg-r2v-green/5' : 'border-r2v-charcoal/10 bg-white/60'}`}>
      <p className="text-[9px] font-bold uppercase tracking-widest text-r2v-charcoal/50 mb-1">{label}</p>
      <p className={`text-2xl font-light font-mono ${accent ? 'text-r2v-green' : 'text-r2v-charcoal'}`}>{value}</p>
      {sub && <p className="text-[10px] font-bold uppercase tracking-widest text-r2v-charcoal/40 mt-1">{sub}</p>}
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
    <div className="flex h-[calc(100vh-56px)] overflow-hidden">

      {/* ═══════════ LEFT: FORM PANEL ═══════════ */}
      <aside className="w-72 xl:w-80 shrink-0 flex flex-col border-r border-r2v-charcoal/10 bg-r2v-base overflow-y-auto">
        <div className="p-5 border-b border-r2v-charcoal/10">
          <div className="flex items-center gap-2 mb-0.5">
            <Zap className="w-3.5 h-3.5 text-r2v-terracotta" />
            <h2 className="text-xs font-bold uppercase tracking-widest text-r2v-charcoal">Analiz Girişi</h2>
          </div>
          <p className="text-[10px] text-r2v-charcoal/40">Hammadde ve lojistik parametrelerini girin</p>
        </div>

        <div className="flex-1 p-5 space-y-5">
          <SelectField label="Hammadde Tipi" value={rawMaterial} options={MAT} onChange={setRawMaterial} />
          <InputField  label="Menşei Şehir"  value={originCity}  onChange={setOriginCity}  placeholder="Nevşehir" />
          <InputField  label="Parti Tonajı"  value={tonnage}     onChange={setTonnage}     type="number" suffix="TON" placeholder="100" />
          <SelectField label="Kalite Sınıfı" value={quality}     options={QUA} onChange={setQuality} />
          <SelectField label="Hedef Ülke"    value={targetCountry} options={COU} onChange={setTargetCountry} />
          <SelectField label="Taşıma Modu"   value={transportMode} options={TRA} onChange={setTransportMode} />
          <SelectField label="Öncelik"       value={priority}    options={PRI} onChange={setPriority} />

          {/* Advanced toggle */}
          <button
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="w-full text-left text-[9px] font-bold uppercase tracking-widest text-r2v-charcoal/40 hover:text-r2v-charcoal flex items-center gap-1 transition-colors pt-1 border-t border-r2v-charcoal/8"
          >
            {showAdvanced ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
            Fiziksel Parametreler (Opsiyonel)
          </button>

          {showAdvanced && (
            <div className="space-y-4 pt-1">
              <InputField label="Nem Oranı"    value={moisturePct}  onChange={setMoisturePct}  type="number" suffix="%" placeholder="12" />
              <InputField label="Saflık"        value={purityPct}    onChange={setPurityPct}    type="number" suffix="%" placeholder="95" />
              <InputField label="Tane Sınıfı"   value={particleSize} onChange={setParticleSize} placeholder="mikronize, 0-5mm..." />
            </div>
          )}
        </div>

        {analyzeError && (
          <div className="mx-5 mb-3 p-3 bg-r2v-terracotta/10 border border-r2v-terracotta/20 text-xs text-r2v-terracotta font-medium">
            {analyzeError}
          </div>
        )}

        <div className="p-5 border-t border-r2v-charcoal/10">
          <button
            onClick={handleAnalyze}
            disabled={isAnalyzing}
            className="w-full bg-r2v-charcoal text-white h-11 flex items-center justify-center gap-2 hover:bg-r2v-charcoal/85 transition-colors disabled:opacity-60 text-xs font-bold uppercase tracking-widest"
          >
            {isAnalyzing ? (
              <><div className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" /> AI Analiz Çalışıyor...</>
            ) : (
              <><ChevronRight className="w-4 h-4" /> Analizi Başlat</>
            )}
          </button>
          <p className="text-[9px] font-mono text-center text-r2v-charcoal/30 mt-2">
            3 AI modeli · CatBoost · mock-v1.0
          </p>
        </div>
      </aside>

      {/* ═══════════ RIGHT: RESULTS + WHATIF ═══════════ */}
      <main className="flex-1 overflow-y-auto bg-r2v-surface/30">

        {/* ── COCKPIT SECTION ── */}
        {!result ? (
          <div className="flex flex-col items-center justify-center h-80 gap-4 text-center px-8 mt-16">
            <div className="w-14 h-14 rounded-full bg-r2v-charcoal/5 flex items-center justify-center">
              <BarChart2 className="w-6 h-6 text-r2v-charcoal/20" />
            </div>
            <p className="text-r2v-charcoal/40 text-sm font-medium">
              Soldaki formu doldurun ve<br/>"Analizi Başlat"a basın
            </p>
            <p className="text-[10px] text-r2v-charcoal/25 font-mono">
              Pomza · Perlit · Kabak Çekirdeği için rota optimizasyonu
            </p>
          </div>
        ) : (
          <div className="p-6 space-y-6">

            {/* Breadcrumb */}
            <div className="flex items-center gap-2 text-[10px] font-bold uppercase tracking-widest text-r2v-charcoal/40">
              <span>{MAT[request!.raw_material]}</span>
              <ArrowRight className="w-3 h-3" />
              <span>{request!.origin_city}</span>
              <ArrowRight className="w-3 h-3" />
              <span>{COU[request!.target_country]}</span>
              <span className="ml-auto text-r2v-charcoal/25 font-mono normal-case">{result.duration_ms}ms · {result.model_version}</span>
            </div>

            {/* Warnings */}
            {result.confidence.warnings.map((w, i) => (
              <div key={i} className="flex items-start gap-2 p-3 bg-r2v-terracotta/5 border border-r2v-terracotta/20 text-xs text-r2v-charcoal/70">
                <AlertTriangle className="w-3.5 h-3.5 text-r2v-terracotta shrink-0 mt-0.5" />
                {w}
              </div>
            ))}

            {/* Hero result */}
            <div className="bg-white border border-r2v-charcoal/10 p-6">
              <div className="flex items-start justify-between gap-4 mb-6">
                <div>
                  <div className="flex items-center gap-2 text-r2v-green text-[10px] font-bold uppercase tracking-widest mb-2">
                    <CheckCircle2 className="w-3.5 h-3.5" /> AI Önerisi Onaylandı
                  </div>
                  <h2 className="text-2xl font-bold text-r2v-charcoal tracking-tight">{result.recommended_route}</h2>
                </div>
                <div className="text-right shrink-0">
                  <p className="text-[9px] font-bold uppercase tracking-widest text-r2v-charcoal/40 mb-1">AI Güveni</p>
                  <p className="text-3xl font-mono font-light text-r2v-charcoal">
                    {Math.round(result.confidence.overall * 100)}<span className="text-base text-r2v-charcoal/30">/100</span>
                  </p>
                  <p className={`text-[9px] font-bold uppercase tracking-widest mt-0.5 ${result.confidence.overall >= 0.8 ? 'text-r2v-green' : 'text-r2v-charcoal/50'}`}>
                    {result.confidence.overall >= 0.8 ? 'Yüksek Kesinlik' : 'Orta Kesinlik'}
                  </p>
                </div>
              </div>

              {/* KPIs */}
              <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
                <KpiCard label="Net Kâr (TL)" value={result.expected_profit_try.toLocaleString('tr-TR', { maximumFractionDigits: 0 })} accent />
                <KpiCard label="Değer Artışı" value={`+%${result.value_uplift_pct.toFixed(1)}`} sub="ham satışa göre" />
                <KpiCard label="Toplam CO₂" value={`${result.co2_kg.toLocaleString('tr-TR', { maximumFractionDigits: 0 })} kg`} />
                <KpiCard label="EUR/TRY (TCMB)" value={result.fx_used.eur_try.toFixed(2)} sub={`USD: ${result.fx_used.usd_try.toFixed(2)}`} />
              </div>

              {/* Toggle details */}
              <button
                onClick={() => setShowDetails(!showDetails)}
                className="mt-4 flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-widest text-r2v-charcoal/50 hover:text-r2v-charcoal transition-colors"
              >
                {showDetails ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                {showDetails ? 'Detayları Gizle' : 'Detayları Gör (Faktörler · Rotalar · Alıcılar)'}
              </button>
            </div>

            {/* Details expanded */}
            {showDetails && (
              <div className="grid grid-cols-1 xl:grid-cols-12 gap-6 animate-in fade-in slide-in-from-top-2 duration-300">

                {/* Feature Importance */}
                <div className="xl:col-span-5 bg-white border border-r2v-charcoal/10 p-5">
                  <h3 className="text-[10px] font-bold uppercase tracking-widest text-r2v-charcoal/50 mb-4">Karar Faktörleri (Feature Importance)</h3>
                  <div className="h-40">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={shapData} layout="vertical" margin={{ top: 0, right: 8, left: 0, bottom: 0 }}>
                        <XAxis type="number" hide />
                        <YAxis dataKey="feature" type="category" axisLine={false} tickLine={false}
                          tick={{ fontSize: 10, fill: '#2D323A', opacity: 0.6 }} width={160} />
                        <Tooltip cursor={{ fill: 'transparent' }}
                          contentStyle={{ border: '1px solid #2D323A20', borderRadius: 0, fontSize: 10, fontFamily: 'monospace' }} />
                        <Bar dataKey="importance" fill="#6B8E78" barSize={10} radius={[0, 3, 3, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>

                  {/* Reason codes */}
                  {result.reason_codes.length > 0 && (
                    <div className="mt-5 pt-4 border-t border-r2v-charcoal/8 space-y-3">
                      <p className="text-[9px] font-bold uppercase tracking-widest text-r2v-charcoal/40">Karar Gerekçeleri</p>
                      {result.reason_codes.map((r, i) => (
                        <div key={i} className="flex gap-2">
                          <span className="text-r2v-charcoal/25 font-mono text-[10px] shrink-0 mt-0.5">0{i + 1}</span>
                          <p className="text-xs text-r2v-charcoal/70 leading-relaxed">{r.text}</p>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {/* Route Alternatives */}
                <div className="xl:col-span-4 bg-white border border-r2v-charcoal/10 p-5">
                  <h3 className="text-[10px] font-bold uppercase tracking-widest text-r2v-charcoal/50 mb-4">Tüm Rotalar</h3>
                  <div className="space-y-0">
                    {result.route_alternatives.map((r) => {
                      const isRec = r.route === result.recommended_route;
                      return (
                        <div key={r.route} className={`py-3 border-b border-r2v-charcoal/5 last:border-b-0 ${isRec ? 'opacity-100' : 'opacity-65'}`}>
                          <div className="flex items-start justify-between gap-2">
                            <div className="flex items-center gap-2 min-w-0">
                              <div className={`w-2 h-2 rounded-sm shrink-0 mt-1 ${isRec ? 'bg-r2v-green' : 'bg-r2v-charcoal/20'}`} />
                              <span className={`text-xs font-bold text-r2v-charcoal leading-tight ${!isRec && 'font-medium'}`}>{r.route}</span>
                            </div>
                            {isRec && <span className="text-[9px] font-bold text-r2v-green uppercase tracking-widest shrink-0">✓ Önerilen</span>}
                          </div>
                          <div className="flex gap-4 mt-1.5 ml-4 text-[10px] font-mono text-r2v-charcoal/60">
                            <span>{r.profit_try.toLocaleString('tr-TR', { maximumFractionDigits: 0 })} TL</span>
                            <span>+%{r.value_uplift_pct.toFixed(0)}</span>
                            <span>{r.co2_kg.toLocaleString('tr-TR', { maximumFractionDigits: 0 })} kg CO₂</span>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>

                {/* Buyer Matches */}
                <div className="xl:col-span-3 bg-white border border-r2v-charcoal/10 p-5">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-[10px] font-bold uppercase tracking-widest text-r2v-charcoal/50">Alıcı Eşleşmeleri</h3>
                    <span className="text-[9px] text-r2v-terracotta border border-r2v-terracotta/30 px-1.5 py-0.5">
                      {COU[request!.target_country]}
                    </span>
                  </div>
                  <div className="space-y-0">
                    {result.match_results.slice(0, 5).map((m, i) => (
                      <div key={i} className="py-3 border-b border-r2v-charcoal/5 last:border-b-0 flex items-center justify-between gap-2">
                        <div className="min-w-0">
                          <p className="text-xs font-bold text-r2v-charcoal truncate">{m.buyer}</p>
                          <p className="text-[9px] text-r2v-charcoal/40 font-mono truncate">{m.processor}</p>
                        </div>
                        <span className={`text-sm font-mono font-bold shrink-0 ${m.score >= 0.85 ? 'text-r2v-green' : 'text-r2v-charcoal/60'}`}>
                          %{(m.score * 100).toFixed(0)}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* ── WHAT-IF SECTION ── */}
            <div className="bg-white border border-r2v-charcoal/10">
              <div className="flex items-center justify-between p-5 border-b border-r2v-charcoal/8">
                <div>
                  <div className="flex items-center gap-2 mb-0.5">
                    <BarChart2 className="w-3.5 h-3.5 text-r2v-charcoal/40" />
                    <h3 className="text-xs font-bold uppercase tracking-widest text-r2v-charcoal">What-if Simülatör</h3>
                  </div>
                  <p className="text-[10px] text-r2v-charcoal/40">Kur, tonaj ve taşıma değişimi etkisi — baz: {result.recommended_route}</p>
                </div>
                <div className="flex items-center gap-1.5 text-[9px] font-bold uppercase tracking-widest text-r2v-charcoal/30">
                  <span>{wfResults.length} senaryo çalıştı</span>
                </div>
              </div>

              <div className="p-5">
                {/* Controls */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-5">
                  {/* FX slider */}
                  <div className="md:col-span-1">
                    <div className="flex justify-between items-end mb-1.5">
                      <label className="text-[9px] font-bold uppercase tracking-widest text-r2v-charcoal/40 flex items-center gap-1">
                        Kur Değişimi <Info className="w-3 h-3 opacity-50" />
                      </label>
                      <span className={`text-xs font-mono font-bold ${wfFxPct > 0 ? 'text-r2v-green' : wfFxPct < 0 ? 'text-r2v-terracotta' : 'text-r2v-charcoal/50'}`}>
                        {wfFxPct > 0 ? '+' : ''}{(wfFxPct * 100).toFixed(0)}%
                      </span>
                    </div>
                    <input
                      type="range" min={-20} max={20} step={1}
                      value={wfFxPct * 100}
                      onChange={(e) => setWfFxPct(Number(e.target.value) / 100)}
                      className="w-full h-0.5 bg-r2v-charcoal/15 appearance-none cursor-pointer accent-r2v-charcoal"
                    />
                    <div className="flex justify-between text-[8px] font-mono text-r2v-charcoal/25 mt-1"><span>-20%</span><span>+20%</span></div>
                  </div>

                  {/* Tonnage */}
                  <div>
                    <label className="text-[9px] font-bold uppercase tracking-widest text-r2v-charcoal/40 block mb-1.5">Tonaj Override</label>
                    <div className="flex items-center border-b border-r2v-charcoal/15 pb-1 focus-within:border-r2v-charcoal/40 transition-colors">
                      <input
                        type="number" value={wfTonnage}
                        onChange={(e) => setWfTonnage(e.target.value)}
                        placeholder={`Mevcut: ${request!.tonnage}`}
                        className="flex-1 bg-transparent border-none focus:ring-0 p-0 text-sm font-mono text-r2v-charcoal outline-none placeholder:text-r2v-charcoal/20"
                      />
                      <span className="text-[9px] text-r2v-charcoal/30 ml-1">TON</span>
                    </div>
                  </div>

                  {/* Transport */}
                  <div>
                    <label className="text-[9px] font-bold uppercase tracking-widest text-r2v-charcoal/40 block mb-1.5">Taşıma Modu</label>
                    <select
                      value={wfTransport}
                      onChange={(e) => setWfTransport(e.target.value as TransportMode | '')}
                      className="w-full bg-transparent border-b border-r2v-charcoal/15 pb-1 text-sm font-medium text-r2v-charcoal outline-none cursor-pointer"
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
                      <label className="text-[9px] font-bold uppercase tracking-widest text-r2v-charcoal/40 block mb-1.5">Senaryo Adı</label>
                      <input
                        type="text" value={wfName} maxLength={30}
                        onChange={(e) => setWfName(e.target.value)}
                        className="w-full bg-transparent border-b border-r2v-charcoal/15 pb-1 text-sm font-bold text-r2v-charcoal outline-none focus:border-r2v-charcoal/40 transition-colors"
                      />
                    </div>
                    <button
                      onClick={handleWhatIf}
                      disabled={isRunning}
                      className="mt-3 w-full bg-r2v-charcoal text-white h-8 flex items-center justify-center gap-1.5 hover:bg-r2v-charcoal/85 transition-colors disabled:opacity-60 text-[10px] font-bold uppercase tracking-widest"
                    >
                      {isRunning ? <><div className="w-3 h-3 border border-white border-t-transparent rounded-full animate-spin" /> Hesaplanıyor</> : 'Çalıştır ▶'}
                    </button>
                  </div>
                </div>

                {/* Presets */}
                <div className="flex flex-wrap gap-1.5 mb-5">
                  <span className="text-[9px] font-bold uppercase tracking-widest text-r2v-charcoal/30 self-center mr-1">Hazır:</span>
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
                      className="px-2.5 py-1 border border-r2v-charcoal/15 text-[9px] font-bold uppercase tracking-widest text-r2v-charcoal/50 hover:border-r2v-charcoal/40 hover:text-r2v-charcoal rounded-sm transition-colors"
                    >
                      {p.label}
                    </button>
                  ))}
                  {wfResults.length > 0 && (
                    <button onClick={() => setWfResults([])} className="ml-auto flex items-center gap-1 text-[9px] font-bold uppercase tracking-widest text-r2v-charcoal/30 hover:text-r2v-terracotta transition-colors">
                      <RefreshCcw className="w-3 h-3" /> Sıfırla
                    </button>
                  )}
                </div>

                {wfError && (
                  <div className="mb-4 p-3 bg-r2v-terracotta/10 border border-r2v-terracotta/20 text-xs text-r2v-terracotta">{wfError}</div>
                )}

                {/* Results */}
                {wfResults.length === 0 ? (
                  <div className="flex items-center justify-center py-10 text-center">
                    <p className="text-[10px] text-r2v-charcoal/30 font-mono">
                      Parametre seçin → Çalıştır butonuna basın → Sonuçlar burada görünür
                    </p>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
                    {/* Table */}
                    <div className="overflow-x-auto">
                      <table className="w-full text-left border-collapse">
                        <thead>
                          <tr className="text-[9px] font-bold uppercase tracking-widest text-r2v-charcoal/40 border-b border-r2v-charcoal/10">
                            <th className="pb-2 pr-3">Senaryo</th>
                            <th className="pb-2 px-3 text-right">Kâr (TL)</th>
                            <th className="pb-2 px-3 text-right">CO₂ (kg)</th>
                            <th className="pb-2 px-3">Rota</th>
                            <th className="pb-2 pl-3 text-center">∆</th>
                          </tr>
                        </thead>
                        <tbody>
                          {/* Base row */}
                          <tr className="border-b border-r2v-charcoal/5 bg-r2v-charcoal/3">
                            <td className="py-2.5 pr-3 text-[10px] font-bold text-r2v-charcoal/50">Baz Analiz</td>
                            <td className="py-2.5 px-3 text-right font-mono text-xs text-r2v-charcoal/60">{baseProfit.toLocaleString('tr-TR', { maximumFractionDigits: 0 })}</td>
                            <td className="py-2.5 px-3 text-right font-mono text-xs text-r2v-charcoal/60">{result.co2_kg.toLocaleString('tr-TR', { maximumFractionDigits: 0 })}</td>
                            <td className="py-2.5 px-3 text-[10px] text-r2v-charcoal/60">{result.recommended_route.split('(')[0].trim()}</td>
                            <td className="py-2.5 pl-3 text-center text-r2v-charcoal/30 text-[10px]">—</td>
                          </tr>
                          {wfResults.map((row, i) => (
                            <tr key={i} className="border-b border-r2v-charcoal/5 hover:bg-r2v-surface/50 transition-colors">
                              <td className="py-2.5 pr-3 text-[10px] font-bold text-r2v-charcoal">{row.scenario}</td>
                              <td className={`py-2.5 px-3 text-right font-mono text-xs font-bold ${row.expected_profit_try > baseProfit ? 'text-r2v-green' : 'text-r2v-terracotta'}`}>
                                {row.expected_profit_try.toLocaleString('tr-TR', { maximumFractionDigits: 0 })}
                              </td>
                              <td className={`py-2.5 px-3 text-right font-mono text-xs ${row.co2_kg < result.co2_kg ? 'text-r2v-green' : 'text-r2v-terracotta'}`}>
                                {row.co2_kg.toLocaleString('tr-TR', { maximumFractionDigits: 0 })}
                              </td>
                              <td className="py-2.5 px-3 text-[10px] text-r2v-charcoal/70">{row.recommended_route.split('(')[0].trim()}</td>
                              <td className="py-2.5 pl-3 text-center">
                                {row.expected_profit_try > baseProfit
                                  ? <TrendingUp className="w-3 h-3 text-r2v-green mx-auto" />
                                  : <TrendingDown className="w-3 h-3 text-r2v-terracotta mx-auto" />}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>

                    {/* Chart */}
                    {wfResults.length >= 2 && (
                      <div>
                        <p className="text-[9px] font-bold uppercase tracking-widest text-r2v-charcoal/40 mb-3">Kâr Karşılaştırması (bin TL)</p>
                        <div className="h-48">
                          <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={[{ name: 'Baz', kar: Math.round(baseProfit / 1000) }, ...chartData]}
                              margin={{ top: 0, right: 0, left: 0, bottom: 0 }}>
                              <XAxis dataKey="name" axisLine={false} tickLine={false}
                                tick={{ fontSize: 9, fontFamily: 'monospace', fill: '#2D323A', opacity: 0.6 }} />
                              <YAxis axisLine={false} tickLine={false}
                                tick={{ fontSize: 9, fontFamily: 'monospace', fill: '#2D323A', opacity: 0.5 }} width={28} />
                              <Tooltip cursor={{ fill: 'rgba(45,50,58,0.04)' }}
                                contentStyle={{ border: '1px solid #2D323A20', borderRadius: 0, fontSize: 10, fontFamily: 'monospace' }} />
                              <Bar dataKey="kar" fill="#2D323A" fillOpacity={0.6} barSize={22} radius={[2, 2, 0, 0]} />
                            </BarChart>
                          </ResponsiveContainer>
                        </div>
                        {/* Line chart: profit trend */}
                        {wfResults.length >= 3 && (
                          <div className="mt-4">
                            <p className="text-[9px] font-bold uppercase tracking-widest text-r2v-charcoal/40 mb-3">Senaryo Kâr Trendi</p>
                            <div className="h-32">
                              <ResponsiveContainer width="100%" height="100%">
                                <LineChart data={chartData} margin={{ top: 0, right: 0, left: 0, bottom: 0 }}>
                                  <XAxis dataKey="name" axisLine={false} tickLine={false}
                                    tick={{ fontSize: 9, fontFamily: 'monospace', fill: '#2D323A', opacity: 0.5 }} />
                                  <YAxis axisLine={false} tickLine={false}
                                    tick={{ fontSize: 9, fontFamily: 'monospace', fill: '#2D323A', opacity: 0.4 }} width={28} />
                                  <Tooltip cursor={{ stroke: '#2D323A30', strokeWidth: 1 }}
                                    contentStyle={{ border: '1px solid #2D323A20', borderRadius: 0, fontSize: 10, fontFamily: 'monospace' }} />
                                  <Line type="monotone" dataKey="kar" stroke="#6B8E78" strokeWidth={2} dot={{ r: 3, fill: '#6B8E78' }} />
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
