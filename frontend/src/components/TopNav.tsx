import { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Map, BarChart2, TrendingUp } from 'lucide-react';
import { api } from '../lib/api';
import { MOCK_FX } from '../lib/mockData';
import type { FxResponse } from '../lib/types';

export default function TopNav() {
  const location = useLocation();
  const [fx, setFx] = useState<FxResponse | null>(null);

  useEffect(() => {
    api.fxCurrent().then(setFx).catch(() => setFx(MOCK_FX));
  }, []);

  return (
    <header className="fixed top-0 left-0 right-0 z-50 h-16 bg-white border-b-2 border-[#0a0a0a] flex items-center px-6 gap-5">
      {/* Logo */}
      <Link to="/" className="flex items-center gap-3 shrink-0">
        <div className="grid grid-cols-2 grid-rows-2 w-7 h-7 border-2 border-[#0a0a0a]">
          <div className="bg-white" />
          <div className="bg-[#0a0a0a]" />
          <div className="bg-[#1d4fd6]" />
          <div className="bg-[#d6342a]" />
        </div>
        <span className="text-base font-bold tracking-tight text-[#0a0a0a]">
          Raw2Value <span className="font-normal text-[#6b6b6b]">AI</span>
        </span>
      </Link>

      {/* FX Widget — K2 canlı kur */}
      <div className="flex-1 flex justify-center">
        <div className="flex items-center gap-3 border border-[#0a0a0a] px-4 py-2 bg-white">
          <span className="font-mono text-[9px] font-bold text-white bg-[#1d4fd6] px-1.5 py-0.5 tracking-widest uppercase">K2</span>
          {fx ? (
            <>
              <span className="font-mono text-xs font-medium text-[#0a0a0a]">
                USD <span className="font-bold">{fx.usd_try.toFixed(2)}</span>
                {!fx.is_stale
                  ? <TrendingUp className="w-3 h-3 text-[#1f7a3a] inline ml-0.5" />
                  : <span className="text-[#c97a17] ml-0.5 text-[10px]">~</span>}
              </span>
              <span className="text-[#e6e6e6] select-none">·</span>
              <span className="font-mono text-xs font-medium text-[#0a0a0a]">
                EUR <span className="font-bold">{fx.eur_try.toFixed(2)}</span>
                {!fx.is_stale && <TrendingUp className="w-3 h-3 text-[#1f7a3a] inline ml-0.5" />}
              </span>
              <span className="text-[#e6e6e6] select-none">·</span>
              <span className={`font-mono text-[10px] font-semibold uppercase tracking-wider ${fx.is_stale ? 'text-[#c97a17]' : 'text-[#1f7a3a]'}`}>
                {fx.is_stale ? 'Fallback' : 'TCMB Canlı'}
              </span>
            </>
          ) : (
            <span className="font-mono text-xs text-[#6b6b6b] animate-pulse">Kur yükleniyor...</span>
          )}
        </div>
      </div>

      {/* Right: nav links + user */}
      <div className="flex items-center gap-3 shrink-0">
        <Link
          to="/dashboard"
          className={`flex items-center gap-1.5 px-4 py-2 text-xs font-mono uppercase tracking-widest font-medium transition-colors ${
            location.pathname === '/dashboard'
              ? 'bg-[#0a0a0a] text-white'
              : 'text-[#0a0a0a] hover:bg-[#f4f4f4] border border-[#0a0a0a]'
          }`}
        >
          <BarChart2 className="w-4 h-4" />
          <span className="hidden sm:inline">Cockpit</span>
        </Link>

        <Link
          to="/dashboard/geo"
          className={`flex items-center gap-1.5 px-4 py-2 text-xs font-mono uppercase tracking-widest font-medium transition-colors ${
            location.pathname === '/dashboard/geo'
              ? 'bg-[#0a0a0a] text-white'
              : 'text-[#0a0a0a] hover:bg-[#f4f4f4] border border-[#0a0a0a]'
          }`}
        >
          <Map className="w-4 h-4" />
          <span className="hidden sm:inline">GeoCarbon</span>
        </Link>

        <div className="h-6 w-px bg-[#0a0a0a]" />

        {/* Mehmet Amca profile */}
        <div className="flex items-center gap-2.5 cursor-pointer group">
          <div className="text-right hidden sm:block leading-tight">
            <p className="text-sm font-semibold text-[#0a0a0a] group-hover:text-[#d6342a] transition-colors">
              Mehmet Yılmaz
            </p>
            <p className="text-[10px] font-mono uppercase tracking-widest text-[#6b6b6b] font-medium">
              Doğa Pomza Ltd · Acıgöl
            </p>
          </div>
          <div className="w-9 h-9 bg-[#0a0a0a] text-white flex items-center justify-center font-mono text-sm font-bold">
            MY
          </div>
        </div>
      </div>
    </header>
  );
}
