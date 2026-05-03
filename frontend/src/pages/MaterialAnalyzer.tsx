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
      <label className="text-[10px] font-bold text-r2v-charcoal/50 uppercase tracking-widest block mb-2">{label}</label>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value as T)}
        className="w-full bg-transparent border-b-2 border-r2v-charcoal/10 focus:border-r2v-charcoal pb-2 text-lg font-light text-r2v-charcoal outline-none cursor-pointer appearance-none"
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
      <label className="text-[10px] font-bold text-r2v-charcoal/50 uppercase tracking-widest block mb-2">{label}</label>
      <div className="flex items-center border-b-2 border-r2v-charcoal/10 focus-within:border-r2v-charcoal transition-colors pb-2">
        <input
          type={type}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          className="w-full bg-transparent border-none focus:ring-0 p-0 text-lg font-light text-r2v-charcoal placeholder:text-r2v-charcoal/20 outline-none"
        />
        {suffix && <span className="text-xs font-bold text-r2v-charcoal/30 uppercase tracking-widest ml-2">{suffix}</span>}
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
    <div className="max-w-7xl mx-auto space-y-12 pb-12">
      {/* Header */}
      <div className="border-b border-r2v-charcoal/20 pb-6 mb-12 flex justify-between items-end">
        <div>
          <h1 className="text-4xl font-bold tracking-tight text-r2v-charcoal mb-2">Material Analyzer</h1>
          <p className="text-base text-r2v-charcoal/60 font-normal">Hammadde ve rota bilgilerini girerek AI analizini başlatın.</p>
        </div>
        <div className="hidden md:flex items-center gap-2 text-[10px] font-bold uppercase tracking-widest text-r2v-charcoal/40">
          <FlaskConical className="w-4 h-4" /> Lab Modülü Aktif
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-16">

        {/* COLUMN 1: Hammadde & Menşei */}
        <div className="lg:col-span-4">
          <h3 className="text-sm font-bold text-r2v-charcoal uppercase tracking-widest mb-8 flex items-center gap-2">
            <MapPin className="w-4 h-4" /> Menşei ve Hammadde
          </h3>

          <Select label="Hammadde Tipi" value={rawMaterial} options={MATERIAL_LABELS} onChange={setRawMaterial} />
          <TextInput label="Menşei Şehir" value={originCity} onChange={setOriginCity} placeholder="Örn: Nevşehir" />
          <TextInput label="Parti Tonajı" value={tonnage} onChange={setTonnage} type="number" suffix="TON" placeholder="100" />
          <Select label="Kalite Sınıfı" value={quality} options={QUALITY_LABELS} onChange={setQuality} />
        </div>

        {/* COLUMN 2: Lojistik & Öncelik */}
        <div className="lg:col-span-4 md:border-l border-r2v-charcoal/10 md:pl-8">
          <h3 className="text-sm font-bold text-r2v-charcoal uppercase tracking-widest mb-8 flex items-center gap-2">
            <Package className="w-4 h-4" /> Lojistik ve Hedef
          </h3>

          <Select label="Hedef Ülke" value={targetCountry} options={COUNTRY_LABELS} onChange={setTargetCountry} />
          <Select label="Taşıma Modu" value={transportMode} options={TRANSPORT_LABELS} onChange={setTransportMode} />
          <Select label="Optimizasyon Önceliği" value={priority} options={PRIORITY_LABELS} onChange={setPriority} />

          <div className="pt-4 mt-4 border-t border-r2v-charcoal/10">
            <h4 className="text-[10px] font-bold text-r2v-charcoal/40 uppercase tracking-widest mb-6">Fiziksel Parametreler (Opsiyonel)</h4>
            <TextInput label="Nem Oranı" value={moisturePct} onChange={setMoisturePct} type="number" suffix="%" placeholder="12" />
            <TextInput label="Saflık Oranı" value={purityPct} onChange={setPurityPct} type="number" suffix="%" placeholder="95" />
            <TextInput label="Tane Boyutu Sınıfı" value={particleSizeClass} onChange={setParticleSizeClass} placeholder="Örn: mikronize, 0-5mm" />
          </div>
        </div>

        {/* COLUMN 3: Lab Raporu & Aksiyon */}
        <div className="lg:col-span-4 md:border-l border-r2v-charcoal/10 md:pl-8 flex flex-col h-full">
          <h3 className="text-sm font-bold text-r2v-charcoal uppercase tracking-widest mb-8">
            Laboratuvar Raporu
          </h3>

          <div className="flex-1">
            <div
              onClick={!uploaded && !isUploading ? handleUpload : undefined}
              className={`w-full aspect-square md:aspect-auto md:h-64 flex flex-col items-center justify-center border-2 border-dashed transition-all cursor-pointer ${
                uploaded
                  ? 'border-r2v-green bg-r2v-green/5'
                  : isUploading
                  ? 'border-r2v-charcoal/30 bg-white/50'
                  : 'border-r2v-charcoal/20 bg-white/30 hover:border-r2v-charcoal/50 hover:bg-white/60'
              }`}
            >
              {uploaded ? (
                <>
                  <FileCheck2 className="w-12 h-12 text-r2v-green mb-4" />
                  <p className="text-sm font-bold text-r2v-charcoal uppercase tracking-widest">Rapor Yüklendi</p>
                  <p className="text-[10px] font-mono text-r2v-charcoal/50 mt-2">NVSHR-LAB-042.pdf</p>
                </>
              ) : isUploading ? (
                <>
                  <div className="w-8 h-8 border-2 border-r2v-charcoal border-t-transparent rounded-full animate-spin mb-4"></div>
                  <p className="text-xs font-bold text-r2v-charcoal uppercase tracking-widest animate-pulse">İşleniyor...</p>
                </>
              ) : (
                <>
                  <UploadCloud className="w-10 h-10 text-r2v-charcoal/30 mb-4" />
                  <p className="text-xs font-bold text-r2v-charcoal uppercase tracking-widest text-center px-6">
                    PDF Analiz Raporunu Sürükleyin
                  </p>
                  <p className="text-[10px] text-r2v-charcoal/40 font-bold tracking-widest uppercase mt-4">veya tıklayıp seçin</p>
                </>
              )}
            </div>
          </div>

          {error && (
            <div className="mt-6 p-4 bg-r2v-terracotta/10 border border-r2v-terracotta/30 text-sm text-r2v-terracotta font-medium">
              {error}
            </div>
          )}

          <div className="mt-8">
            <button
              onClick={handleAnalyze}
              disabled={isAnalyzing}
              className="w-full bg-r2v-charcoal text-white h-16 flex items-center justify-center gap-3 hover:bg-r2v-charcoal/90 transition-colors disabled:opacity-70"
            >
              {isAnalyzing ? (
                <span className="text-xs font-bold uppercase tracking-widest flex items-center gap-2">
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  AI Modeli Çalışıyor...
                </span>
              ) : (
                <>
                  <span className="text-xs font-bold uppercase tracking-widest">Analizi Başlat ve Rota Çıkar</span>
                  <ChevronRight className="w-4 h-4" />
                </>
              )}
            </button>
            <p className="text-[10px] font-mono text-center text-r2v-charcoal/40 mt-4">
              *Değer artışı, rota önerisi ve alıcı eşleşmesi için 3 AI modeli çalışır.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
