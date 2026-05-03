import { useState } from 'react';
import { CheckCircle2, TrendingUp, ChevronDown, ChevronUp, AlertTriangle, ArrowRight } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { Link } from 'react-router-dom';
import { useAnalysis } from '../contexts/AnalysisContext';

const MATERIAL_LABELS: Record<string, string> = {
  pomza: 'Pomza',
  perlit: 'Perlit',
  kabak_cekirdegi: 'Kabak Çekirdeği',
};

const COUNTRY_LABELS: Record<string, string> = {
  TR: 'Türkiye',
  DE: 'Almanya',
  NL: 'Hollanda',
};

function confidenceLabel(score: number): string {
  if (score >= 0.8) return 'Yüksek Kesinlik';
  if (score >= 0.6) return 'Orta Kesinlik';
  return 'Düşük Kesinlik';
}

function confidenceColor(score: number): string {
  if (score >= 0.8) return 'text-[#1f7a3a]';
  if (score >= 0.6) return 'text-[#0a0a0a]';
  return 'text-[#d6342a]';
}

export default function DecisionCockpit() {
  const { request, result } = useAnalysis();
  const [selectedRoute, setSelectedRoute] = useState<string | null>(null);
  const [showDetails, setShowDetails] = useState(false);

  if (!result || !request) {
    return (
      <div className="max-w-7xl mx-auto pt-24 flex flex-col items-center gap-6 bg-white">
        <p className="text-[#0a0a0a] text-2xl font-bold tracking-tightest">Henüz analiz yapılmadı.</p>
        <Link
          to="/dashboard/material"
          className="flex items-center gap-2 px-6 py-3 bg-[#0a0a0a] text-white font-mono text-xs font-medium uppercase tracking-widest hover:bg-[#d6342a] transition-colors"
        >
          Material Analyzer'a Git <ArrowRight className="w-4 h-4" />
        </Link>
      </div>
    );
  }

  const confidence100 = Math.round(result.confidence.overall * 100);
  const activeRoute = selectedRoute ?? result.recommended_route;
  const shapData = result.feature_importance.slice(0, 6).map((f: { feature: string; importance: number }) => ({
    feature: f.feature,
    value: f.importance,
  }));

  return (
    <div className="max-w-7xl mx-auto space-y-12 pb-12 bg-white">
      {/* Header — Swiss eyebrow */}
      <div className="border-b-2 border-[#0a0a0a] pb-6 mb-8 flex justify-between items-end gap-6 flex-wrap">
        <div>
          <div className="flex items-center gap-4 mb-3">
            <span className="bg-[#1d4fd6] text-white text-xs font-semibold font-mono px-2.5 py-1 tracking-wider">02</span>
            <span className="font-mono text-sm font-medium tracking-wider text-[#0a0a0a]">AI Decision Cockpit</span>
          </div>
          <h1 className="text-5xl md:text-6xl font-bold tracking-tightest text-[#0a0a0a] mb-3 leading-[0.96]">Karar Yönlendirmesi.</h1>
          <p className="text-base text-[#2a2a2a] font-normal">Sistem optimizasyonu ve karar yönlendirmesi.</p>
        </div>
        <div className="text-right hidden md:block">
          <div className="font-mono text-[11px] font-medium uppercase tracking-widest text-[#6b6b6b] mb-1">Model</div>
          <div className="font-mono text-sm text-[#0a0a0a]">{result.model_version}</div>
        </div>
      </div>

      {/* Summary Row */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-0 border-2 border-[#0a0a0a]">
        {[
          { l: 'Hammadde', v: MATERIAL_LABELS[request.raw_material] ?? request.raw_material, accent: false },
          { l: 'Kaynak', v: request.origin_city, accent: false },
          { l: 'Tonaj', v: `${request.tonnage.toLocaleString('tr-TR')} ton`, accent: false },
          { l: 'Kalite', v: `${request.quality} Sınıfı`, accent: false },
          { l: 'Hedef Pazar', v: COUNTRY_LABELS[request.target_country] ?? request.target_country, accent: true },
        ].map((item, i) => (
          <div key={i} className={`p-5 ${i < 4 ? 'border-r-2 md:border-r-2 border-[#0a0a0a]' : ''} ${i < 4 && i % 2 === 1 ? 'border-r-0 md:border-r-2' : ''} border-b-2 md:border-b-0 ${item.accent ? 'bg-[#d6342a] text-white' : 'bg-white'}`}>
            <p className={`font-mono text-[11px] font-medium uppercase tracking-widest mb-2 ${item.accent ? 'text-white/80' : 'text-[#6b6b6b]'}`}>{item.l}</p>
            <p className={`text-lg font-bold tracking-tight ${item.accent ? 'text-white' : 'text-[#0a0a0a]'}`}>{item.v}</p>
          </div>
        ))}
      </div>

      {/* Warnings */}
      {(result.warnings.length > 0 || result.confidence.warnings.length > 0) && (
        <div className="flex flex-col gap-2">
          {[...result.warnings, ...result.confidence.warnings].map((w: string, i: number) => (
            <div key={i} className="flex items-start gap-3 p-3 bg-white border-2 border-[#d6342a]">
              <AlertTriangle className="w-4 h-4 text-[#d6342a] shrink-0 mt-0.5" />
              <p className="text-sm text-[#0a0a0a]">{w}</p>
            </div>
          ))}
        </div>
      )}

      <div className="pt-4 space-y-8">
        {/* Level 1: Main Result */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-8 border-l-[6px] border-[#1f7a3a] pl-8 py-6 bg-white">
          <div className="flex-1">
            <div className="inline-flex items-center gap-2 text-[#1f7a3a] font-mono text-xs font-semibold uppercase tracking-widest mb-4">
              <CheckCircle2 className="w-4 h-4" /> AI Önerisi Onaylandı
            </div>
            <h2 className="text-4xl md:text-6xl font-bold tracking-tightest text-[#0a0a0a] mb-8 break-words leading-[0.96]">{result.recommended_route}</h2>

            <div className="flex items-center gap-12 flex-wrap">
              <div>
                <p className="font-mono text-[11px] font-medium text-[#6b6b6b] uppercase tracking-widest mb-2">Net Kâr (Tahmini)</p>
                <p className="text-4xl font-bold font-mono text-[#0a0a0a] tracking-tightest tabular-nums">
                  {result.expected_profit_try.toLocaleString('tr-TR', { maximumFractionDigits: 0 })} <span className="text-xl text-[#6b6b6b]">TL</span>
                </p>
              </div>
              <div>
                <p className="font-mono text-[11px] font-medium text-[#6b6b6b] uppercase tracking-widest mb-2">Değer Artışı</p>
                <p className="text-3xl font-bold text-[#1f7a3a] flex items-center gap-2 tabular-nums">
                  <TrendingUp className="w-6 h-6" /> +%{result.value_uplift_pct.toFixed(1)}
                </p>
              </div>
            </div>
          </div>

          <div className="shrink-0 md:text-right flex flex-col items-end pr-6">
            <p className="font-mono text-[11px] font-medium text-[#6b6b6b] uppercase tracking-widest mb-2">AI Güven Skoru</p>
            <div className="text-6xl font-bold font-mono text-[#1d4fd6] mb-2 tracking-tightest tabular-nums">
              {confidence100}<span className="text-2xl text-[#6b6b6b] font-medium">/100</span>
            </div>
            <p className={`font-mono text-xs font-semibold uppercase tracking-widest mb-6 ${confidenceColor(result.confidence.overall)}`}>
              {confidenceLabel(result.confidence.overall)}
            </p>
            <button
              onClick={() => setShowDetails(!showDetails)}
              className="group flex items-center gap-2 px-6 py-3 border-2 border-[#0a0a0a] hover:bg-[#0a0a0a] hover:text-white font-mono text-xs font-medium text-[#0a0a0a] uppercase tracking-widest transition-all"
            >
              {showDetails ? 'Detayları Gizle' : 'Nedenleri Gör'}
              {showDetails ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4 group-hover:translate-y-1 transition-transform" />}
            </button>
          </div>
        </div>

        {/* Level 2: Details */}
        {showDetails && (
          <div className="pt-12 border-t-2 border-[#0a0a0a]">
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-16">

              {/* Left: SHAP + Route Table */}
              <div className="lg:col-span-8 space-y-16">

                {shapData.length > 0 && (
                  <div>
                    <h3 className="font-mono text-xs font-semibold text-[#0a0a0a] tracking-widest uppercase mb-8 pb-3 border-b border-[#0a0a0a]">Karar Faktörleri (Feature Importance)</h3>
                    <div className="h-48 w-full">
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={shapData} layout="vertical" margin={{ top: 0, right: 0, left: 0, bottom: 0 }}>
                          <XAxis type="number" hide />
                          <YAxis dataKey="feature" type="category" axisLine={false} tickLine={false}
                            tick={{ fontSize: 11, fontWeight: 'bold', fill: '#0a0a0a', fontFamily: 'JetBrains Mono' }} width={200} />
                          <Tooltip cursor={{ fill: 'transparent' }} contentStyle={{ border: '2px solid #0a0a0a', borderRadius: 0, background: 'white', fontWeight: 'bold', fontSize: '12px' }} />
                          <Bar dataKey="value" barSize={12} fill="#1d4fd6" />
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  </div>
                )}

                {/* Route Alternatives */}
                <div>
                  <div className="flex justify-between items-end mb-6 border-b-2 border-[#0a0a0a] pb-4">
                    <h3 className="text-2xl font-bold text-[#0a0a0a] tracking-tightest">Tüm Rotalar</h3>
                  </div>
                  <div className="overflow-x-auto">
                    <table className="w-full text-left border-collapse">
                      <thead>
                        <tr className="font-mono text-[11px] font-medium text-[#0a0a0a] uppercase tracking-widest border-b-2 border-[#0a0a0a]">
                          <th className="pb-3 pr-4">Rota</th>
                          <th className="pb-3 px-4 text-right">Kâr (TL)</th>
                          <th className="pb-3 px-4 text-right">CO₂ (kg)</th>
                          <th className="pb-3 px-4 text-right">Olasılık</th>
                          <th className="pb-3 pl-4">Durum</th>
                        </tr>
                      </thead>
                      <tbody className="text-sm">
                        {result.route_alternatives.map((route: { route: string; profit_try: number; co2_kg: number; probability: number }) => {
                          const isSelected = activeRoute === route.route;
                          const isRecommended = route.route === result.recommended_route;
                          return (
                            <tr
                              key={route.route}
                              onClick={() => setSelectedRoute(route.route)}
                              className={`border-b border-[#e6e6e6] transition-colors cursor-pointer ${isSelected ? 'bg-[#f4f4f4]' : 'hover:bg-[#f4f4f4]'}`}
                            >
                              <td className="py-5 pr-4 font-bold text-[#0a0a0a] flex items-center gap-3">
                                <div className={`w-3 h-3 shrink-0 ${isSelected ? (isRecommended ? 'bg-[#1f7a3a]' : 'bg-[#0a0a0a]') : 'bg-[#e6e6e6]'}`}></div>
                                {route.route}
                              </td>
                              <td className="py-5 px-4 font-mono text-right text-[#0a0a0a] tabular-nums">
                                {route.profit_try.toLocaleString('tr-TR', { maximumFractionDigits: 0 })}
                              </td>
                              <td className="py-5 px-4 font-mono text-right text-[#0a0a0a] tabular-nums">
                                {route.co2_kg.toLocaleString('tr-TR', { maximumFractionDigits: 1 })}
                              </td>
                              <td className="py-5 px-4 font-mono text-right text-[#0a0a0a] tabular-nums">
                                %{(route.probability * 100).toFixed(0)}
                              </td>
                              <td className="py-5 pl-4">
                                {isRecommended ? (
                                  <span className="text-white bg-[#1f7a3a] font-mono font-medium text-[10px] uppercase tracking-widest px-2 py-1">Önerilen</span>
                                ) : (
                                  <span className="text-[#6b6b6b] font-mono font-medium text-[10px] uppercase tracking-widest">Alternatif</span>
                                )}
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>

              {/* Right: FX + Buyers */}
              <div className="lg:col-span-4 space-y-12 lg:pl-12 lg:border-l-2 lg:border-[#0a0a0a]">
                <div className="grid grid-cols-2 gap-6">
                  <div>
                    <p className="font-mono text-[11px] font-medium uppercase tracking-widest text-[#6b6b6b] mb-2">EUR/TRY (TCMB)</p>
                    <p className="text-3xl font-mono font-bold text-[#0a0a0a] tabular-nums">{result.fx_used.eur_try.toFixed(2)}</p>
                  </div>
                  <div>
                    <p className="font-mono text-[11px] font-medium uppercase tracking-widest text-[#6b6b6b] mb-2">USD/TRY (TCMB)</p>
                    <p className="text-3xl font-mono font-bold text-[#0a0a0a] tabular-nums">{result.fx_used.usd_try.toFixed(2)}</p>
                  </div>
                </div>

                <div>
                  <p className="font-mono text-[11px] font-medium uppercase tracking-widest text-[#6b6b6b] mb-2">Toplam CO₂</p>
                  <p className="text-3xl font-mono font-bold text-[#0a0a0a] tabular-nums">
                    {result.co2_kg.toLocaleString('tr-TR', { maximumFractionDigits: 1 })} <span className="text-base text-[#6b6b6b] font-medium">kg</span>
                  </p>
                </div>

                {result.match_results.length > 0 && (
                  <div>
                    <h3 className="font-mono text-[11px] font-semibold uppercase tracking-widest text-[#0a0a0a] mb-4 flex items-center justify-between border-b-2 border-[#0a0a0a] pb-2">
                      <span>Alıcı Eşleşmeleri</span>
                      <span className="font-mono text-[10px] font-medium text-white bg-[#d6342a] px-2 py-0.5 uppercase tracking-widest">
                        {COUNTRY_LABELS[request.target_country] ?? request.target_country}
                      </span>
                    </h3>
                    <div className="space-y-0">
                      {result.match_results.slice(0, 5).map((m: { buyer: string; processor: string; score: number }) => (
                        <div key={m.buyer} className="py-4 border-b border-[#e6e6e6] flex items-center justify-between group">
                          <div>
                            <p className="text-base font-bold text-[#0a0a0a] group-hover:text-[#d6342a] transition-colors">{m.buyer}</p>
                            <p className="font-mono text-xs text-[#6b6b6b] mt-1 tracking-wide">{m.processor}</p>
                          </div>
                          <div className="text-right">
                            <p className={`text-xl font-mono font-bold tabular-nums ${m.score >= 0.8 ? 'text-[#1f7a3a]' : 'text-[#0a0a0a]'}`}>
                              %{(m.score * 100).toFixed(0)}
                            </p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {result.reason_codes.length > 0 && (
                  <div>
                    <h3 className="font-mono text-[11px] font-semibold uppercase tracking-widest text-[#0a0a0a] mb-4 border-b-2 border-[#0a0a0a] pb-2">
                      Karar Gerekçeleri
                    </h3>
                    <div className="space-y-4">
                      {result.reason_codes.slice(0, 3).map((r: { text: string }, i: number) => (
                        <div key={i} className="flex gap-3">
                          <span className="text-[#d6342a] font-mono text-sm font-bold shrink-0">0{i + 1}</span>
                          <p className="text-sm text-[#2a2a2a] leading-relaxed">{r.text}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
