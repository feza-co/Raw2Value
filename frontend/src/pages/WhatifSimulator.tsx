import { useState } from 'react';
import { RefreshCcw, TrendingDown, TrendingUp, ArrowRight, Info } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { Link } from 'react-router-dom';
import { whatif, ApiError } from '../lib/api';
import { useAnalysis } from '../contexts/AnalysisContext';
import type { WhatIfResultRow, TransportMode } from '../lib/types';

const TRANSPORT_LABELS: Record<TransportMode, string> = {
  kara: 'Karayolu',
  deniz: 'Denizyolu',
  demiryolu: 'Demiryolu',
  hava: 'Havayolu',
};

interface ScenarioConfig {
  name: string;
  fx_scenario_pct: number;
  tonnage_override: number | null;
  transport_mode_override: TransportMode | null;
}

const PRESETS: ScenarioConfig[] = [
  { name: 'Baz Senaryo', fx_scenario_pct: 0, tonnage_override: null, transport_mode_override: null },
  { name: 'Kur +%10', fx_scenario_pct: 0.10, tonnage_override: null, transport_mode_override: null },
  { name: 'Kur -%10', fx_scenario_pct: -0.10, tonnage_override: null, transport_mode_override: null },
  { name: 'Tonaj x2', fx_scenario_pct: 0, tonnage_override: null, transport_mode_override: null },
  { name: 'Havayolu', fx_scenario_pct: 0, tonnage_override: null, transport_mode_override: 'hava' },
];

export default function WhatifSimulator() {
  const { request, result } = useAnalysis();

  const [fxPct, setFxPct] = useState(0);
  const [tonnageOverride, setTonnageOverride] = useState('');
  const [transportOverride, setTransportOverride] = useState<TransportMode | ''>('');
  const [scenarioName, setScenarioName] = useState('Senaryo 1');

  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<WhatIfResultRow[]>([]);

  if (!request || !result) {
    return (
      <div className="max-w-7xl mx-auto pt-24 flex flex-col items-center gap-6">
        <p className="text-r2v-charcoal/60 text-base">Önce bir analiz yapmanız gerekiyor.</p>
        <Link
          to="/dashboard/material"
          className="flex items-center gap-2 px-6 py-3 bg-r2v-charcoal text-white text-xs font-bold uppercase tracking-widest hover:bg-r2v-charcoal/90 transition-colors"
        >
          Material Analyzer'a Git <ArrowRight className="w-4 h-4" />
        </Link>
      </div>
    );
  }

  const applyPreset = (p: ScenarioConfig) => {
    setScenarioName(p.name);
    setFxPct(p.fx_scenario_pct);
    setTonnageOverride(p.tonnage_override !== null ? String(p.tonnage_override) : '');
    setTransportOverride(p.transport_mode_override ?? '');
  };

  const handleRun = async () => {
    setError(null);
    setIsRunning(true);
    try {
      const scenario = {
        name: scenarioName,
        fx_scenario_pct: fxPct,
        ...(tonnageOverride ? { tonnage_override: parseFloat(tonnageOverride) } : {}),
        ...(transportOverride ? { transport_mode_override: transportOverride as TransportMode } : {}),
      };
      const res = await whatif({ base_payload: request, scenarios: [scenario] });
      setResults((prev) => [res.results[0], ...prev].slice(0, 10));
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        setError('Oturum açmanız gerekiyor.');
      } else {
        setError(err instanceof Error ? err.message : 'What-if hesaplanırken hata oluştu.');
      }
    } finally {
      setIsRunning(false);
    }
  };

  const baseProfit = result.expected_profit_try;
  const baseCO2 = result.co2_kg;
  const baseRoute = result.recommended_route;

  const chartData = results.map((r) => ({
    name: r.scenario,
    kar: Math.round(r.expected_profit_try),
  }));

  return (
    <div className="max-w-[1400px] mx-auto space-y-12 pb-12">
      {/* Header */}
      <div className="border-b-2 border-r2v-charcoal/10 pb-6">
        <h1 className="text-3xl font-bold tracking-tight text-r2v-charcoal mb-2">What-if Simulator</h1>
        <p className="text-sm text-r2v-charcoal/60 font-normal">
          Döviz kuru, tonaj veya taşıma modu değişimlerinin kâr ve CO₂ üzerindeki etkisini simüle edin.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-16">
        {/* LEFT: Controls */}
        <div className="lg:col-span-4">
          <div className="flex justify-between items-end mb-8 border-b border-r2v-charcoal/20 pb-2">
            <h3 className="text-lg font-bold text-r2v-charcoal tracking-tight">Senaryo Parametreleri</h3>
            <button
              onClick={() => { setFxPct(0); setTonnageOverride(''); setTransportOverride(''); setScenarioName('Senaryo 1'); }}
              className="text-[10px] font-bold uppercase tracking-widest text-r2v-charcoal/50 hover:text-r2v-terracotta flex items-center gap-1 transition-colors border border-r2v-charcoal/10 px-2 py-1 rounded"
            >
              <RefreshCcw className="w-3 h-3" /> Sıfırla
            </button>
          </div>

          {/* Scenario Name */}
          <div className="mb-6">
            <label className="text-[10px] font-bold text-r2v-charcoal/60 uppercase tracking-widest block mb-2">Senaryo Adı</label>
            <div className="border-b border-r2v-charcoal/20 pb-2">
              <input
                type="text"
                value={scenarioName}
                onChange={(e) => setScenarioName(e.target.value)}
                maxLength={50}
                className="w-full bg-transparent border-none focus:ring-0 p-0 text-sm font-bold text-r2v-charcoal outline-none"
              />
            </div>
          </div>

          {/* FX Scenario */}
          <div className="mb-6">
            <div className="flex justify-between items-end mb-2">
              <label className="text-[10px] font-bold text-r2v-charcoal/60 uppercase tracking-widest flex items-center gap-1">
                Kur Değişimi (FX) <Info className="w-3 h-3 opacity-50" />
              </label>
              <div className="flex items-center gap-1 border-b border-r2v-charcoal/20 pb-0.5">
                <input
                  type="number"
                  value={(fxPct * 100).toFixed(0)}
                  onChange={(e) => setFxPct(Math.max(-20, Math.min(20, Number(e.target.value))) / 100)}
                  className="w-14 text-right bg-transparent border-none focus:ring-0 p-0 text-sm font-mono font-bold text-r2v-charcoal"
                />
                <span className="text-[10px] text-r2v-charcoal/40 font-mono">%</span>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-[9px] font-mono text-r2v-charcoal/30">-20</span>
              <input
                type="range" min={-20} max={20} step={1}
                value={fxPct * 100}
                onChange={(e) => setFxPct(Number(e.target.value) / 100)}
                className="flex-1 h-0.5 bg-r2v-charcoal/10 appearance-none cursor-pointer accent-r2v-charcoal"
              />
              <span className="text-[9px] font-mono text-r2v-charcoal/30">+20</span>
            </div>
            <p className="text-[9px] text-r2v-charcoal/40 mt-1 font-mono">
              Baz kur: EUR {result.fx_used.eur_try.toFixed(2)} → {(result.fx_used.eur_try * (1 + fxPct)).toFixed(2)}
            </p>
          </div>

          {/* Tonnage Override */}
          <div className="mb-6">
            <label className="text-[10px] font-bold text-r2v-charcoal/60 uppercase tracking-widest block mb-2">
              Tonaj Değişimi (opsiyonel)
            </label>
            <div className="flex items-center border-b border-r2v-charcoal/20 pb-2">
              <input
                type="number"
                value={tonnageOverride}
                onChange={(e) => setTonnageOverride(e.target.value)}
                placeholder={`Mevcut: ${request.tonnage}`}
                className="w-full bg-transparent border-none focus:ring-0 p-0 text-sm font-mono font-bold text-r2v-charcoal outline-none placeholder:text-r2v-charcoal/20"
              />
              <span className="text-[10px] text-r2v-charcoal/40 font-mono ml-2">TON</span>
            </div>
          </div>

          {/* Transport Override */}
          <div className="mb-8">
            <label className="text-[10px] font-bold text-r2v-charcoal/60 uppercase tracking-widest block mb-2">
              Taşıma Modu Değişimi (opsiyonel)
            </label>
            <select
              value={transportOverride}
              onChange={(e) => setTransportOverride(e.target.value as TransportMode | '')}
              className="w-full bg-transparent border-b border-r2v-charcoal/20 pb-2 text-sm font-bold text-r2v-charcoal focus:ring-0 outline-none cursor-pointer"
            >
              <option value="">— Mevcut tut ({TRANSPORT_LABELS[request.transport_mode]}) —</option>
              {(Object.entries(TRANSPORT_LABELS) as [TransportMode, string][]).map(([k, v]) => (
                <option key={k} value={k}>{v}</option>
              ))}
            </select>
          </div>

          {/* Presets */}
          <div className="pt-6 border-t border-r2v-charcoal/10">
            <p className="text-[10px] font-bold text-r2v-charcoal/60 uppercase tracking-widest mb-4">Hazır Senaryolar</p>
            <div className="flex flex-wrap gap-2">
              {PRESETS.map((p) => (
                <button
                  key={p.name}
                  onClick={() => applyPreset(p)}
                  className="px-3 py-1.5 border border-r2v-charcoal/20 text-r2v-charcoal/60 text-[10px] font-bold uppercase tracking-widest rounded-sm hover:border-r2v-charcoal hover:text-r2v-charcoal transition-colors"
                >
                  {p.name}
                </button>
              ))}
            </div>
          </div>

          {error && (
            <div className="mt-6 p-4 bg-r2v-terracotta/10 border border-r2v-terracotta/30 text-sm text-r2v-terracotta font-medium">
              {error}
            </div>
          )}

          <button
            onClick={handleRun}
            disabled={isRunning}
            className="w-full mt-8 bg-r2v-charcoal text-white h-12 flex items-center justify-center gap-2 hover:bg-r2v-charcoal/90 transition-colors disabled:opacity-70 text-xs font-bold uppercase tracking-widest"
          >
            {isRunning ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                Hesaplanıyor...
              </>
            ) : 'Senaryoyu Çalıştır'}
          </button>
        </div>

        {/* RIGHT: Results */}
        <div className="lg:col-span-8 flex flex-col gap-12">

          {/* Before vs After (if results exist) */}
          {results.length > 0 && (
            <div>
              <h3 className="text-xl font-bold text-r2v-charcoal tracking-tight mb-6">Son Senaryo — Baz Karşılaştırması</h3>
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="border-b-2 border-r2v-charcoal/20">
                    <th className="py-2 w-1/4"></th>
                    <th className="py-2 text-[10px] font-bold uppercase tracking-widest text-r2v-charcoal/50 w-1/4">Baz (Mevcut Analiz)</th>
                    <th className="py-2 text-[10px] font-bold uppercase tracking-widest text-r2v-charcoal/30 text-center w-1/6">Değişim</th>
                    <th className="py-2 text-[10px] font-bold uppercase tracking-widest text-r2v-charcoal w-1/4">Senaryo</th>
                  </tr>
                </thead>
                <tbody className="text-sm">
                  <tr className="border-b border-r2v-charcoal/10">
                    <td className="py-4 text-[11px] font-bold uppercase tracking-widest text-r2v-charcoal/60">Önerilen Rota</td>
                    <td className="py-4 font-bold text-r2v-charcoal text-sm">{baseRoute}</td>
                    <td className="py-4 text-center text-r2v-charcoal/30"><ArrowRight className="w-4 h-4 mx-auto" /></td>
                    <td className="py-4 font-bold text-r2v-charcoal text-sm">{results[0].recommended_route}</td>
                  </tr>
                  <tr className="border-b border-r2v-charcoal/5">
                    <td className="py-3 text-[11px] font-bold uppercase tracking-widest text-r2v-charcoal/60">Beklenen Kâr (TL)</td>
                    <td className="py-3 font-mono">{baseProfit.toLocaleString('tr-TR', { maximumFractionDigits: 0 })}</td>
                    <td className={`py-3 text-center font-mono text-xs font-bold ${results[0].expected_profit_try > baseProfit ? 'text-r2v-green' : 'text-r2v-terracotta'}`}>
                      {results[0].expected_profit_try > baseProfit
                        ? `+${(results[0].expected_profit_try - baseProfit).toLocaleString('tr-TR', { maximumFractionDigits: 0 })} ↑`
                        : `${(results[0].expected_profit_try - baseProfit).toLocaleString('tr-TR', { maximumFractionDigits: 0 })} ↓`}
                    </td>
                    <td className="py-3 font-mono font-bold text-r2v-charcoal">
                      {results[0].expected_profit_try.toLocaleString('tr-TR', { maximumFractionDigits: 0 })}
                    </td>
                  </tr>
                  <tr className="border-b border-r2v-charcoal/5">
                    <td className="py-3 text-[11px] font-bold uppercase tracking-widest text-r2v-charcoal/60">CO₂ (kg)</td>
                    <td className="py-3 font-mono">{baseCO2.toLocaleString('tr-TR', { maximumFractionDigits: 1 })}</td>
                    <td className={`py-3 text-center font-mono text-xs font-bold ${results[0].co2_kg < baseCO2 ? 'text-r2v-green' : 'text-r2v-terracotta'}`}>
                      {results[0].co2_kg < baseCO2
                        ? `${(((results[0].co2_kg - baseCO2) / baseCO2) * 100).toFixed(0)}% ↓`
                        : `+${(((results[0].co2_kg - baseCO2) / baseCO2) * 100).toFixed(0)}% ↑`}
                    </td>
                    <td className="py-3 font-mono font-bold text-r2v-charcoal">
                      {results[0].co2_kg.toLocaleString('tr-TR', { maximumFractionDigits: 1 })}
                    </td>
                  </tr>
                  <tr>
                    <td className="py-3 text-[11px] font-bold uppercase tracking-widest text-r2v-charcoal/60">AI Güveni</td>
                    <td className="py-3 font-mono">{(result.confidence.overall * 100).toFixed(0)}</td>
                    <td className="py-3 text-center text-r2v-charcoal/30"><ArrowRight className="w-4 h-4 mx-auto" /></td>
                    <td className="py-3 font-mono font-bold text-r2v-charcoal">{(results[0].confidence_overall * 100).toFixed(0)}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          )}

          {/* Chart */}
          {chartData.length > 1 && (
            <div className="border-t-2 border-r2v-charcoal/10 pt-8">
              <h4 className="text-[11px] font-bold text-r2v-charcoal tracking-widest uppercase mb-1">Senaryo Kâr Karşılaştırması</h4>
              <p className="text-[10px] font-mono text-r2v-charcoal/40 mb-6">Beklenen Kâr (TL)</p>
              <div className="h-48 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={chartData} margin={{ top: 5, right: 0, left: 0, bottom: 0 }}>
                    <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fontSize: 9, fontFamily: 'monospace', fill: '#2D323A', opacity: 0.6 }} />
                    <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 9, fontFamily: 'monospace', fill: '#2D323A', opacity: 0.5 }}
                      tickFormatter={(v) => `${(v / 1000).toFixed(0)}k`} width={35} />
                    <Tooltip cursor={{ fill: 'transparent' }} contentStyle={{ border: '1px solid #2D323A', borderRadius: 0, fontSize: '10px', fontFamily: 'monospace' }} />
                    <Bar dataKey="kar" fill="#2D323A" fillOpacity={0.5} barSize={24} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}

          {/* Scenario History Table */}
          {results.length > 0 && (
            <div className="border-t-2 border-r2v-charcoal/10 pt-8">
              <h3 className="text-xl font-bold text-r2v-charcoal tracking-tight mb-6">Senaryo Geçmişi</h3>
              <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="text-[10px] font-bold text-r2v-charcoal/40 uppercase tracking-widest border-b border-r2v-charcoal/10">
                      <th className="pb-3 pr-4">Senaryo</th>
                      <th className="pb-3 px-4 text-right">Kâr (TL)</th>
                      <th className="pb-3 px-4 text-right">CO₂ (kg)</th>
                      <th className="pb-3 px-4">Rota</th>
                      <th className="pb-3 px-4 text-center">Güven</th>
                      <th className="pb-3 pl-4 text-center">Değişim</th>
                    </tr>
                  </thead>
                  <tbody className="text-xs">
                    {results.map((row, i) => (
                      <tr key={i} className="border-b border-r2v-charcoal/5 hover:bg-white/40 transition-colors">
                        <td className="py-4 pr-4 font-bold text-r2v-charcoal">{row.scenario}</td>
                        <td className="py-4 px-4 text-right font-mono text-r2v-charcoal">
                          {row.expected_profit_try.toLocaleString('tr-TR', { maximumFractionDigits: 0 })}
                        </td>
                        <td className="py-4 px-4 text-right font-mono text-r2v-charcoal">
                          {row.co2_kg.toLocaleString('tr-TR', { maximumFractionDigits: 1 })}
                        </td>
                        <td className="py-4 px-4 text-r2v-charcoal/80">{row.recommended_route}</td>
                        <td className="py-4 px-4 text-center font-mono font-bold text-r2v-charcoal">
                          {(row.confidence_overall * 100).toFixed(0)}
                        </td>
                        <td className="py-4 pl-4 text-center">
                          {row.expected_profit_try > baseProfit
                            ? <TrendingUp className="w-3 h-3 text-r2v-green mx-auto" />
                            : <TrendingDown className="w-3 h-3 text-r2v-terracotta mx-auto" />}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Empty state */}
          {results.length === 0 && (
            <div className="flex flex-col items-center justify-center py-24 text-center gap-4">
              <Info className="w-8 h-8 text-r2v-charcoal/20" />
              <p className="text-r2v-charcoal/50 text-sm font-medium">
                Parametreleri ayarlayın ve "Senaryoyu Çalıştır"a basın.
              </p>
              <p className="text-r2v-charcoal/30 text-xs font-mono">
                Baz: {result.recommended_route} — {baseProfit.toLocaleString('tr-TR', { maximumFractionDigits: 0 })} TL
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
