import { useState } from 'react';
import { FlaskConical, UploadCloud, FileCheck2, ChevronRight, MapPin, Package } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { analyze, ApiError } from '../lib/api';
import { useAnalysis } from '../contexts/AnalysisContext';
import type { AnalyzeRequest, RawMaterial, Quality, TransportMode, TargetCountry, Priority } from '../lib/types';

const MATERIAL_LABELS: Record<RawMaterial, string> = {
  pomza: 'Pomza (Pumice)',
  perlit: 'Perlit',
  kabak_cekirdegi: 'Kabak Çekirdeği',
};

const QUALITY_LABELS: Record<Quality, string> = {
  A: 'A Sınıfı (Yüksek)',
  B: 'B Sınıfı (Orta)',
  C: 'C Sınıfı (Düşük)',
  unknown: 'Bilinmiyor',
};

const TRANSPORT_LABELS: Record<TransportMode, string> = {
  kara: 'Karayolu',
  deniz: 'Denizyolu',
  demiryolu: 'Demiryolu',
  hava: 'Havayolu',
};

const COUNTRY_LABELS: Record<TargetCountry, string> = {
  TR: 'Türkiye (İç Pazar)',
  DE: 'Almanya',
  NL: 'Hollanda',
};

const PRIORITY_LABELS: Record<Priority, string> = {
  max_profit: 'Maksimum Kâr',
  low_carbon: 'Düşük Karbon',
  fast_delivery: 'Hızlı Teslimat',
};

type SelectProps<T extends string> = {
  label: string;
  value: T;
  options: Record<T, string>;
  onChange: (v: T) => void;
};

function Select<T extends string>({ label, value, options, onChange }: SelectProps<T>) {
  return (
    <div className="mb-8">
      <label className="font-mono text-[11px] font-medium text-[#0a0a0a] uppercase tracking-widest block mb-2">{label}</label>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value as T)}
        className="w-full bg-transparent border-b-2 border-[#0a0a0a] focus:ring-0 pb-2 text-lg font-medium text-[#0a0a0a] outline-none cursor-pointer appearance-none"
      >
        {(Object.entries(options) as [T, string][]).map(([k, v]) => (
          <option key={k} value={k}>{v}</option>
        ))}
      </select>
    </div>
  );
}

function TextInput({ label, value, onChange, placeholder, type = 'text', suffix = '' }: {
  label: string; value: string | number; onChange: (v: string) => void;
  placeholder?: string; type?: string; suffix?: string;
}) {
  return (
    <div className="mb-8">
      <label className="font-mono text-[11px] font-medium text-[#0a0a0a] uppercase tracking-widest block mb-2">{label}</label>
      <div className="flex items-center border-b-2 border-[#0a0a0a] focus-within:border-[#1d4fd6] transition-colors pb-2">
        <input
          type={type}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          className="w-full bg-transparent border-none focus:ring-0 p-0 text-lg font-medium text-[#0a0a0a] placeholder:text-[#6b6b6b] outline-none"
        />
        {suffix && <span className="font-mono text-xs font-semibold text-[#6b6b6b] uppercase tracking-widest ml-2">{suffix}</span>}
      </div>
    </div>
  );
}

export default function MaterialAnalyzer() {
  const navigate = useNavigate();
  const { setAnalysis } = useAnalysis();

  const [rawMaterial, setRawMaterial] = useState<RawMaterial>('pomza');
  const [tonnage, setTonnage] = useState('100');
  const [quality, setQuality] = useState<Quality>('A');
  const [originCity, setOriginCity] = useState('Nevşehir');
  const [targetCountry, setTargetCountry] = useState<TargetCountry>('DE');
  const [transportMode, setTransportMode] = useState<TransportMode>('deniz');
  const [priority, setPriority] = useState<Priority>('max_profit');
  const [moisturePct, setMoisturePct] = useState('');
  const [purityPct, setPurityPct] = useState('');
  const [particleSizeClass, setParticleSizeClass] = useState('');

  const [isUploading, setIsUploading] = useState(false);
  const [uploaded, setUploaded] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleUpload = () => {
    setIsUploading(true);
    setTimeout(() => { setIsUploading(false); setUploaded(true); }, 1500);
  };

  const handleAnalyze = async () => {
    const t = parseFloat(tonnage);
    if (!originCity.trim()) { setError('Menşei şehir zorunludur.'); return; }
    if (isNaN(t) || t <= 0) { setError('Geçerli bir tonaj girin.'); return; }

    setError(null);
    setIsAnalyzing(true);

    const payload: AnalyzeRequest = {
      raw_material: rawMaterial,
      tonnage: t,
      quality,
      origin_city: originCity.trim(),
      target_country: targetCountry,
      transport_mode: transportMode,
      priority,
      input_mode: moisturePct || purityPct || particleSizeClass ? 'advanced' : 'basic',
      ...(moisturePct ? { moisture_pct: parseFloat(moisturePct) } : {}),
      ...(purityPct ? { purity_pct: parseFloat(purityPct) } : {}),
      ...(particleSizeClass ? { particle_size_class: particleSizeClass } : {}),
    };

    try {
      const result = await analyze(payload);
      setAnalysis(payload, result);
      navigate('/dashboard/cockpit');
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        setError('Oturum açmanız gerekiyor. Lütfen API token\'ınızı ayarlayın.');
      } else {
        setError(err instanceof Error ? err.message : 'Analiz sırasında hata oluştu.');
      }
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto space-y-12 pb-12 bg-white">
      {/* Header — Swiss eyebrow */}
      <div className="border-b-2 border-[#0a0a0a] pb-6 mb-12 flex justify-between items-end gap-6 flex-wrap">
        <div>
          <div className="flex items-center gap-4 mb-3">
            <span className="bg-[#d6342a] text-white text-xs font-semibold font-mono px-2.5 py-1 tracking-wider">01</span>
            <span className="font-mono text-sm font-medium tracking-wider text-[#0a0a0a]">Material Analyzer</span>
          </div>
          <h1 className="text-5xl md:text-6xl font-bold tracking-tightest text-[#0a0a0a] mb-3 leading-[0.96]">Hammadde Girişi.</h1>
          <p className="text-base text-[#2a2a2a] font-normal max-w-2xl">Hammadde ve rota bilgilerini girerek AI analizini başlatın.</p>
        </div>
        <div className="hidden md:flex items-center gap-2 font-mono text-xs font-medium uppercase tracking-widest text-[#6b6b6b]">
          <FlaskConical className="w-4 h-4" /> Lab Modülü Aktif
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-16">

        {/* COLUMN 1 */}
        <div className="lg:col-span-4">
          <h3 className="font-mono text-xs font-semibold text-[#0a0a0a] uppercase tracking-widest mb-8 flex items-center gap-2 pb-3 border-b border-[#0a0a0a]">
            <MapPin className="w-4 h-4 text-[#d6342a]" /> Menşei ve Hammadde
          </h3>

          <Select label="Hammadde Tipi" value={rawMaterial} options={MATERIAL_LABELS} onChange={setRawMaterial} />
          <TextInput label="Menşei Şehir" value={originCity} onChange={setOriginCity} placeholder="Örn: Nevşehir" />
          <TextInput label="Parti Tonajı" value={tonnage} onChange={setTonnage} type="number" suffix="TON" placeholder="100" />
          <Select label="Kalite Sınıfı" value={quality} options={QUALITY_LABELS} onChange={setQuality} />
        </div>

        {/* COLUMN 2 */}
        <div className="lg:col-span-4 lg:border-l-2 lg:border-[#0a0a0a] lg:pl-12">
          <h3 className="font-mono text-xs font-semibold text-[#0a0a0a] uppercase tracking-widest mb-8 flex items-center gap-2 pb-3 border-b border-[#0a0a0a]">
            <Package className="w-4 h-4 text-[#1d4fd6]" /> Lojistik ve Hedef
          </h3>

          <Select label="Hedef Ülke" value={targetCountry} options={COUNTRY_LABELS} onChange={setTargetCountry} />
          <Select label="Taşıma Modu" value={transportMode} options={TRANSPORT_LABELS} onChange={setTransportMode} />
          <Select label="Optimizasyon Önceliği" value={priority} options={PRIORITY_LABELS} onChange={setPriority} />

          <div className="pt-4 mt-4 border-t-2 border-[#0a0a0a]">
            <h4 className="font-mono text-[11px] font-medium text-[#6b6b6b] uppercase tracking-widest mb-6">Fiziksel Parametreler (Opsiyonel)</h4>
            <TextInput label="Nem Oranı" value={moisturePct} onChange={setMoisturePct} type="number" suffix="%" placeholder="12" />
            <TextInput label="Saflık Oranı" value={purityPct} onChange={setPurityPct} type="number" suffix="%" placeholder="95" />
            <TextInput label="Tane Boyutu Sınıfı" value={particleSizeClass} onChange={setParticleSizeClass} placeholder="Örn: mikronize, 0-5mm" />
          </div>
        </div>

        {/* COLUMN 3 */}
        <div className="lg:col-span-4 lg:border-l-2 lg:border-[#0a0a0a] lg:pl-12 flex flex-col">
          <h3 className="font-mono text-xs font-semibold text-[#0a0a0a] uppercase tracking-widest mb-8 pb-3 border-b border-[#0a0a0a]">
            Laboratuvar Raporu
          </h3>

          <div className="flex-1">
            <div
              onClick={!uploaded && !isUploading ? handleUpload : undefined}
              className={`w-full aspect-square md:aspect-auto md:h-64 flex flex-col items-center justify-center border-2 border-dashed transition-all cursor-pointer ${
                uploaded
                  ? 'border-[#1f7a3a] bg-white'
                  : isUploading
                  ? 'border-[#0a0a0a] bg-white'
                  : 'border-[#0a0a0a] bg-white hover:bg-[#f4f4f4]'
              }`}
            >
              {uploaded ? (
                <>
                  <FileCheck2 className="w-12 h-12 text-[#1f7a3a] mb-4" />
                  <p className="font-mono text-sm font-bold text-[#0a0a0a] uppercase tracking-widest">Rapor Yüklendi</p>
                  <p className="font-mono text-[10px] text-[#6b6b6b] mt-2 tracking-wide">NVSHR-LAB-042.pdf</p>
                </>
              ) : isUploading ? (
                <>
                  <div className="w-8 h-8 border-2 border-[#0a0a0a] border-t-transparent rounded-full animate-spin mb-4"></div>
                  <p className="font-mono text-xs font-bold text-[#0a0a0a] uppercase tracking-widest animate-pulse">İşleniyor...</p>
                </>
              ) : (
                <>
                  <UploadCloud className="w-10 h-10 text-[#0a0a0a] mb-4" />
                  <p className="font-mono text-xs font-bold text-[#0a0a0a] uppercase tracking-widest text-center px-6">
                    PDF Analiz Raporunu Sürükleyin
                  </p>
                  <p className="font-mono text-[10px] text-[#6b6b6b] font-medium tracking-widest uppercase mt-4">veya tıklayıp seçin</p>
                </>
              )}
            </div>
          </div>

          {error && (
            <div className="mt-6 p-4 bg-white border-2 border-[#d6342a] text-sm text-[#d6342a] font-medium">
              {error}
            </div>
          )}

          <div className="mt-8">
            <button
              onClick={handleAnalyze}
              disabled={isAnalyzing}
              className="w-full bg-[#0a0a0a] text-white h-16 flex items-center justify-center gap-3 hover:bg-[#d6342a] transition-colors disabled:opacity-70"
            >
              {isAnalyzing ? (
                <span className="font-mono text-xs font-medium uppercase tracking-widest flex items-center gap-2">
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  AI Modeli Çalışıyor...
                </span>
              ) : (
                <>
                  <span className="font-mono text-xs font-medium uppercase tracking-widest">Analizi Başlat ve Rota Çıkar</span>
                  <ChevronRight className="w-4 h-4" />
                </>
              )}
            </button>
            <p className="font-mono text-[10px] text-center text-[#6b6b6b] mt-4 tracking-wide">
              *Değer artışı, rota önerisi ve alıcı eşleşmesi için 3 AI modeli çalışır.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
