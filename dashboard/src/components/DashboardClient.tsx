"use client";

import React, { useState, useEffect } from 'react';
import { ShieldCheck, TrendingUp, Activity, BarChart2, Heart, Star, Sparkles, Info, Bell, Lock, Settings } from 'lucide-react';
import StockChart from './StockChart';

interface Opportunity {
  ticker: string;
  index: string;
  score: number;
  pattern: string;
  price: number | null;
  ema_alignment: boolean;
  volume_score: number;
  atr_compression: number;
  history: any[];
  resistance_level?: number;
  entry_price?: number;
  take_profit?: number;
}

// Helper to hash password on the client side using Web Crypto API
async function sha256(message: string): Promise<string> {
  const msgBuffer = new TextEncoder().encode(message);
  const hashBuffer = await crypto.subtle.digest('SHA-256', msgBuffer);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
  return hashHex;
}

// Target hash for password "trading2026"
const PASSWORD_HASH = "5cfb13b4f090f3a96a25ff85ec2801211d97c7e06e502385785e1f51411150ca";

export default function DashboardClient({ initialData }: { initialData: Opportunity[] }) {
  const [favorites, setFavorites] = useState<Opportunity[]>([]);
  const [mounted, setMounted] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [passwordInput, setPasswordInput] = useState('');
  const [loginError, setLoginError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [activeTab, setActiveTab] = useState<'all' | 'favorites'>('all');
  const [jsonBinKey, setJsonBinKey] = useState('');
  const [showSettings, setShowSettings] = useState(false);
  const [isSyncing, setIsSyncing] = useState(false);

  const JSONBIN_BIN_ID = "6a10dc0c6610dd3ae88d7b1d";

  useEffect(() => {
    setMounted(true);
    
    // Check if session is already authenticated
    const authSession = localStorage.getItem('swing-scanner-auth');
    if (authSession === 'true') {
      setIsAuthenticated(true);
    }

    const storedKey = localStorage.getItem('swing-scanner-jsonbin-key');
    if (storedKey) {
      setJsonBinKey(storedKey);
    }

    const fetchFavorites = async () => {
      try {
        const headers: HeadersInit = {};
        if (storedKey) {
          headers['X-Access-Key'] = storedKey;
        }
        
        const res = await fetch(`https://api.jsonbin.io/v3/b/${JSONBIN_BIN_ID}/latest`, { headers });
        if (res.ok) {
          const data = await res.json();
          const storedFavs: Opportunity[] = data.record?.favorites || [];
          
          const syncedFavs = storedFavs.map(fav => {
            const freshData = initialData.find(d => d.ticker === fav.ticker);
            if (freshData) {
              return {
                ...fav,
                price: freshData.price,
                history: freshData.history,
                score: freshData.score
              };
            }
            return fav;
          });
          setFavorites(syncedFavs);
        }
      } catch (err) {
        console.error("Error fetching favorites from JSONBin", err);
      }
    };

    fetchFavorites();
  }, [initialData]);

  const toggleFavorite = async (opp: Opportunity) => {
    if (!jsonBinKey) {
      alert("Por favor, configura tu API Key de JSONBin en la sección de Ajustes para guardar favoritos.");
      setShowSettings(true);
      return;
    }

    const isAlreadyFav = favorites.some(f => f.ticker === opp.ticker);
    let newFavorites: Opportunity[];

    if (isAlreadyFav) {
      newFavorites = favorites.filter(f => f.ticker !== opp.ticker);
    } else {
      newFavorites = [...favorites, opp];
    }
    
    setFavorites(newFavorites);
    setIsSyncing(true);

    try {
      await fetch(`https://api.jsonbin.io/v3/b/${JSONBIN_BIN_ID}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'X-Access-Key': jsonBinKey
        },
        body: JSON.stringify({ favorites: newFavorites })
      });
    } catch (err) {
      console.error("Error saving favorites to JSONBin", err);
    } finally {
      setIsSyncing(false);
    }
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setLoginError('');
    try {
      const hashed = await sha256(passwordInput);
      if (hashed === PASSWORD_HASH) {
        setIsAuthenticated(true);
        localStorage.setItem('swing-scanner-auth', 'true');
      } else {
        setLoginError('Contraseña incorrecta. Inténtalo de nuevo.');
      }
    } catch (err) {
      setLoginError('Error al validar la contraseña.');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!mounted) return null;

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center p-4">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,rgba(16,185,129,0.08),transparent_70%)] pointer-events-none" />
        <div className="w-full max-w-md bg-slate-900/80 backdrop-blur-xl border border-slate-800 p-8 rounded-2xl shadow-2xl relative z-10 animate-in fade-in zoom-in duration-500">
          <div className="text-center mb-8">
            <div className="w-16 h-16 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center mx-auto mb-4 shadow-[0_0_20px_rgba(16,185,129,0.1)]">
              <Lock className="text-emerald-400" size={28} />
            </div>
            <h1 className="text-2xl font-black tracking-tight text-slate-100">Swing Scanner Access</h1>
            <p className="text-slate-400 text-sm mt-2 font-medium">Introduce la contraseña para acceder al panel de control técnico</p>
          </div>

          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Contraseña</label>
              <input
                type="password"
                value={passwordInput}
                onChange={(e) => setPasswordInput(e.target.value)}
                placeholder="••••••••"
                className="w-full bg-slate-950 border border-slate-800 focus:border-emerald-500/50 focus:ring-1 focus:ring-emerald-500/30 rounded-xl px-4 py-3 text-slate-100 placeholder-slate-600 outline-none transition-all font-sans"
                required
              />
            </div>

            {loginError && (
              <p className="text-rose-400 text-xs font-semibold bg-rose-500/10 border border-rose-500/20 p-3 rounded-lg">
                {loginError}
              </p>
            )}

            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full bg-emerald-500 hover:bg-emerald-400 disabled:opacity-50 text-slate-950 font-bold py-3 px-4 rounded-xl transition-all shadow-[0_4px_20px_rgba(16,185,129,0.2)] hover:shadow-[0_4px_25px_rgba(16,185,129,0.3)] flex items-center justify-center"
            >
              {isSubmitting ? 'Validando...' : 'Acceder al Panel'}
            </button>
          </form>
          
          <div className="text-center mt-6">
            <span className="text-[10px] text-slate-600 font-bold uppercase tracking-widest">
              Swing Trading Technical Scanner v2.0
            </span>
          </div>
        </div>
      </div>
    );
  }


  const renderCard = (opp: Opportunity, idx: number) => {
    const isBreakout = opp.price && opp.resistance_level && opp.price >= opp.resistance_level;
    
    return (
      <div key={opp.ticker + idx} className={`bg-slate-900 rounded-xl border transition-all duration-500 shadow-lg relative group ${
        isBreakout 
        ? "border-emerald-500/60 ring-1 ring-emerald-500/30 shadow-[0_0_25px_rgba(16,185,129,0.15)] bg-emerald-500/[0.02]" 
        : "border-slate-800 hover:border-emerald-500/50"
      }`}>
        <div className="p-6 pb-4">
        <div className="flex justify-between items-start mb-4">
          <div className="flex-1">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center space-x-3">
                <a 
                  href={`https://finance.yahoo.com/quote/${opp.ticker}`} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="hover:text-emerald-400 transition-colors cursor-pointer"
                >
                  <h3 className="text-3xl font-black tracking-tighter">{opp.ticker}</h3>
                </a>
                
                <div className="flex items-center space-x-2">
                  <a 
                    href={`https://www.google.com/search?aep=11&udm=50&q=Analiza+${opp.ticker}+90+dias+triangulo+alcista+resistencia+${opp.resistance_level}+objetivo+${opp.take_profit}+precio+${opp.price}.+Comprueba+la+evolucion+del+grafico+para+contrastar+los+datos.+Primero+da+una+tabla+con+entrada+stop+riesgo+por+accion+beneficio+proyeccion+RR+nitidez+grafico+volatilidad+base+pct+perdida+stop+y+pct+ganancia+target.+Despues+da+un+informe+detallado+con:+1.Estructura+del+Grafico+y+Dinamica+de+Precios+2.Gestion+de+Riesgos+y+Puntos+Criticos+3.Viabilidad+de+la+Proyeccion+4.Descripcion+de+la+actividad+de+la+empresa.`} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="p-1 px-2 rounded-md bg-slate-800 text-cyan-400 hover:bg-cyan-400/10 transition-all border border-slate-700/50 flex items-center space-x-1 shadow-sm group/ai"
                    title="AI Analysis"
                  >
                    <Sparkles size={12} className="group-hover/ai:rotate-12 transition-transform" />
                    <span className="text-[10px] font-black tracking-tighter">AI</span>
                  </a>
                  
                  <div className="bg-slate-950 border border-slate-700 rounded-full px-2 py-0.5 flex items-center space-x-1">
                    <ShieldCheck size={12} className={opp.score >= 85 ? "text-emerald-400" : "text-amber-400"} />
                    <span className="font-bold text-[10px]">{opp.score}%</span>
                  </div>
                </div>
              </div>
              
              <div className="text-right">
                <p className={`text-2xl font-black tracking-tighter ${isBreakout ? 'text-emerald-400 drop-shadow-[0_0_8px_rgba(16,185,129,0.5)] animate-[pulse_1s_infinite]' : 'text-slate-100'}`}>
                  ${opp.price?.toFixed(2) ?? 'N/A'}
                </p>
                {isBreakout && (
                  <div className="flex items-center justify-end text-[10px] font-black text-emerald-400 animate-[pulse_1s_infinite] mt-1 uppercase tracking-tighter">
                    <Bell size={10} className="mr-1 fill-emerald-400" />
                    Breakout Detected
                  </div>
                )}
              </div>
            </div>
            
            <div className="flex items-center space-x-3">
              {opp.index && (
                <span className="text-[10px] font-bold text-slate-500 bg-slate-800/30 px-2 py-0.5 rounded border border-slate-800/50 uppercase tracking-widest">
                  {opp.index}
                </span>
              )}
              <button 
                onClick={() => toggleFavorite(opp)}
                className="text-slate-500 hover:text-rose-500 transition-colors p-1 rounded-full hover:bg-slate-800"
              >
                <Heart 
                  size={16} 
                  className={favorites.some(f => f.ticker === opp.ticker) ? "fill-rose-500 text-rose-500" : ""} 
                />
              </button>
            </div>
          </div>
        </div>

        {/* Micro Breakdown */}
        <div className="space-y-3 mt-6">
          <div className="flex justify-between items-center text-sm group/tip relative">
            <span className="text-slate-400 flex items-center cursor-help">
              <Activity size={14} className="mr-1"/> Trend Alignment
              <Info size={10} className="ml-1 text-slate-600" />
            </span>
            <div className="absolute left-0 -top-12 bg-slate-800 text-[10px] text-slate-200 p-2 rounded border border-slate-700 w-48 hidden group-hover/tip:block z-50 shadow-2xl">
              Confirma que el precio y las medias móviles (EMA 20/50/200) están en una estructura alcista clara.
            </div>
            {opp.ema_alignment ? 
              <span className="text-emerald-400 font-medium bg-emerald-400/10 px-2 py-0.5 rounded text-xs">Perfect</span> : 
              <span className="text-amber-400 font-medium bg-amber-400/10 px-2 py-0.5 rounded text-xs">Mixed</span>}
          </div>
          <div className="flex justify-between items-center text-sm group/tip relative">
            <span className="text-slate-400 flex items-center cursor-help">
              <BarChart2 size={14} className="mr-1"/> Vol Contraction
              <Info size={10} className="ml-1 text-slate-600" />
            </span>
            <div className="absolute left-0 -top-12 bg-slate-800 text-[10px] text-slate-200 p-2 rounded border border-slate-700 w-48 hidden group-hover/tip:block z-50 shadow-2xl">
              Indica si el volumen ha disminuido durante la consolidación, señal de que la presión vendedora se agota.
            </div>
            <span className="font-medium">{opp.volume_score > 0 ? 'Yes' : 'No'}</span>
          </div>
          <div className="flex justify-between items-center text-sm group/tip relative">
            <span className="text-slate-400 flex items-center cursor-help">
              ATR Compression
              <Info size={10} className="ml-1 text-slate-600" />
            </span>
            <div className="absolute left-0 -top-14 bg-slate-800 text-[10px] text-slate-200 p-2 rounded border border-slate-700 w-48 hidden group-hover/tip:block z-50 shadow-2xl">
              Mide la reducción de volatilidad. Un valor bajo (&lt;5%) indica que el precio está muy apretado y listo para explotar.
            </div>
            <span className="font-medium text-cyan-400">{opp.atr_compression}%</span>
          </div>
          <div className="pt-2 border-t border-slate-800/50 flex justify-between items-center">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Breakout Level</span>
            <span className="text-sm font-black text-emerald-400 bg-emerald-400/10 px-2 py-0.5 rounded border border-emerald-500/20">
              ${opp.resistance_level?.toFixed(2) ?? '---'}
            </span>
          </div>
          <div className="flex justify-between items-center text-xs font-medium">
            <span className="text-slate-500 uppercase tracking-wider">Target Projection</span>
            <div className="flex items-center space-x-2">
              <span className="text-cyan-400 font-bold">${opp.take_profit?.toFixed(2) ?? '---'}</span>
              {opp.take_profit && opp.resistance_level && (
                <span className="text-[10px] text-emerald-500 bg-emerald-500/5 px-1 rounded">
                  (+{((opp.take_profit / opp.resistance_level - 1) * 100).toFixed(1)}%)
                </span>
              )}
            </div>
          </div>
        </div>
      </div>
      
      {/* Chart */}
      <div className="h-56 w-full bg-slate-950/50 border-t border-slate-800 p-2 opacity-80 group-hover:opacity-100 transition-opacity duration-300">
        <StockChart data={opp.history} ticker={opp.ticker} price={opp.price} />
      </div>
    </div>
    );
  };

  const favoriteOpps = favorites;
  const otherOpps = initialData.filter(opp => !favorites.some(f => f.ticker === opp.ticker));

  return (
    <div className="space-y-6">
      {/* Tab Switcher + Settings */}
      <div className="flex items-center justify-between">
        <div className="flex space-x-1 bg-slate-900/50 p-1 rounded-xl border border-slate-800 w-fit">
          <button
            onClick={() => setActiveTab('all')}
            className={`flex items-center px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              activeTab === 'all' 
              ? "bg-slate-800 text-emerald-400 shadow-sm" 
              : "text-slate-400 hover:text-slate-200"
            }`}
          >
            <TrendingUp size={16} className="mr-2" />
            All Opportunities
            <span className="ml-2 bg-slate-950 px-1.5 py-0.5 rounded text-[10px] text-slate-500">
              {initialData.length}
            </span>
          </button>
          <button
            onClick={() => setActiveTab('favorites')}
            className={`flex items-center px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              activeTab === 'favorites' 
              ? "bg-slate-800 text-rose-400 shadow-sm" 
              : "text-slate-400 hover:text-slate-200"
            }`}
          >
            <Heart size={16} className={`mr-2 ${activeTab === 'favorites' ? 'fill-rose-400' : ''}`} />
            My Watchlist
            <span className="ml-2 bg-slate-950 px-1.5 py-0.5 rounded text-[10px] text-slate-500">
              {favorites.length}
            </span>
          </button>
        </div>

        <div className="flex items-center space-x-2">
          {isSyncing && (
            <span className="text-xs text-slate-400 animate-pulse flex items-center">
              <Activity size={12} className="mr-1" /> Sincronizando...
            </span>
          )}
          <button
            onClick={() => setShowSettings(!showSettings)}
            className="text-slate-500 hover:text-slate-300 p-2 rounded-lg hover:bg-slate-800 transition-colors"
            title="Cloud Sync Settings"
          >
            <Settings size={18} />
          </button>
        </div>
      </div>

      {showSettings && (
        <div className="bg-slate-900/80 backdrop-blur border border-slate-800 p-6 rounded-xl shadow-lg mb-6 animate-in fade-in slide-in-from-top-2">
          <h3 className="text-sm font-bold text-slate-200 mb-2 flex items-center">
            <Lock size={14} className="mr-2 text-emerald-400" />
            Configuración de Sincronización en la Nube
          </h3>
          <p className="text-xs text-slate-400 mb-4 max-w-2xl">
            Para que tus favoritos se guarden en la nube y se sincronicen en todos tus dispositivos, pega aquí tu API Key de JSONBin. Solo tendrás que hacerlo una vez por dispositivo.
          </p>
          <div className="flex space-x-3">
            <input
              type="password"
              value={jsonBinKey}
              onChange={(e) => setJsonBinKey(e.target.value)}
              placeholder="Ej: $2a$10$v/m4qo..."
              className="flex-1 bg-slate-950 border border-slate-800 rounded-lg px-4 py-2 text-sm text-slate-100 focus:border-emerald-500/50 outline-none font-mono"
            />
            <button
              onClick={() => {
                localStorage.setItem('swing-scanner-jsonbin-key', jsonBinKey);
                alert("Clave guardada en este dispositivo.");
                setShowSettings(false);
              }}
              className="bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-4 py-2 rounded-lg text-sm font-bold hover:bg-emerald-500/20 transition-colors"
            >
              Guardar Clave
            </button>
          </div>
        </div>
      )}

      {/* Grid Content */}
      <section className="pt-2">
        {activeTab === 'favorites' ? (
          favorites.length === 0 ? (
            <div className="bg-slate-900 border border-slate-800 p-12 rounded-xl text-center w-full animate-in fade-in zoom-in duration-300">
              <div className="bg-slate-950 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4 border border-slate-800">
                <Heart size={32} className="text-slate-700" />
              </div>
              <p className="text-slate-400 text-lg font-medium">Your watchlist is empty</p>
              <p className="text-slate-500 text-sm mt-2 max-w-xs mx-auto">
                Mark opportunities with a heart to track them separately. They will stay here even if the scanner score changes.
              </p>
              <button 
                onClick={() => setActiveTab('all')}
                className="mt-6 text-emerald-400 text-sm font-semibold hover:underline"
              >
                Browse all opportunities
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
              {favorites.map(renderCard)}
            </div>
          )
        ) : (
          initialData.length === 0 ? (
            <div className="bg-slate-900 border border-slate-800 p-8 rounded-xl text-center w-full">
              <p className="text-slate-400 text-lg">No breakout opportunities found matching the criteria.</p>
              <p className="text-slate-500 text-sm mt-2">The scanner runs daily. Conditions for high probability setups might not be met right now.</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
              {initialData.map(renderCard)}
            </div>
          )
        )}
      </section>
    </div>
  );
}
