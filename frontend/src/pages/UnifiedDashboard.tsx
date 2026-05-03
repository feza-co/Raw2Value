import { useState } from 'react';
import {
  ChevronRight, RefreshCcw, TrendingUp, TrendingDown,
  CheckCircle2, ChevronDown, ChevronUp, Info, ArrowRight,
  Zap, BarChart2, AlertTriangle, MapPin, Building2, Anchor, Leaf, Users,
} from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { analyze, whatif } from '../lib/api';
import { buildMockAnalysis, buildMockWhatIfAll, buildMockWhatIfSingle } from '../lib/mockData';
import { useAnalysis } from '../contexts/AnalysisContext';
import type {
  RawMaterial, Quality, TransportMode, TargetCountry, Priority,
  AnalyzeRequest, WhatIfResultRow,
} from '../lib/types';

// ── Labels ────────────────────────────────────────────────────────────────────
const MAT: Record<RawMaterial, string> = {
  pomza: 'Pomza (Pumice)', perlit: 'Perlit', kabak_cekirdegi: 'Kabak Çekirdeği',
};
const QUA: Record<Quality, string> = {
  A: 'A Sınıfı (Yüksek)', B: 'B Sınıfı (Orta)', C: 'C Sınıfı (Düşük)', unknown: 'Bilinmiyor',
};
const TRA: Record<TransportMode, string> = {
  kara: 'Karayolu (TIR)', deniz: 'Denizyolu', demiryolu: 'Demiryolu', hava: 'Havayolu',
};
const COU: Record<TargetCountry, string> = { TR: 'Türkiye', DE: 'Almanya', NL: 'Hollanda' };
const PRI: Record<Priority, string> = {
  max_profit: 'Maksimum Kâr', low_carbon: 'Düşük Karbon', fast_delivery: 'Hızlı Teslimat',
};

const EMISSION_FACTORS: Record<TransportMode, number> = {
  kara: 0.100, deniz: 0.015, demiryolu: 0.030, hava: 0.500,
};
const DEST_CITY: Record<TargetCountry, string> = {
  DE: 'Hamburg', NL: 'Rotterdam', TR: 'İstanbul',
};

// Demo seed'deki işleyiciler (K3 yakın arama — Haversine + bbox)
const MOCK_PROCESSORS = [
  { name: 'Genper Madencilik A.Ş.', city: 'Acıgöl', dist_km: 12.5, recommended: true },
  { name: 'Akper A.Ş.', city: 'Acıgöl', dist_km: 28.3, recommended: false },
  { name: 'NevPom Madencilik Ltd.', city: 'Nevşehir', dist_km: 45.1, recommended: false },
];

// ── Helper UI ──────────────────────────────────────────────────────────────────
function SelectField<T extends string>({ label, value, options, onChange }: {
  label: string; value: T; options: Record<T, string>; onChange: (v: T) => void;
}) {
  return (
    <div>
      <label className="font-mono text-[11px] uppercase tracking-widest text-[#0a0a0a] block mb-1.5 font-medium">{label}</label>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value as T)}
        className="w-full bg-white border border-[#0a0a0a] px-3 py-2.5 text-sm font-medium text-[#0a0a0a] outline-none cursor-pointer appearance-none focus:ring-2 focus:ring-[#1d4fd6]/30 transition-all"
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
      <label className="font-mono text-[11px] uppercase tracking-widest text-[#0a0a0a] block mb-1.5 font-medium">{label}</label>
      <div className="flex items-center bg-white border border-[#0a0a0a] px-3 py-2.5 focus-within:ring-2 focus-within:ring-[#1d4fd6]/30 transition-all">
        <input
          type={type}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          className="flex-1 bg-transparent border-none focus:ring-0 p-0 text-sm font-medium text-[#0a0a0a] placeholder:text-[#6b6b6b] outline-none"
        />
        {suffix && <span className="font-mono text-xs font-medium text-[#6b6b6b] ml-1.5 uppercase tracking-wider">{suffix}</span>}
      </div>
    </div>
  );
}

// ── Main Component ─────────────────────────────────────────────────────────────
export default function UnifiedDashboard() {
  const { request, result, setAnalysis } = useAnalysis();

  // Form state — pre-filled with Mehmet Amca's demo scenario
  const [rawMaterial, setRawMaterial] = useState<RawMaterial>('pomza');
  const [tonnage, setTonnage]         = useState('150');
  const [quality, setQuality]         = useState<Quality>('A');
  const [originCity, setOriginCity]   = useState('Nevşehir');
  const [targetCountry, setTargetCountry] = useState<TargetCountry>('DE');
  const [transportMode, setTransportMode] = useState<TransportMode>('kara');
  const [priority, setPriority]       = useState<Priority>('max_profit');
  const [moisturePct, setMoisturePct] = useState('');
  const [purityPct, setPurityPct]     = useState('');
  const [particleSize, setParticleSize] = useState('');
  const [showAdvanced, setShowAdvanced] = useState(false);

  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analyzeError, setAnalyzeError] = useState<string | null>(null);

  // Result UI state
  const [showReasons, setShowReasons]     = useState(true);
  const [showProcessors, setShowProcessors] = useState(false);
  const [isMockMode, setIsMockMode]       = useState(false);

  // What-if state
  const [wfFxPct, setWfFxPct]           = useState(0);
  const [wfTonnage, setWfTonnage]       = useState('');
  const [wfName, setWfName]             = useState('Senaryo 1');
  const [wfResults, setWfResults]       = useState<WhatIfResultRow[]>([]);
  const [isRunning, setIsRunning]       = useState(false);
  const [isRunningAll, setIsRunningAll] = useState(false);
  const [wfError, setWfError]           = useState<string | null>(null);

  // ── Handlers ──────────────────────────────────────────────────────────────
  const handleAnalyze = async () => {
    const t = parseFloat(tonnage);
    if (!originCity.trim() || isNaN(t) || t <= 0) {
      setAnalyzeError('Menşei şehir ve geçerli bir tonaj giriniz.'); return;
    }
    setAnalyzeError(null);
    setIsAnalyzing(true);
    setWfResults([]);
    const payload: AnalyzeRequest = {
      raw_material: rawMaterial, tonnage: t, quality,
      origin_city: originCity.trim(),
      target_country: targetCountry,
      transport_mode: transportMode,
      priority,
      input_mode: moisturePct || purityPct || particleSize ? 'advanced' : 'basic',
      ...(moisturePct  ? { moisture_pct: parseFloat(moisturePct) }    : {}),
      ...(purityPct    ? { purity_pct: parseFloat(purityPct) }         : {}),
      ...(particleSize ? { particle_size_class: particleSize }          : {}),
    };
    try {
      const res = await analyze(payload);
      setAnalysis(payload, res);
      setIsMockMode(false);
      setShowReasons(true);
    } catch {
      // Backend ulaşılamıyor — demo mock verisi kullan
      await new Promise((r) => setTimeout(r, 900)); // gerçekçi gecikme
      setAnalysis(payload, buildMockAnalysis(t));
      setIsMockMode(true);
      setShowReasons(true);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleWhatIf = async () => {
    if (!request) return;
    setWfError(null);
    setIsRunning(true);
    const scenario = {
      name: wfName,
      fx_scenario_pct: wfFxPct,
      ...(wfTonnage ? { tonnage_override: parseFloat(wfTonnage) } : {}),
    };
    try {
      const res = await whatif({ base_payload: request, scenarios: [scenario] });
      setWfResults((prev) => [res.results[0], ...prev].slice(0, 8));
    } catch {
      await new Promise((r) => setTimeout(r, 400));
      const res = buildMockWhatIfSingle(scenario, request.tonnage);
      setWfResults((prev) => [res.results[0], ...prev].slice(0, 8));
    } finally {
      setWfName(`Senaryo ${wfResults.length + 2}`);
      setIsRunning(false);
    }
  };

  const handleKurKarsilastirma = async () => {
    if (!request) return;
    setWfError(null);
    setIsRunningAll(true);
    try {
      const res = await whatif({
        base_payload: request,
        scenarios: [
          { name: 'Kur -%20', fx_scenario_pct: -0.20 },
          { name: 'Kur sabit', fx_scenario_pct: 0.0 },
          { name: 'Kur +%20', fx_scenario_pct: 0.20 },
        ],
      });
      setWfResults(res.results);
    } catch {
      await new Promise((r) => setTimeout(r, 600));
      setWfResults(buildMockWhatIfAll(request.tonnage).results);
    } finally {
      setIsRunningAll(false);
    }
  };

  // ── Derived values ─────────────────────────────────────────────────────────
  const baseProfit    = result?.expected_profit_try ?? 0;
  const shapData      = result?.feature_importance.slice(0, 6) ?? [];
  const ef            = request ? (EMISSION_FACTORS[request.transport_mode] ?? 0.100) : 0.100;
  const distKm        = result && request ? Math.round(result.co2_kg / (request.tonnage * ef)) : 0;
  const destCity      = request ? DEST_CITY[request.target_country] : '';

  const processorName = result?.match_results?.[0]
    ? ((result.match_results[0] as any).processor_name ?? (result.match_results[0] as any).processor ?? null)
    : null;
  const buyerTop      = result?.match_results?.[0]
    ? ((result.match_results[0] as any).buyer_name ?? (result.match_results[0] as any).buyer ?? '—')
    : '—';

  // ── Render ─────────────────────────────────────────────────────────────────
  return (
    <div className="flex h-[calc(100vh-64px)] overflow-hidden bg-white">

      {/* ══════════ LEFT: FORM PANEL ══════════ */}
      <aside className="w-80 xl:w-[340px] shrink-0 flex flex-col border-r-2 border-[#0a0a0a] bg-white overflow-y-auto">
        <div className="p-6 border-b-2 border-[#0a0a0a]">
          <div className="flex items-center gap-3 mb-2">
            <span className="bg-[#d6342a] text-white text-xs font-semibold font-mono px-2.5 py-1 tracking-wider">01</span>
            <h2 className="text-base font-bold text-[#0a0a0a] tracking-tight">Analiz Girişi</h2>
            <Zap className="w-4 h-4 text-[#d6342a] ml-auto" />
          </div>
          <div className="flex items-center gap-2 mt-2 flex-wrap">
            <span className="font-mono text-[9px] font-bold text-white bg-[#1f7a3a] px-2 py-0.5 uppercase tracking-widest">Basic Mode</span>
            <span className="font-mono text-[9px] text-[#6b6b6b] uppercase tracking-widest">Doğa Pomza Ltd</span>
          </div>
        </div>

        <div className="flex-1 p-6 space-y-4">
          <SelectField label="Hammadde Tipi"   value={rawMaterial}    options={MAT} onChange={setRawMaterial} />
          <InputField  label="Menşei Şehir"    value={originCity}     onChange={setOriginCity}    placeholder="Nevşehir" />
          <InputField  label="Parti Tonajı"    value={tonnage}        onChange={setTonnage}        type="number" suffix="ton" placeholder="150" />
          <SelectField label="Kalite Sınıfı"   value={quality}        options={QUA} onChange={setQuality} />
          <SelectField label="Hedef Ülke"      value={targetCountry}  options={COU} onChange={setTargetCountry} />
          <SelectField label="Taşıma Modu"     value={transportMode}  options={TRA} onChange={setTransportMode} />
          <SelectField label="Öncelik"         value={priority}       options={PRI} onChange={setPriority} />

          <button
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="w-full text-left font-mono text-[11px] uppercase tracking-widest text-[#0a0a0a] hover:text-[#d6342a] flex items-center gap-1.5 transition-colors pt-3 border-t border-[#0a0a0a] font-medium"
          >
            {showAdvanced ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
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
          <div className="mx-6 mb-4 p-3.5 bg-white border-2 border-[#d6342a] text-sm text-[#d6342a] font-medium">
            {analyzeError}
          </div>
        )}

        <div className="p-6 border-t-2 border-[#0a0a0a]">
          <button
            onClick={handleAnalyze}
            disabled={isAnalyzing}
            className="w-full bg-[#0a0a0a] text-white h-12 flex items-center justify-center gap-2 hover:bg-[#d6342a] transition-colors disabled:opacity-60 font-mono text-xs uppercase tracking-widest font-medium"
          >
            {isAnalyzing ? (
              <><div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" /> AI Modeli Çalışıyor</>
            ) : (
              <><ChevronRight className="w-4 h-4" /> Analizi Başlat</>
            )}
          </button>
          <p className="font-mono text-[10px] text-center text-[#6b6b6b] mt-3 tracking-wide">
            Kâr reg. + Rota class. + Alıcı eşleşmesi
          </p>
        </div>
      </aside>

      {/* ══════════ RIGHT: RESULTS ══════════ */}
      <main className="flex-1 overflow-y-auto bg-white">

        {/* EMPTY STATE */}
        {!result ? (
          <div className="flex flex-col items-center justify-center h-full gap-8 px-12">
            <div className="w-full max-w-lg border-2 border-[#0a0a0a] p-6 bg-white">
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 bg-[#0a0a0a] text-white flex items-center justify-center font-mono text-lg font-bold shrink-0">MY</div>
                <div>
                  <p className="text-base font-bold text-[#0a0a0a]">Mehmet Yılmaz</p>
                  <p className="font-mono text-[10px] text-[#6b6b6b] tracking-widest uppercase mt-0.5">Doğa Pomza Ltd · Acıgöl/Nevşehir</p>
                  <div className="flex items-center gap-2 mt-3">
                    <MapPin className="w-3.5 h-3.5 text-[#d6342a]" />
                    <span className="text-sm text-[#2a2a2a] font-medium">150 ton A-kalite pomza hazır</span>
                    <span className="font-mono text-[9px] font-bold text-white bg-[#1f7a3a] px-1.5 py-0.5 uppercase tracking-widest ml-1">Stok Var</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="text-center max-w-md">
              <div className="w-16 h-16 border-2 border-[#0a0a0a] flex items-center justify-center bg-white mx-auto mb-4">
                <BarChart2 className="w-8 h-8 text-[#0a0a0a]" />
              </div>
              <p className="text-[#0a0a0a] text-2xl font-bold tracking-tightest mb-2">Analiz Bekleniyor</p>
              <p className="text-[#6b6b6b] text-sm leading-relaxed">
                Formdaki bilgiler Mehmet Amca senaryosuyla hazır.<br />
                <strong className="text-[#0a0a0a]">"Analizi Başlat"</strong>'a basın → 30 sn içinde rota kararı.
              </p>
            </div>

            <div className="flex gap-3 font-mono text-[10px] uppercase tracking-widest flex-wrap justify-center">
              {['Kâr Tahmini', 'Rota Önerisi', 'Karbon Hesabı', 'Alıcı Eşleşmesi'].map((t) => (
                <span key={t} className="px-3 py-1.5 border border-[#e6e6e6] text-[#6b6b6b]">{t}</span>
              ))}
            </div>
          </div>
        ) : (
          <div className="p-8 space-y-6 max-w-[1400px] mx-auto">

            {/* Mock mode banner */}
            {isMockMode && (
              <div className="flex items-center gap-3 p-3 border border-[#c97a17] bg-white text-sm text-[#c97a17]">
                <span className="font-mono text-[9px] font-bold bg-[#c97a17] text-white px-1.5 py-0.5 uppercase tracking-widest shrink-0">Demo</span>
                Backend'e ulaşılamadı — Mehmet Amca senaryosu için simüle edilmiş veriler gösteriliyor.
              </div>
            )}

            {/* Breadcrumb */}
            <div className="flex items-center gap-2 text-sm font-medium text-[#6b6b6b] pb-4 border-b-2 border-[#0a0a0a] flex-wrap">
              <span className="text-[#0a0a0a] font-bold">{MAT[request!.raw_material]}</span>
              <ArrowRight className="w-3.5 h-3.5" />
              <span>{request!.origin_city}</span>
              <ArrowRight className="w-3.5 h-3.5" />
              <span>{COU[request!.target_country]}</span>
              <span className="font-mono text-[10px] uppercase tracking-wider px-2 py-0.5 border border-[#0a0a0a] ml-1">
                {TRA[request!.transport_mode]}
              </span>
              <span className="font-mono text-[10px] uppercase tracking-wider px-2 py-0.5 border border-[#0a0a0a]">
                {request!.tonnage} ton
              </span>
              <span className="ml-auto font-mono text-xs text-[#6b6b6b] tracking-wide">
                {result.duration_ms}ms · {result.model_version ?? 'v1'}
              </span>
            </div>

            {/* Warnings */}
            {result.confidence.warnings.map((w: string, i: number) => (
              <div key={i} className="flex items-start gap-3 p-4 border-2 border-[#d6342a] text-sm text-[#0a0a0a]">
                <AlertTriangle className="w-4 h-4 text-[#d6342a] shrink-0 mt-0.5" />
                <span>{w}</span>
              </div>
            ))}

            {/* ── 3-COLUMN RESULTS GRID ── */}
            <div className="grid grid-cols-1 xl:grid-cols-12 gap-6">

              {/* Col 1: Hero recommendation */}
              <div className="xl:col-span-4 border-2 border-[#1f7a3a] p-6 bg-white">
                <div className="flex items-center gap-2 font-mono text-xs font-semibold text-[#1f7a3a] uppercase tracking-widest mb-4">
                  <CheckCircle2 className="w-4 h-4" /> Önerilen Rota — #1
                </div>
                <h2 className="text-xl font-bold text-[#0a0a0a] tracking-tightest leading-tight mb-5">
                  {result.recommended_route}
                </h2>
                <div className="space-y-3">
                  <div className="flex items-end justify-between border-b border-[#e6e6e6] pb-3">
                    <span className="font-mono text-[10px] uppercase tracking-widest text-[#6b6b6b] font-medium">Beklenen Kâr</span>
                    <span className="text-2xl font-bold text-[#1f7a3a] tabular-nums tracking-tightest">
                      {result.expected_profit_try.toLocaleString('tr-TR', { maximumFractionDigits: 0 })} TL
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="font-mono text-[10px] uppercase tracking-widest text-[#6b6b6b] font-medium">Değer Artışı</span>
                    <span className="text-lg font-bold text-[#1d4fd6] tabular-nums">
                      +%{result.value_uplift_pct.toFixed(1)}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="font-mono text-[10px] uppercase tracking-widest text-[#6b6b6b] font-medium">AI Güveni</span>
                    <span className="font-mono text-sm font-bold text-[#0a0a0a]">
                      %{Math.round(result.confidence.overall * 100)}
                      <span className={`ml-1.5 text-[10px] font-semibold uppercase tracking-wider ${result.confidence.overall >= 0.8 ? 'text-[#1f7a3a]' : 'text-[#6b6b6b]'}`}>
                        {result.confidence.overall >= 0.8 ? '● Yüksek' : '● Orta'}
                      </span>
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="font-mono text-[10px] uppercase tracking-widest text-[#6b6b6b] font-medium">EUR/TRY (TCMB)</span>
                    <span className="font-mono text-sm font-bold text-[#0a0a0a]">
                      {result.fx_used.eur_try.toFixed(2)}
                      <span className="font-normal text-[#6b6b6b] ml-1">· USD {result.fx_used.usd_try.toFixed(2)}</span>
                    </span>
                  </div>
                </div>
              </div>

              {/* Col 2: Route chain */}
              <div className="xl:col-span-4 border-2 border-[#0a0a0a] p-6 bg-white flex flex-col">
                <p className="font-mono text-xs font-semibold uppercase tracking-widest text-[#0a0a0a] mb-5 pb-3 border-b border-[#0a0a0a]">
                  Rota Zinciri
                </p>
                <div className="flex-1 flex flex-col justify-center gap-0">
                  {/* Menşei */}
                  <div className="flex items-center gap-3 p-3 bg-[#f4f4f4] border border-[#e6e6e6]">
                    <MapPin className="w-5 h-5 text-[#d6342a] shrink-0" />
                    <div>
                      <p className="text-sm font-bold text-[#0a0a0a]">{request!.origin_city}</p>
                      <p className="font-mono text-[9px] text-[#6b6b6b] uppercase tracking-widest">Menşei · Doğa Pomza Ltd</p>
                    </div>
                  </div>

                  <div className="ml-5 w-px h-5 bg-[#0a0a0a]" />

                  {/* İşleyici */}
                  {processorName ? (
                    <>
                      <div className="flex items-center gap-3 p-3 bg-[#f4f4f4] border border-[#e6e6e6]">
                        <Building2 className="w-5 h-5 text-[#1d4fd6] shrink-0" />
                        <div>
                          <p className="text-sm font-bold text-[#0a0a0a]">{processorName}</p>
                          <p className="font-mono text-[9px] text-[#6b6b6b] uppercase tracking-widest">İşleyici · Mikronize</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2 ml-5 my-0">
                        <div className="w-px h-5 bg-[#0a0a0a]" />
                        <span className="font-mono text-[9px] text-[#6b6b6b] tracking-wider ml-1">
                          {distKm.toLocaleString()} km · {TRA[request!.transport_mode]}
                        </span>
                      </div>
                    </>
                  ) : (
                    <div className="flex items-center gap-2 ml-5 my-0">
                      <div className="w-px h-5 bg-[#0a0a0a]" />
                      <span className="font-mono text-[9px] text-[#6b6b6b] tracking-wider ml-1">
                        {distKm.toLocaleString()} km · {TRA[request!.transport_mode]}
                      </span>
                    </div>
                  )}

                  {/* Hedef */}
                  <div className="flex items-center gap-3 p-3 bg-[#f4f4f4] border border-[#e6e6e6]">
                    <Anchor className="w-5 h-5 text-[#1f7a3a] shrink-0" />
                    <div>
                      <p className="text-sm font-bold text-[#0a0a0a]">{destCity}, {COU[request!.target_country]}</p>
                      <p className="font-mono text-[9px] text-[#6b6b6b] uppercase tracking-widest">Alıcı Limanı</p>
                    </div>
                  </div>
                </div>

                {/* CO₂ mini */}
                <div className="mt-4 pt-3 border-t border-[#0a0a0a] flex items-center gap-2">
                  <Leaf className="w-4 h-4 text-[#1f7a3a]" />
                  <span className="font-mono text-xs text-[#0a0a0a] font-semibold">
                    {result.co2_tonnes.toFixed(2)} ton CO₂
                  </span>
                  <span className="font-mono text-[9px] text-[#6b6b6b] ml-1">
                    · {ef.toFixed(3)} kg/ton-km
                  </span>
                </div>
              </div>

              {/* Col 3: Alternatives */}
              <div className="xl:col-span-4 border-2 border-[#0a0a0a] p-6 bg-white">
                <p className="font-mono text-xs font-semibold uppercase tracking-widest text-[#0a0a0a] mb-5 pb-3 border-b border-[#0a0a0a]">
                  Rota Alternatifleri
                </p>
                <div className="space-y-2">
                  {result.route_alternatives.slice(0, 4).map((r: any, i: number) => {
                    const isRec     = r.route === result.recommended_route;
                    const profit    = r.profit_try ?? r.predicted_profit_try ?? 0;
                    const probRaw   = r.route_probability ?? 0;
                    const prob      = (probRaw * 100).toFixed(0);
                    return (
                      <div key={r.route} className={`p-3 ${isRec ? 'border-2 border-[#1f7a3a]' : 'border border-[#e6e6e6]'}`}>
                        <div className="flex items-center justify-between gap-2 mb-1.5">
                          <div className="flex items-center gap-2 min-w-0">
                            <span className={`font-mono text-xs font-bold shrink-0 ${isRec ? 'text-[#1f7a3a]' : 'text-[#6b6b6b]'}`}>
                              #{i + 1}
                            </span>
                            <span className={`text-sm leading-snug truncate ${isRec ? 'font-bold text-[#0a0a0a]' : 'font-medium text-[#2a2a2a]'}`}>
                              {r.route}
                            </span>
                          </div>
                          {isRec && (
                            <span className="font-mono text-[9px] font-bold text-white bg-[#1f7a3a] px-1.5 py-0.5 uppercase tracking-widest shrink-0">
                              ✓
                            </span>
                          )}
                        </div>
                        <div className="flex gap-3 ml-6 font-mono text-xs tracking-wide">
                          <span className={`font-bold ${isRec ? 'text-[#1f7a3a]' : 'text-[#0a0a0a]'}`}>
                            {profit.toLocaleString('tr-TR', { maximumFractionDigits: 0 })} TL
                          </span>
                          <span className="text-[#6b6b6b]">%{prob} olas.</span>
                        </div>
                      </div>
                    );
                  })}
                </div>
                {result.match_results.length > 0 && (
                  <div className="mt-4 pt-3 border-t border-[#0a0a0a] flex items-center gap-2">
                    <Users className="w-3.5 h-3.5 text-[#0a0a0a]" />
                    <span className="font-mono text-[10px] text-[#0a0a0a] font-medium">
                      {result.match_results.length} alıcı eşleşti · Top: {buyerTop}
                    </span>
                  </div>
                )}
              </div>
            </div>

            {/* ── "BU KARARI NASIL VERDİ?" ── */}
            <div className="border-2 border-[#0a0a0a] bg-white">
              <button
                onClick={() => setShowReasons(!showReasons)}
                className="w-full flex items-center justify-between p-6 hover:bg-[#f4f4f4] transition-colors"
              >
                <div className="flex items-center gap-3">
                  <span className="bg-[#1d4fd6] text-white text-xs font-semibold font-mono px-2.5 py-1 tracking-wider">02</span>
                  <span className="text-base font-bold text-[#0a0a0a] tracking-tight">
                    Bu kararı sistem nasıl verdi?
                  </span>
                </div>
                {showReasons ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
              </button>

              {showReasons && (
                <div className="px-6 pb-6 border-t border-[#0a0a0a] grid grid-cols-1 xl:grid-cols-2 gap-6 pt-6">
                  {/* Reason codes */}
                  <div>
                    <p className="font-mono text-xs font-semibold uppercase tracking-widest text-[#0a0a0a] mb-4">Karar Gerekçeleri</p>
                    <div className="space-y-3">
                      {result.reason_codes.map((r: any, i: number) => (
                        <div key={i} className="flex gap-3 p-4 border border-[#e6e6e6]">
                          <div className="shrink-0">
                            <span className="font-mono text-[10px] font-bold text-white bg-[#0a0a0a] px-1.5 py-0.5">
                              {((r.importance ?? 0) * 100).toFixed(0)}%
                            </span>
                          </div>
                          <div>
                            <p className="font-mono text-[9px] font-semibold text-[#1d4fd6] uppercase tracking-widest mb-1">
                              {r.feature}
                            </p>
                            <p className="text-sm text-[#2a2a2a] leading-relaxed">{r.text}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Feature importance chart */}
                  <div>
                    <p className="font-mono text-xs font-semibold uppercase tracking-widest text-[#0a0a0a] mb-4">
                      Feature Importance (Top 6)
                    </p>
                    <div className="h-52">
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={shapData} layout="vertical" margin={{ top: 0, right: 8, left: 0, bottom: 0 }}>
                          <XAxis type="number" hide />
                          <YAxis dataKey="feature" type="category" axisLine={false} tickLine={false}
                            tick={{ fontSize: 11, fill: '#0a0a0a', fontFamily: 'JetBrains Mono' }} width={160} />
                          <Tooltip cursor={{ fill: 'rgba(10,10,10,0.04)' }}
                            contentStyle={{ border: '2px solid #0a0a0a', borderRadius: 0, fontSize: 12 }} />
                          <Bar dataKey="importance" fill="#1d4fd6" barSize={14} />
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* ── CARBON + NEARBY PROCESSORS ── */}
            <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">

              {/* Carbon card — K1 */}
              <div className="border-2 border-[#0a0a0a] p-6 bg-white">
                <div className="flex items-center gap-3 mb-5">
                  <Leaf className="w-5 h-5 text-[#1f7a3a]" />
                  <span className="font-mono text-xs font-semibold uppercase tracking-widest text-[#0a0a0a]">
                    CO₂ Ayak İzi
                  </span>
                  <span className="font-mono text-[9px] font-bold text-white bg-[#1f7a3a] px-1.5 py-0.5 uppercase tracking-widest ml-auto">K1</span>
                </div>

                {/* Formula display */}
                <div className="bg-[#f4f4f4] p-4 font-mono text-sm border border-[#e6e6e6] mb-4 leading-relaxed">
                  <span className="text-[#0a0a0a] font-bold">{request!.tonnage}</span>
                  <span className="text-[#6b6b6b]"> ton × </span>
                  <span className="text-[#0a0a0a] font-bold">{distKm.toLocaleString()}</span>
                  <span className="text-[#6b6b6b]"> km × </span>
                  <span className="text-[#1d4fd6] font-bold">{ef.toFixed(3)}</span>
                  <span className="text-[#6b6b6b]"> kg/ton-km = </span>
                  <span className="text-[#1f7a3a] font-bold">
                    {result.co2_kg.toLocaleString('tr-TR', { maximumFractionDigits: 0 })} kg CO₂
                  </span>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div className="p-3 border border-[#e6e6e6]">
                    <p className="font-mono text-[9px] uppercase tracking-widest text-[#6b6b6b] mb-1">Toplam CO₂</p>
                    <p className="text-xl font-bold text-[#1f7a3a] tabular-nums">{result.co2_tonnes.toFixed(2)} ton</p>
                  </div>
                  <div className="p-3 border border-[#e6e6e6]">
                    <p className="font-mono text-[9px] uppercase tracking-widest text-[#6b6b6b] mb-1">Emisyon Faktörü</p>
                    <p className="text-sm font-bold text-[#0a0a0a]">{ef.toFixed(3)} kg/ton-km</p>
                    <p className="font-mono text-[9px] text-[#6b6b6b] mt-0.5 uppercase">{TRA[request!.transport_mode]}</p>
                  </div>
                </div>
                <p className="font-mono text-[9px] text-[#6b6b6b] mt-3 tracking-wide">
                  * Hackathon resmi emisyon faktörleri · Mesafe: ORS veya Haversine fallback
                </p>
              </div>

              {/* Nearby processors — K3 */}
              <div className="border-2 border-[#0a0a0a] p-6 bg-white">
                <div className="flex items-center gap-3 mb-5">
                  <Building2 className="w-5 h-5 text-[#1d4fd6]" />
                  <span className="font-mono text-xs font-semibold uppercase tracking-widest text-[#0a0a0a]">
                    Yakın İşleyiciler
                  </span>
                  <span className="font-mono text-[9px] font-bold text-white bg-[#1d4fd6] px-1.5 py-0.5 uppercase tracking-widest ml-auto">K3</span>
                </div>

                <button
                  onClick={() => setShowProcessors(!showProcessors)}
                  className="w-full flex items-center justify-center gap-2 border-2 border-[#0a0a0a] py-3 font-mono text-xs font-medium uppercase tracking-widest text-[#0a0a0a] hover:bg-[#0a0a0a] hover:text-white transition-colors mb-4"
                >
                  <MapPin className="w-4 h-4" />
                  {showProcessors ? 'Listeyi Gizle' : '100 km İçindeki İşleyicileri Göster'}
                </button>

                {showProcessors ? (
                  <div className="space-y-2">
                    {MOCK_PROCESSORS.map((p, i) => (
                      <div key={i} className={`flex items-center justify-between p-3 ${p.recommended ? 'border-2 border-[#1f7a3a]' : 'border border-[#e6e6e6]'}`}>
                        <div className="flex items-center gap-3">
                          <span className={`font-mono text-xs font-bold w-5 shrink-0 ${p.recommended ? 'text-[#1f7a3a]' : 'text-[#6b6b6b]'}`}>
                            #{i + 1}
                          </span>
                          <div>
                            <p className={`text-sm font-bold ${p.recommended ? 'text-[#0a0a0a]' : 'text-[#2a2a2a]'}`}>{p.name}</p>
                            <p className="font-mono text-[9px] text-[#6b6b6b] uppercase tracking-widest">
                              {p.city} · {p.dist_km} km
                            </p>
                          </div>
                        </div>
                        {p.recommended && (
                          <span className="font-mono text-[9px] font-bold text-white bg-[#1f7a3a] px-1.5 py-0.5 uppercase tracking-widest shrink-0">
                            ✓ Önerilen
                          </span>
                        )}
                      </div>
                    ))}
                    <p className="font-mono text-[9px] text-[#6b6b6b] mt-2 tracking-wide">
                      * Haversine + bbox coğrafi arama · {request!.origin_city} merkez · 100 km yarıçap
                    </p>
                  </div>
                ) : (
                  <div className="space-y-2">
                    <div className="flex items-start gap-2 text-sm text-[#6b6b6b]">
                      <Info className="w-4 h-4 shrink-0 mt-0.5" />
                      <span>100 km çevresindeki akredite işleyicileri listeler. Kapasite/fiyat değişirse alternatife geçilebilir.</span>
                    </div>
                    <div className="flex items-start gap-2 text-sm text-[#6b6b6b]">
                      <Info className="w-4 h-4 shrink-0 mt-0.5" />
                      <span>Ana öneri: Genper Madencilik A.Ş. — 12.5 km · Acıgöl.</span>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* ── WHAT-IF SECTION — K2 ── */}
            <div className="border-2 border-[#0a0a0a] bg-white">
              <div className="flex items-center justify-between gap-4 p-6 border-b-2 border-[#0a0a0a] flex-wrap">
                <div>
                  <div className="flex items-center gap-3 mb-1">
                    <span className="bg-[#c97a17] text-white text-xs font-semibold font-mono px-2.5 py-1 tracking-wider">03</span>
                    <h3 className="text-base font-bold text-[#0a0a0a] tracking-tight">What-if Simülatör</h3>
                    <span className="font-mono text-[9px] font-bold text-white bg-[#c97a17] px-1.5 py-0.5 uppercase tracking-widest">K2</span>
                  </div>
                  <p className="text-sm text-[#6b6b6b]">
                    Kur değişince karar değişir mi? — Baz: <span className="font-semibold text-[#0a0a0a]">{result.recommended_route.split('(')[0].trim()}</span>
                  </p>
                </div>
                <button
                  onClick={handleKurKarsilastirma}
                  disabled={isRunningAll}
                  className="flex items-center gap-2 bg-[#c97a17] text-white px-5 py-3 font-mono text-xs font-medium uppercase tracking-widest hover:bg-[#0a0a0a] transition-colors disabled:opacity-60 whitespace-nowrap"
                >
                  {isRunningAll ? (
                    <><div className="w-3.5 h-3.5 border border-white border-t-transparent rounded-full animate-spin" /> Hesaplanıyor</>
                  ) : (
                    <>Kur Karşılaştırması ▶ (–20% / sabit / +20%)</>
                  )}
                </button>
              </div>

              <div className="p-6">
                {/* Custom scenario controls */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-5 mb-6 pb-6 border-b border-[#e6e6e6]">
                  <div>
                    <div className="flex justify-between items-end mb-2">
                      <label className="font-mono text-[11px] font-medium uppercase tracking-widest text-[#0a0a0a] flex items-center gap-1">
                        Kur Değişimi <Info className="w-3.5 h-3.5 opacity-50" />
                      </label>
                      <span className={`font-mono text-sm font-bold ${wfFxPct > 0 ? 'text-[#1f7a3a]' : wfFxPct < 0 ? 'text-[#d6342a]' : 'text-[#6b6b6b]'}`}>
                        {wfFxPct > 0 ? '+' : ''}{(wfFxPct * 100).toFixed(0)}%
                      </span>
                    </div>
                    <input
                      type="range" min={-20} max={20} step={1}
                      value={wfFxPct * 100}
                      onChange={(e) => setWfFxPct(Number(e.target.value) / 100)}
                      className="w-full h-1.5 bg-[#e6e6e6] appearance-none cursor-pointer accent-[#c97a17]"
                    />
                    <div className="flex justify-between font-mono text-[9px] text-[#6b6b6b] mt-1.5">
                      <span>-20%</span><span>+20%</span>
                    </div>
                  </div>

                  <div>
                    <label className="font-mono text-[11px] font-medium uppercase tracking-widest text-[#0a0a0a] block mb-2">Tonaj Override</label>
                    <div className="flex items-center bg-white border border-[#0a0a0a] px-3 py-2">
                      <input
                        type="number" value={wfTonnage}
                        onChange={(e) => setWfTonnage(e.target.value)}
                        placeholder={`Mevcut: ${request!.tonnage}`}
                        className="flex-1 bg-transparent border-none focus:ring-0 p-0 text-sm font-medium text-[#0a0a0a] outline-none placeholder:text-[#6b6b6b]"
                      />
                      <span className="font-mono text-xs font-medium text-[#6b6b6b] ml-1 uppercase tracking-wider">ton</span>
                    </div>
                  </div>

                  <div>
                    <label className="font-mono text-[11px] font-medium uppercase tracking-widest text-[#0a0a0a] block mb-2">Senaryo Adı</label>
                    <input
                      type="text" value={wfName} maxLength={30}
                      onChange={(e) => setWfName(e.target.value)}
                      className="w-full bg-white border border-[#0a0a0a] px-3 py-2 text-sm font-semibold text-[#0a0a0a] outline-none"
                    />
                  </div>

                  <div className="flex flex-col justify-end">
                    <button
                      onClick={handleWhatIf}
                      disabled={isRunning}
                      className="w-full bg-[#0a0a0a] text-white h-10 flex items-center justify-center gap-1.5 hover:bg-[#1d4fd6] transition-colors disabled:opacity-60 font-mono text-xs uppercase tracking-widest font-medium"
                    >
                      {isRunning ? (
                        <><div className="w-3.5 h-3.5 border border-white border-t-transparent rounded-full animate-spin" /> Hesaplanıyor</>
                      ) : 'Çalıştır ▶'}
                    </button>
                  </div>
                </div>

                {wfError && (
                  <div className="mb-5 p-3.5 border-2 border-[#d6342a] text-sm text-[#d6342a] font-medium">{wfError}</div>
                )}

                {wfResults.length === 0 ? (
                  <div className="flex flex-col items-center justify-center py-10 text-center border-2 border-dashed border-[#0a0a0a] gap-3">
                    <p className="text-sm text-[#6b6b6b] font-medium max-w-md">
                      <strong className="text-[#0a0a0a]">Kur Karşılaştırması</strong> butonuna basın —
                      sistem –20% / sabit / +20% senaryolarını paralel çalıştırır ve rotanın değişip değişmediğini gösterir.
                    </p>
                  </div>
                ) : (
                  <>
                    <div className="overflow-x-auto border-2 border-[#0a0a0a]">
                      <table className="w-full text-left border-collapse">
                        <thead className="bg-[#0a0a0a] text-white">
                          <tr className="font-mono text-xs font-medium uppercase tracking-widest">
                            <th className="py-3 px-4">Senaryo</th>
                            <th className="py-3 px-4 text-right">Kâr (TL)</th>
                            <th className="py-3 px-4 text-right">∆ Baz</th>
                            <th className="py-3 px-4">Önerilen Rota</th>
                            <th className="py-3 px-4 text-center">Rota Değişti?</th>
                          </tr>
                        </thead>
                        <tbody className="bg-white">
                          {/* Base row */}
                          <tr className="border-t border-[#e6e6e6] bg-[#f4f4f4]">
                            <td className="py-3 px-4 text-sm font-semibold text-[#6b6b6b]">Baz (mevcut)</td>
                            <td className="py-3 px-4 text-right font-mono text-sm text-[#6b6b6b]">
                              {baseProfit.toLocaleString('tr-TR', { maximumFractionDigits: 0 })}
                            </td>
                            <td className="py-3 px-4 text-right font-mono text-xs text-[#6b6b6b]">—</td>
                            <td className="py-3 px-4 text-xs text-[#6b6b6b]">{result.recommended_route.split('(')[0].trim()}</td>
                            <td className="py-3 px-4 text-center text-[#6b6b6b] text-xs">—</td>
                          </tr>
                          {wfResults.map((row: WhatIfResultRow, i: number) => {
                            const delta       = row.expected_profit_try - baseProfit;
                            const deltaPct    = (delta / (baseProfit || 1) * 100).toFixed(1);
                            const routeChg    = row.recommended_route !== result.recommended_route;
                            return (
                              <tr key={i} className="border-t border-[#e6e6e6] hover:bg-[#f4f4f4] transition-colors">
                                <td className="py-3 px-4 text-sm font-bold text-[#0a0a0a]">{row.scenario}</td>
                                <td className={`py-3 px-4 text-right font-mono text-sm font-bold ${row.expected_profit_try >= baseProfit ? 'text-[#1f7a3a]' : 'text-[#d6342a]'}`}>
                                  {row.expected_profit_try.toLocaleString('tr-TR', { maximumFractionDigits: 0 })}
                                </td>
                                <td className={`py-3 px-4 text-right font-mono text-xs ${delta >= 0 ? 'text-[#1f7a3a]' : 'text-[#d6342a]'}`}>
                                  {delta >= 0 ? '+' : ''}{deltaPct}%
                                </td>
                                <td className={`py-3 px-4 text-xs ${routeChg ? 'text-[#d6342a] font-bold' : 'text-[#2a2a2a]'}`}>
                                  {row.recommended_route.split('(')[0].trim()}
                                </td>
                                <td className="py-3 px-4 text-center">
                                  {routeChg
                                    ? <span className="font-mono text-[9px] font-bold text-white bg-[#d6342a] px-1.5 py-0.5">EVET !</span>
                                    : <span className="font-mono text-[9px] font-bold text-white bg-[#1f7a3a] px-1.5 py-0.5">AYNI</span>}
                                </td>
                              </tr>
                            );
                          })}
                        </tbody>
                      </table>
                    </div>

                    <div className="flex items-center justify-between mt-3">
                      <p className="font-mono text-[9px] text-[#6b6b6b] tracking-wide">
                        * K2: Kur özelliği model feature vector'ünün parçası — kur değişimi öneri rotayı değiştirebilir.
                      </p>
                      <button
                        onClick={() => { setWfResults([]); setWfName('Senaryo 1'); }}
                        className="inline-flex items-center gap-1.5 font-mono text-xs font-medium uppercase tracking-widest text-[#6b6b6b] hover:text-[#d6342a] transition-colors"
                      >
                        <RefreshCcw className="w-3.5 h-3.5" /> Sıfırla
                      </button>
                    </div>

                    {/* Trend indicator */}
                    <div className="mt-4 grid grid-cols-3 gap-3">
                      {wfResults.map((row: WhatIfResultRow, i: number) => {
                        const delta = row.expected_profit_try - baseProfit;
                        const Icon  = delta >= 0 ? TrendingUp : TrendingDown;
                        const color = delta >= 0 ? 'text-[#1f7a3a] border-[#1f7a3a]' : 'text-[#d6342a] border-[#d6342a]';
                        return (
                          <div key={i} className={`p-3 border ${color} flex items-center gap-3`}>
                            <Icon className={`w-5 h-5 shrink-0 ${delta >= 0 ? 'text-[#1f7a3a]' : 'text-[#d6342a]'}`} />
                            <div>
                              <p className="font-mono text-[9px] uppercase tracking-widest text-[#6b6b6b]">{row.scenario}</p>
                              <p className={`text-sm font-bold tabular-nums ${delta >= 0 ? 'text-[#1f7a3a]' : 'text-[#d6342a]'}`}>
                                {row.expected_profit_try.toLocaleString('tr-TR', { maximumFractionDigits: 0 })} TL
                              </p>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </>
                )}
              </div>
            </div>

          </div>
        )}
      </main>
    </div>
  );
}
