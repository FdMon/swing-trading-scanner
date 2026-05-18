import fs from 'fs';
import path from 'path';
import DashboardClient from '@/components/DashboardClient';

export default function Home() {
  let data: any[] = [];
  try {
    const dataPath = path.join(process.cwd(), 'public', 'data', 'opportunities.json');
    if (fs.existsSync(dataPath)) {
      data = JSON.parse(fs.readFileSync(dataPath, 'utf8'));
    }
  } catch (error) {
    console.error("Error reading data:", error);
  }

  return (
    <main className="min-h-screen bg-slate-950 text-slate-50 p-8 font-sans">
      <div className="max-w-7xl mx-auto space-y-8">
        
        {/* Header */}
        <header className="flex justify-between items-center pb-6 border-b border-slate-800">
          <div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent">
              Swing Quant Scanner
            </h1>
            <p className="text-slate-400 mt-1">High probability breakout setups based on technical contraction.</p>
          </div>
          <div className="flex items-center space-x-2 bg-slate-900 px-4 py-2 rounded-full border border-slate-800 shadow-sm">
            <span className="relative flex h-3 w-3">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
            </span>
            <span className="text-sm font-medium text-slate-300">Live • Daily TF</span>
          </div>
        </header>

        {/* Dashboard Content (Client Side) */}
        <DashboardClient initialData={data} />

      </div>
    </main>
  );
}
