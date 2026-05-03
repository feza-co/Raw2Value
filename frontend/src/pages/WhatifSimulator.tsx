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
      <div className="max-w-7xl mx-auto pt-24 flex flex-col items-center gap-6 bg-white">
        <p className="text-[#0a0a0a] text-2xl font-bold tracking-tightest">Önce bir analiz yapmanız gerekiyor.</p>
        <Link
          to="/dashboard/material"
          className="flex items-center gap-2 px-6 py-3 bg-[#0a0a0a] text-white font-mono text-xs font-medium uppercase tracking-widest hover:bg-[#d6342a] transition-colors"
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

  const chartData = results.map((r: WhatIfResultRow) => ({
    name: r.scenario,
    kar: Math.round(r.expected_profit_try),
  }));

  return (
    <div className="max-w-[1400px] mx-auto space-y-12 pb-12 bg-white">
      {/* Header — Swiss eyebrow */}
      <div className="border-b-2 border-[#0a0a0a] pb-6">
        <div className="flex items-center gap-4 mb-3">
          <span className="bg-[#c97a17] text-white text-xs font-semibold font-mono px-2.5 py-1 tracking-wider">03</span>
          <span className="font-mono text-sm font-medium tracking-wider text-[#0a0a0a]">What-if Simulator</span>
        </div>
        <h1 className="text-5xl md:text-6xl font-bold tracking-tightest text-[#0a0a0a] mb-3 leading-[0.96]">Senaryo Etkisi.</h1>
        <p className="text-base text-[#2a2a2a] font-normal max-w-3xl">
          Döviz kuru, tonaj veya taşıma modu değişimlerinin kâr ve CO₂ üzerindeki etkisini simüle edin.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-16">
        {/* LEFT: Controls */}
        <div className="lg:col-span-4">
          <div className="flex justify-between items-end mb-8 border-b-2 border-[#0a0a0a] pb-2">
            <h3 className="text-2xl font-bold text-[#0a0a0a] tracking-tightest">Senaryo Parametreleri</h3>
            <button
              onClick={() => { setFxPct(0); setTonnageOverride(''); setTransportOverride(''); setScenarioName('Senaryo 1'); }}
              className="font-mono text-[10px] font-medium uppercase tracking-widest text-[#6b6b6b] hover:text-[#d6342a] flex items-center gap-1 transition-colors border border-[#0a0a0a] px-2 py-1"
            >
              <RefreshCcw className="w-3 h-3" /> Sıfırla
            </button>
          </div>

          {/* Scenario Name */}
          <div className="mb-6">
            <label className="font-mono text-[11px] font-medium text-[#0a0a0a] uppercase tracking-widest block mb-2">Senaryo Adı</label>
            <div className="border-b-2 border-[#0a0a0a] pb-2">
              <input
                type="text"
                value={scenarioName}
                onChange={(e) => setScenarioName(e.target.value)}
                maxLength={50}
                className="w-full bg-transparent border-none focus:ring-0 p-0 text-sm font-bold text-[#0a0a0a] outline-none"
              />
            </div>
          </div>

          {/* FX Scenario */}
          <div className="mb-6">
            <div className="flex justify-between items-end mb-2">
              <label className="font-mono text-[11px] font-medium text-[#0a0a0a] uppercase tracking-widest flex items-center gap-1">
                Kur Değişimi (FX) <Info className="w-3 h-3 opacity-50" />
              </label>
              <div className="flex items-center gap-1 border-b-2 border-[#0a0a0a] pb-0.5">
                <input
                  type="number"
                  value={(fxPct * 100).toFixed(0)}
                  onChange={(e) => setFxPct(Math.max(-20, Math.min(20, Number(e.target.value))) / 100)}
                  className="w-14 text-right bg-transparent border-none focus:ring-0 p-0 text-sm font-mono font-bold text-[#0a0a0a]"
                />
                <span className="font-mono text-[10px] text-[#6b6b6b]">%</span>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <span className="font-mono text-[9px] text-[#6b6b6b]">-20</span>
              <input
                type="range" min={-20} max={20} step={1}
                value={fxPct * 100}
                onChange={(e) => setFxPct(Number(e.target.value) / 100)}
                className="flex-1 h-1 bg-[#e6e6e6] appearance-none cursor-pointer accent-[#0a0a0a]"
              />
              <span className="font-mono text-[9px] text-[#6b6b6b]">+20</span>
            </div>
            <p className="font-mono text-[10px] text-[#6b6b6b] mt-1 tracking-wide">
              Baz kur: EUR {result.fx_used.eur_try.toFixed(2)} → {(result.fx_used.eur_try * (1 + fxPct)).toFixed(2)}
            </p>
          </div>

          {/* Tonnage Override */}
          <div className="mb-6">
            <label className="font-mono text-[11px] font-medium text-[#0a0a0a] uppercase tracking-widest block mb-2">
              Tonaj Değişimi (opsiyonel)
            </label>
            <div className="flex items-center border-b-2 border-[#0a0a0a] pb-2">
              <input
                type="number"
                value={tonnageOverride}
                onChange={(e) => setTonnageOverride(e.target.value)}
                placeholder={`Mevcut: ${request.tonnage}`}
                className="w-full bg-transparent border-none focus:ring-0 p-0 text-sm font-mono font-bold text-[#0a0a0a] outline-none placeholder:text-[#6b6b6b]"
              />
              <span className="font-mono text-[10px] text-[#6b6b6b] ml-2 uppercase tracking-widest">TON</span>
            </div>
          </div>

          {/* Transport Override */}
          <div className="mb-8">
            <label className="font-mono text-[11px] font-medium text-[#0a0a0a] uppercase tracking-widest block mb-2">
              Taşıma Modu Değişimi (opsiyonel)
            </label>
            <select
              value={transportOverride}
              onChange={(e) => setTransportOverride(e.target.value as TransportMode | '')}
              className="w-full bg-transparent border-b-2 border-[#0a0a0a] pb-2 text-sm font-bold text-[#0a0a0a] focus:ring-0 outline-none cursor-pointer"
            >
              <option value="">— Mevcut tut ({TRANSPORT_LABELS[request.transport_mode]}) —</option>
              {(Object.entries(TRANSPORT_LABELS) as [TransportMode, string][]).map(([k, v]) => (
                <option key={k} value={k}>{v}</option>
              ))}
            </select>
          </div>

          {/* Presets */}
          <div className="pt-6 border-t-2 border-[#0a0a0a]">
            <p className="font-mono text-[11px] font-medium text-[#0a0a0a] uppercase tracking-widest mb-4">Hazır Senaryolar</p>
            <div className="flex flex-wrap gap-2">
              {PRESETS.map((p) => (
                <button
                  key={p.name}
                  onClick={() => applyPreset(p)}
                  className="px-3 py-1.5 border border-[#0a0a0a] text-[#0a0a0a] font-mono text-[10px] font-medium uppercase tracking-widest hover:bg-[#0a0a0a] hover:text-white transition-colors"
                >
                  {p.name}
                </button>
              ))}
            </div>
          </div>

          {error && (
            <div className="mt-6 p-4 bg-white border-2 border-[#d6342a] text-sm text-[#d6342a] font-medium">
              {error}
            </div>
          )}

          <button
            onClick={handleRun}
            disabled={isRunning}
            className="w-full mt-8 bg-[#0a0a0a] text-white h-12 flex items-center justify-center gap-2 hover:bg-[#1d4fd6] transition-colors disabled:opacity-70 font-mono text-xs font-medium uppercase tracking-widest"
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
              <h3 className="text-2xl font-bold text-[#0a0a0a] tracking-tightest mb-6">Son Senaryo — Baz Karşılaştırması</h3>
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="border-b-2 border-[#0a0a0a]">
                    <th className="py-2 w-1/4"></th>
                    <th className="py-2 font-mono text-[11px] font-medium uppercase tracking-widest text-[#6b6b6b] w-1/4">Baz (Mevcut Analiz)</th>
                    <th className="py-2 font-mono text-[11px] font-medium uppercase tracking-widest text-[#6b6b6b] text-center w-1/6">Değişim</th>
                    <th className="py-2 font-mono text-[11px] font-medium uppercase tracking-widest text-[#0a0a0a] w-1/4">Senaryo</th>
                  </tr>
                </thead>
                <tbody className="text-sm">
                  <tr className="border-b border-[#e6e6e6]">
                    <td className="py-4 font-mono text-[11px] font-medium uppercase tracking-widest text-[#0a0a0a]">Önerilen Rota</td>
                    <td className="py-4 font-bold text-[#2a2a2a] text-sm">{baseRoute}</td>
                    <td className="py-4 text-center text-[#6b6b6b]"><ArrowRight className="w-4 h-4 mx-auto" /></td>
                    <td className="py-4 font-bold text-[#0a0a0a] text-sm">{results[0].recommended_route}</td>
                  </tr>
                  <tr className="border-b border-[#e6e6e6]">
                    <td className="py-3 font-mono text-[11px] font-medium uppercase tracking-widest text-[#0a0a0a]">Beklenen Kâr (TL)</td>
                    <td className="py-3 font-mono text-[#2a2a2a] tabular-nums">{baseProfit.toLocaleString('tr-TR', { maximumFractionDigits: 0 })}</td>
                    <td className={`py-3 text-center font-mono text-xs font-bold ${results[0].expected_profit_try > baseProfit ? 'text-[#1f7a3a]' : 'text-[#d6342a]'}`}>
                      {results[0].expected_profit_try > baseProfit
                        ? `+${(results[0].expected_profit_try - baseProfit).toLocaleString('tr-TR', { maximumFractionDigits: 0 })} ↑`
                        : `${(results[0].expected_profit_try - baseProfit).toLocaleString('tr-TR', { maximumFractionDigits: 0 })} ↓`}
                    </td>
                    <td className="py-3 font-mono font-bold text-[#0a0a0a] tabular-nums">
                      {results[0].expected_profit_try.toLocaleString('tr-TR', { maximumFractionDigits: 0 })}
                    </td>
                  </tr>
                  <tr className="border-b border-[#e6e6e6]">
                    <td className="py-3 font-mono text-[11px] font-medium uppercase tracking-widest text-[#0a0a0a]">CO₂ (kg)</td>
                    <td className="py-3 font-mono text-[#2a2a2a] tabular-nums">{baseCO2.toLocaleString('tr-TR', { maximumFractionDigits: 1 })}</td>
                    <td className={`py-3 text-center font-mono text-xs font-bold ${results[0].co2_kg < baseCO2 ? 'text-[#1f7a3a]' : 'text-[#d6342a]'}`}>
                      {results[0].co2_kg < baseCO2
                        ? `${(((results[0].co2_kg - baseCO2) / baseCO2) * 100).toFixed(0)}% ↓`
                        : `+${(((results[0].co2_kg - baseCO2) / baseCO2) * 100).toFixed(0)}% ↑`}
                    </td>
                    <td className="py-3 font-mono font-bold text-[#0a0a0a] tabular-nums">
                      {results[0].co2_kg.toLocaleString('tr-TR', { maximumFractionDigits: 1 })}
                    </td>
                  </tr>
                  <tr>
                    <td className="py-3 font-mono text-[11px] font-medium uppercase tracking-widest text-[#0a0a0a]">AI Güveni</td>
                    <td className="py-3 font-mono text-[#2a2a2a] tabular-nums">{(result.confidence.overall * 100).toFixed(0)}</td>
                    <td className="py-3 text-center text-[#6b6b6b]"><ArrowRight className="w-4 h-4 mx-auto" /></td>
                    <td className="py-3 font-mono font-bold text-[#0a0a0a] tabular-nums">{(results[0].confidence_overall * 100).toFixed(0)}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          )}

          {/* Chart */}
          {chartData.length > 1 && (
            <div className="border-t-2 border-[#0a0a0a] pt-8">
              <h4 className="font-mono text-xs font-semibold text-[#0a0a0a] tracking-widest uppercase mb-1">Senaryo Kâr Karşılaştırması</h4>
              <p className="font-mono text-[10px] text-[#6b6b6b] mb-6 tracking-wide">Beklenen Kâr (TL)</p>
              <div className="h-48 w-full border-2 border-[#0a0a0a] p-3">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={chartData} margin={{ top: 5, right: 0, left: 0, bottom: 0 }}>
                    <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fontSize: 9, fontFamily: 'JetBrains Mono', fill: '#0a0a0a' }} />
                    <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 9, fontFamily: 'JetBrains Mono', fill: '#6b6b6b' }}
                      tickFormatter={(v) => `${(v / 1000).toFixed(0)}k`} width={35} />
                    <Tooltip cursor={{ fill: 'transparent' }} contentStyle={{ border: '2px solid #0a0a0a', borderRadius: 0, background: 'white', fontSize: '10px', fontFamily: 'JetBrains Mono' }} />
                    <Bar dataKey="kar" fill="#1d4fd6" barSize={24} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}

          {/* Scenario History Table */}
          {results.length > 0 && (
            <div className="border-t-2 border-[#0a0a0a] pt-8">
              <h3 className="text-2xl font-bold text-[#0a0a0a] tracking-tightest mb-6">Senaryo Geçmişi</h3>
              <div className="overflow-x-auto border-2 border-[#0a0a0a]">
                <table className="w-full text-left border-collapse">
                  <thead className="bg-[#0a0a0a] text-white">
                    <tr className="font-mono text-[11px] font-medium uppercase tracking-widest">
                      <th className="py-3 px-4">Senaryo</th>
                      <th className="py-3 px-4 text-right">Kâr (TL)</th>
                      <th className="py-3 px-4 text-right">CO₂ (kg)</th>
                      <th className="py-3 px-4">Rota</th>
                      <th className="py-3 px-4 text-center">Güven</th>
                      <th className="py-3 px-4 text-center">Değişim</th>
                    </tr>
                  </thead>
                  <tbody className="text-xs bg-white">
                    {results.map((row: WhatIfResultRow, i: number) => (
                      <tr key={i} className="border-t border-[#e6e6e6] hover:bg-[#f4f4f4] transition-colors">
                        <td className="py-4 px-4 font-bold text-[#0a0a0a]">{row.scenario}</td>
                        <td className="py-4 px-4 text-right font-mono text-[#0a0a0a] tabular-nums">
                          {row.expected_profit_try.toLocaleString('tr-TR', { maximumFractionDigits: 0 })}
                        </td>
                        <td className="py-4 px-4 text-right font-mono text-[#0a0a0a] tabular-nums">
                          {row.co2_kg.toLocaleString('tr-TR', { maximumFractionDigits: 1 })}
                        </td>
                        <td className="py-4 px-4 text-[#2a2a2a]">{row.recommended_route}</td>
                        <td className="py-4 px-4 text-center font-mono font-bold text-[#0a0a0a] tabular-nums">
                          {(row.confidence_overall * 100).toFixed(0)}
                        </td>
                        <td className="py-4 px-4 text-center">
                          {row.expected_profit_try > baseProfit
                            ? <TrendingUp className="w-3 h-3 text-[#1f7a3a] mx-auto" />
                            : <TrendingDown className="w-3 h-3 text-[#d6342a] mx-auto" />}
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
            <div className="flex flex-col items-center justify-center py-24 text-center gap-4 border-2 border-dashed border-[#0a0a0a]">
              <Info className="w-8 h-8 text-[#0a0a0a]" />
              <p className="text-[#0a0a0a] text-sm font-medium">
                Parametreleri ayarlayın ve "Senaryoyu Çalıştır"a basın.
              </p>
              <p className="text-[#6b6b6b] font-mono text-xs tracking-wide">
                Baz: {result.recommended_route} — {baseProfit.toLocaleString('tr-TR', { maximumFractionDigits: 0 })} TL
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
