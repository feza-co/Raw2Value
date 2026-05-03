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
  if (score >= 0.8) return 'text-r2v-green';
  if (score >= 0.6) return 'text-r2v-charcoal';
  return 'text-r2v-terracotta';
}

export default function DecisionCockpit() {
  const { request, result } = useAnalysis();
  const [selectedRoute, setSelectedRoute] = useState<string | null>(null);
  const [showDetails, setShowDetails] = useState(false);

  if (!result || !request) {
    return (
      <div className="max-w-7xl mx-auto pt-24 flex flex-col items-center gap-6">
        <p className="text-r2v-charcoal/60 text-base">Henüz analiz yapılmadı.</p>
        <Link
          to="/dashboard/material"
          className="flex items-center gap-2 px-6 py-3 bg-r2v-charcoal text-white text-xs font-bold uppercase tracking-widest hover:bg-r2v-charcoal/90 transition-colors"
        >
          Material Analyzer'a Git <ArrowRight className="w-4 h-4" />
        </Link>
      </div>
    );
  }

  const confidence100 = Math.round(result.confidence.overall * 100);
  const activeRoute = selectedRoute ?? result.recommended_route;
  const shapData = result.feature_importance.slice(0, 6).map((f) => ({
    feature: f.feature,
    value: f.importance,
  }));

  return (
    <div className="max-w-7xl mx-auto space-y-12 pb-12">
      {/* Header */}
      <div className="border-b border-r2v-charcoal/20 pb-6 mb-8 flex justify-between items-end">
        <div>
          <h1 className="text-4xl font-bold tracking-tight text-r2v-charcoal mb-2">AI Decision Cockpit</h1>
          <p className="text-base text-r2v-charcoal/60 font-normal">Sistem optimizasyonu ve karar yönlendirmesi.</p>
        </div>
        <div className="text-right hidden md:block">
          <div className="text-[10px] font-bold uppercase tracking-widest text-r2v-charcoal/40 mb-1">Model</div>
          <div className="text-sm font-mono text-r2v-charcoal">{result.model_version}</div>
        </div>
      </div>

      {/* Summary Row */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-8 px-2">
        <div className="border-l-2 border-r2v-charcoal/10 pl-4">
          <p className="text-[11px] font-bold uppercase tracking-widest text-r2v-charcoal/50 mb-1">Hammadde</p>
          <p className="text-lg font-semibold text-r2v-charcoal">{MATERIAL_LABELS[request.raw_material] ?? request.raw_material}</p>
        </div>
        <div className="border-l-2 border-r2v-charcoal/10 pl-4">
          <p className="text-[11px] font-bold uppercase tracking-widest text-r2v-charcoal/50 mb-1">Kaynak</p>
          <p className="text-lg font-semibold text-r2v-charcoal">{request.origin_city}</p>
        </div>
        <div className="border-l-2 border-r2v-charcoal/10 pl-4">
          <p className="text-[11px] font-bold uppercase tracking-widest text-r2v-charcoal/50 mb-1">Tonaj</p>
          <p className="text-lg font-semibold text-r2v-charcoal">{request.tonnage.toLocaleString('tr-TR')} ton</p>
        </div>
        <div className="border-l-2 border-r2v-charcoal/10 pl-4">
          <p className="text-[11px] font-bold uppercase tracking-widest text-r2v-charcoal/50 mb-1">Kalite</p>
          <p className="text-lg font-semibold text-r2v-charcoal">{request.quality} Sınıfı</p>
        </div>
        <div className="border-l-2 border-r2v-terracotta pl-4">
          <p className="text-[11px] font-bold uppercase tracking-widest text-r2v-terracotta/80 mb-1">Hedef Pazar</p>
          <p className="text-lg font-semibold text-r2v-charcoal">{COUNTRY_LABELS[request.target_country] ?? request.target_country}</p>
        </div>
      </div>

      {/* Warnings */}
      {(result.warnings.length > 0 || result.confidence.warnings.length > 0) && (
        <div className="flex flex-col gap-2">
          {[...result.warnings, ...result.confidence.warnings].map((w, i) => (
            <div key={i} className="flex items-start gap-3 p-3 bg-r2v-terracotta/5 border border-r2v-terracotta/20">
              <AlertTriangle className="w-4 h-4 text-r2v-terracotta shrink-0 mt-0.5" />
              <p className="text-sm text-r2v-charcoal/80">{w}</p>
            </div>
          ))}
        </div>
      )}

      <div className="pt-8 space-y-8">
        {/* Level 1: Main Result */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-8 border-l-4 border-r2v-green pl-8">
          <div className="flex-1">
            <div className="inline-flex items-center gap-2 text-r2v-green text-xs font-bold uppercase tracking-widest mb-4">
              <CheckCircle2 className="w-4 h-4" /> AI Önerisi Onaylandı
            </div>
            <h2 className="text-5xl font-bold tracking-tight text-r2v-charcoal mb-8 break-words">{result.recommended_route}</h2>

            <div className="flex items-center gap-12">
              <div>
                <p className="text-r2v-charcoal/50 text-[11px] font-bold uppercase tracking-widest mb-2">Net Kâr (Tahmini)</p>
                <p className="text-4xl font-light font-mono text-r2v-charcoal">
                  {result.expected_profit_try.toLocaleString('tr-TR', { maximumFractionDigits: 0 })} <span className="text-xl">TL</span>
                </p>
              </div>
              <div>
                <p className="text-r2v-charcoal/50 text-[11px] font-bold uppercase tracking-widest mb-2">Değer Artışı</p>
                <p className="text-3xl font-semibold text-r2v-green flex items-center gap-2">
                  <TrendingUp className="w-6 h-6" /> +%{result.value_uplift_pct.toFixed(1)}
                </p>
              </div>
            </div>
          </div>

          <div className="shrink-0 md:text-right flex flex-col items-end">
            <p className="text-r2v-charcoal/50 text-[11px] font-bold uppercase tracking-widest mb-2">AI Güven Skoru</p>
            <div className="text-6xl font-light font-mono text-r2v-charcoal mb-2">
              {confidence100}<span className="text-2xl text-r2v-charcoal/40">/100</span>
            </div>
            <p className={`text-xs font-bold uppercase tracking-widest mb-6 ${confidenceColor(result.confidence.overall)}`}>
              {confidenceLabel(result.confidence.overall)}
            </p>
            <button
              onClick={() => setShowDetails(!showDetails)}
              className="group flex items-center gap-2 px-6 py-3 border border-r2v-charcoal/20 hover:border-r2v-charcoal/50 hover:bg-white/50 text-sm font-bold text-r2v-charcoal uppercase tracking-widest transition-all"
            >
              {showDetails ? 'Detayları Gizle' : 'Nedenleri Gör'}
              {showDetails ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4 group-hover:translate-y-1 transition-transform" />}
            </button>
          </div>
        </div>

        {/* Level 2: Details */}
        {showDetails && (
          <div className="pt-12 border-t border-r2v-charcoal/10 animate-in fade-in slide-in-from-top-4 duration-500">
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-16">

              {/* Left: SHAP + Route Table */}
              <div className="lg:col-span-8 space-y-16">

                {shapData.length > 0 && (
                  <div>
                    <h3 className="text-sm font-bold text-r2v-charcoal tracking-widest uppercase mb-8">Karar Faktörleri (Feature Importance)</h3>
                    <div className="h-48 w-full">
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={shapData} layout="vertical" margin={{ top: 0, right: 0, left: 0, bottom: 0 }}>
                          <XAxis type="number" hide />
                          <YAxis dataKey="feature" type="category" axisLine={false} tickLine={false}
                            tick={{ fontSize: 11, fontWeight: 'bold', fill: '#2D323A', opacity: 0.6 }} width={200} />
                          <Tooltip cursor={{ fill: 'transparent' }} contentStyle={{ border: 'none', background: 'transparent', fontWeight: 'bold', fontSize: '12px' }} />
                          <Bar dataKey="value" barSize={12} radius={[0, 4, 4, 0]} fill="#6B8E78" />
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  </div>
                )}

                {/* Route Alternatives */}
                <div>
                  <div className="flex justify-between items-end mb-6 border-b border-r2v-charcoal/20 pb-4">
                    <h3 className="text-xl font-bold text-r2v-charcoal tracking-tight">Tüm Rotalar</h3>
                  </div>
                  <div className="overflow-x-auto">
                    <table className="w-full text-left border-collapse">
                      <thead>
                        <tr className="text-[10px] font-bold text-r2v-charcoal/40 uppercase tracking-widest border-b border-r2v-charcoal/10">
                          <th className="pb-3 pr-4">Rota</th>
                          <th className="pb-3 px-4 text-right">Kâr (TL)</th>
                          <th className="pb-3 px-4 text-right">CO₂ (kg)</th>
                          <th className="pb-3 px-4 text-right">Olasılık</th>
                          <th className="pb-3 pl-4">Durum</th>
                        </tr>
                      </thead>
                      <tbody className="text-sm">
                        {result.route_alternatives.map((route) => {
                          const isSelected = activeRoute === route.route;
                          const isRecommended = route.route === result.recommended_route;
                          return (
                            <tr
                              key={route.route}
                              onClick={() => setSelectedRoute(route.route)}
                              className={`border-b border-r2v-charcoal/5 transition-colors cursor-pointer ${isSelected ? 'bg-white/60' : 'hover:bg-white/40'}`}
                            >
                              <td className="py-5 pr-4 font-bold text-r2v-charcoal flex items-center gap-3">
                                <div className={`w-3 h-3 rounded-sm shrink-0 ${isSelected ? (isRecommended ? 'bg-r2v-green' : 'bg-r2v-charcoal') : 'bg-r2v-charcoal/10'}`}></div>
                                {route.route}
                              </td>
                              <td className="py-5 px-4 font-mono text-right text-r2v-charcoal">
                                {route.profit_try.toLocaleString('tr-TR', { maximumFractionDigits: 0 })}
                              </td>
                              <td className="py-5 px-4 font-mono text-right text-r2v-charcoal">
                                {route.co2_kg.toLocaleString('tr-TR', { maximumFractionDigits: 1 })}
                              </td>
                              <td className="py-5 px-4 font-mono text-right text-r2v-charcoal">
                                %{(route.probability * 100).toFixed(0)}
                              </td>
                              <td className="py-5 pl-4">
                                {isRecommended ? (
                                  <span className="text-r2v-green font-bold text-[10px] uppercase tracking-widest">Önerilen Rota</span>
                                ) : (
                                  <span className="text-r2v-charcoal/50 font-bold text-[10px] uppercase tracking-widest">Alternatif</span>
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
              <div className="lg:col-span-4 space-y-12 md:pl-8 md:border-l border-r2v-charcoal/10">
                <div className="grid grid-cols-2 gap-6">
                  <div>
                    <p className="text-[10px] font-bold uppercase tracking-widest text-r2v-charcoal/50 mb-2">EUR/TRY (TCMB)</p>
                    <p className="text-3xl font-mono font-light text-r2v-charcoal">{result.fx_used.eur_try.toFixed(2)}</p>
                  </div>
                  <div>
                    <p className="text-[10px] font-bold uppercase tracking-widest text-r2v-charcoal/50 mb-2">USD/TRY (TCMB)</p>
                    <p className="text-3xl font-mono font-light text-r2v-charcoal">{result.fx_used.usd_try.toFixed(2)}</p>
                  </div>
                </div>

                <div>
                  <p className="text-[10px] font-bold uppercase tracking-widest text-r2v-charcoal/50 mb-2">Toplam CO₂</p>
                  <p className="text-3xl font-mono font-light text-r2v-charcoal">
                    {result.co2_kg.toLocaleString('tr-TR', { maximumFractionDigits: 1 })} <span className="text-base">kg</span>
                  </p>
                </div>

                {result.match_results.length > 0 && (
                  <div>
                    <h3 className="text-[10px] font-bold uppercase tracking-widest text-r2v-charcoal/50 mb-4 flex items-center justify-between border-b border-r2v-charcoal/10 pb-2">
                      <span>Alıcı Eşleşmeleri</span>
                      <span className="text-[10px] text-r2v-terracotta border border-r2v-terracotta/30 px-2 py-0.5 rounded-full">
                        {COUNTRY_LABELS[request.target_country] ?? request.target_country}
                      </span>
                    </h3>
                    <div className="space-y-0">
                      {result.match_results.slice(0, 5).map((m) => (
                        <div key={m.buyer} className="py-4 border-b border-r2v-charcoal/5 flex items-center justify-between group">
                          <div>
                            <p className="text-base font-bold text-r2v-charcoal group-hover:text-r2v-terracotta transition-colors">{m.buyer}</p>
                            <p className="text-xs text-r2v-charcoal/50 font-mono mt-1">{m.processor}</p>
                          </div>
                          <div className="text-right">
                            <p className={`text-xl font-mono font-light ${m.score >= 0.8 ? 'text-r2v-green' : 'text-r2v-charcoal'}`}>
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
                    <h3 className="text-[10px] font-bold uppercase tracking-widest text-r2v-charcoal/50 mb-4 border-b border-r2v-charcoal/10 pb-2">
                      Karar Gerekçeleri
                    </h3>
                    <div className="space-y-4">
                      {result.reason_codes.slice(0, 3).map((r, i) => (
                        <div key={i} className="flex gap-3">
                          <span className="text-r2v-charcoal/30 font-mono text-sm shrink-0">0{i + 1}</span>
                          <p className="text-sm text-r2v-charcoal/80">{r.text}</p>
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
