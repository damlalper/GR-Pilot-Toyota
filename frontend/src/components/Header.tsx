import { Car, Activity, Cpu } from 'lucide-react';

export function Header() {
  return (
    <header className="glass border-b border-white/10">
      <div className="container mx-auto px-4 py-3">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-toyota-red to-red-700 flex items-center justify-center glow-red">
              <Car className="w-7 h-7 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-white tracking-tight">
                GR-<span className="text-toyota-red">Pilot</span>
              </h1>
              <p className="text-xs text-gray-400">Toyota GR Cup Series Analytics</p>
            </div>
          </div>

          {/* Status Indicators */}
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-green-500/10 border border-green-500/30">
              <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
              <span className="text-xs text-green-400 font-medium">Live Data</span>
            </div>

            <div className="hidden md:flex items-center gap-4 text-gray-400">
              <div className="flex items-center gap-1.5">
                <Activity className="w-4 h-4" />
                <span className="text-xs">Telemetry</span>
              </div>
              <div className="flex items-center gap-1.5">
                <Cpu className="w-4 h-4" />
                <span className="text-xs">AI Analysis</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Racing stripe accent */}
      <div className="h-1 bg-gradient-to-r from-transparent via-toyota-red to-transparent opacity-50" />
    </header>
  );
}
