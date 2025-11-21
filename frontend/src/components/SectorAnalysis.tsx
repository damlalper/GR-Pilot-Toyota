import { useState, useEffect } from 'react';
import { useStore } from '../store/useStore';
import { fetchSectors } from '../api';
import { Timer, Loader2, TrendingUp, TrendingDown, Minus } from 'lucide-react';

interface SectorData {
  lap: number;
  total_time: number;
  sectors: Array<{
    sector: number;
    time: number;
    best_time: number;
    delta: number;
    status: string;
    speed_avg: number;
    speed_max: number;
    distance: { start: number; end: number };
  }>;
  best_sector_times: number[];
  theoretical_best: number;
  potential_gain: number;
}

export function SectorAnalysis() {
  const { currentLap } = useStore();
  const [data, setData] = useState<SectorData | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (!currentLap) return;
    setIsLoading(true);
    fetchSectors(currentLap)
      .then(setData)
      .catch(console.error)
      .finally(() => setIsLoading(false));
  }, [currentLap]);

  if (isLoading) {
    return (
      <div className="glass rounded-xl p-4 flex items-center justify-center h-48">
        <Loader2 className="w-6 h-6 animate-spin text-toyota-red" />
      </div>
    );
  }

  if (!data) return null;

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'faster': return <TrendingUp className="w-4 h-4 text-green-400" />;
      case 'slower': return <TrendingDown className="w-4 h-4 text-red-400" />;
      default: return <Minus className="w-4 h-4 text-yellow-400" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'faster': return 'bg-green-500';
      case 'slower': return 'bg-red-500';
      default: return 'bg-yellow-500';
    }
  };

  return (
    <div className="glass rounded-xl p-4">
      <div className="flex items-center gap-2 mb-4">
        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center">
          <Timer className="w-5 h-5 text-white" />
        </div>
        <div>
          <h3 className="font-medium text-white">Sector Analysis</h3>
          <p className="text-xs text-gray-400">Time gain/loss breakdown</p>
        </div>
      </div>

      {/* Lap Time Summary */}
      <div className="grid grid-cols-3 gap-2 mb-4">
        <div className="p-2 rounded-lg bg-white/5 text-center">
          <div className="text-lg font-bold text-white">{data.total_time.toFixed(2)}s</div>
          <div className="text-xs text-gray-500">Lap Time</div>
        </div>
        <div className="p-2 rounded-lg bg-white/5 text-center">
          <div className="text-lg font-bold text-purple-400">{data.theoretical_best.toFixed(2)}s</div>
          <div className="text-xs text-gray-500">Theoretical</div>
        </div>
        <div className="p-2 rounded-lg bg-white/5 text-center">
          <div className="text-lg font-bold text-green-400">-{data.potential_gain.toFixed(2)}s</div>
          <div className="text-xs text-gray-500">Potential</div>
        </div>
      </div>

      {/* Sector Bars */}
      <div className="space-y-3">
        {data.sectors.map((sector) => (
          <div key={sector.sector} className="space-y-1">
            <div className="flex items-center justify-between text-sm">
              <div className="flex items-center gap-2">
                <span className="text-gray-400">S{sector.sector}</span>
                {getStatusIcon(sector.status)}
              </div>
              <div className="flex items-center gap-3">
                <span className="text-white font-mono">{sector.time.toFixed(2)}s</span>
                <span className={`text-xs font-mono ${sector.delta > 0 ? 'text-red-400' : 'text-green-400'}`}>
                  {sector.delta > 0 ? '+' : ''}{sector.delta.toFixed(2)}s
                </span>
              </div>
            </div>
            <div className="h-2 bg-white/10 rounded-full overflow-hidden">
              <div
                className={`h-full ${getStatusColor(sector.status)} transition-all duration-500`}
                style={{ width: `${Math.min(100, (sector.best_time / sector.time) * 100)}%` }}
              />
            </div>
            <div className="flex justify-between text-xs text-gray-500">
              <span>Avg: {sector.speed_avg.toFixed(0)} km/h</span>
              <span>Max: {sector.speed_max.toFixed(0)} km/h</span>
            </div>
          </div>
        ))}
      </div>

      {/* Best Sector Times */}
      <div className="mt-4 pt-3 border-t border-white/10">
        <p className="text-xs text-gray-400 mb-2">Best Sector Times (All Laps)</p>
        <div className="flex gap-2">
          {data.best_sector_times.map((time, i) => (
            <div key={i} className="flex-1 p-2 rounded bg-purple-500/20 text-center">
              <div className="text-xs text-purple-400">S{i + 1}</div>
              <div className="text-sm font-mono text-white">{time.toFixed(2)}s</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
