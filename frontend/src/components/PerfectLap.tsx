import { useEffect, useState } from 'react';
import { Sparkles, Zap, TrendingDown, Loader2 } from 'lucide-react';
import { fetchPerfectLap } from '../api';
import { DatasetBadges } from './DatasetBadge';
import { ComponentExplanation } from './ComponentExplanation';

interface BestSector {
  time: number;
  vehicle: number;
  lap: number;
}

interface PerfectLapData {
  perfect_lap_time: number;
  best_sectors: {
    s1: BestSector;
    s2: BestSector;
    s3: BestSector;
  };
  actual_best_lap: number;
  improvement_potential: number;
}

export default function PerfectLap() {
  const [data, setData] = useState<PerfectLapData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      try {
        // Pass empty array or default laps - backend will use all available laps
        const result = await fetchPerfectLap([]);
        setData(result);
      } catch (error) {
        console.error('Error loading perfect lap:', error);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  if (loading) {
    return (
      <div className="glass p-6 rounded-xl border border-white/10">
        <div className="flex items-center justify-center h-64">
          <Loader2 className="w-12 h-12 animate-spin text-toyota-red" />
        </div>
      </div>
    );
  }

  if (!data) return null;

  return (
    <div className="glass p-6 rounded-xl border border-white/10 relative overflow-hidden">
      {/* Animated background */}
      <div className="absolute inset-0 bg-gradient-to-br from-toyota-red/5 via-transparent to-purple-500/5 animate-pulse-slow"></div>

      <div className="relative z-10">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-gradient-to-br from-yellow-500/20 to-toyota-red/20 rounded-lg">
              <Sparkles className="w-5 h-5 text-yellow-400" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-lg font-bold text-white">Perfect Lap</h3>
                <ComponentExplanation componentName="perfect_lap" />
              </div>
              <p className="text-sm text-gray-400">
                Theoretical best from all sectors
              </p>
            </div>
          </div>
          <DatasetBadges.Sectors />
        </div>

        {/* Perfect Time */}
        <div className="glass-inner p-6 rounded-xl mb-6 text-center border-2 border-yellow-500/30">
          <p className="text-sm text-gray-400 mb-2">Perfect Lap Time</p>
          <p className="text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-yellow-400 to-toyota-red">
            {data.perfect_lap_time.toFixed(3)}s
          </p>
          <div className="flex items-center justify-center gap-2 mt-3">
            <TrendingDown className="w-4 h-4 text-green-400" />
            <p className="text-sm text-green-400">
              {data.improvement_potential.toFixed(3)}s faster than best lap
            </p>
          </div>
        </div>

        {/* Best Sectors */}
        <div className="space-y-3">
          <h4 className="text-sm font-semibold text-gray-400">Best Sector Times</h4>

          {/* Sector 1 */}
          <div className="glass-inner p-4 rounded-lg border-l-4 border-blue-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-gray-400 mb-1">Sector 1</p>
                <p className="text-2xl font-bold text-white">
                  {data.best_sectors.s1.time.toFixed(3)}s
                </p>
              </div>
              <div className="text-right">
                <p className="text-xs text-gray-400">Best by</p>
                <p className="text-sm font-semibold text-white">
                  #{data.best_sectors.s1.vehicle}
                </p>
                <p className="text-xs text-blue-400">Lap {data.best_sectors.s1.lap}</p>
              </div>
            </div>
          </div>

          {/* Sector 2 */}
          <div className="glass-inner p-4 rounded-lg border-l-4 border-green-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-gray-400 mb-1">Sector 2</p>
                <p className="text-2xl font-bold text-white">
                  {data.best_sectors.s2.time.toFixed(3)}s
                </p>
              </div>
              <div className="text-right">
                <p className="text-xs text-gray-400">Best by</p>
                <p className="text-sm font-semibold text-white">
                  #{data.best_sectors.s2.vehicle}
                </p>
                <p className="text-xs text-green-400">Lap {data.best_sectors.s2.lap}</p>
              </div>
            </div>
          </div>

          {/* Sector 3 */}
          <div className="glass-inner p-4 rounded-lg border-l-4 border-yellow-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-gray-400 mb-1">Sector 3</p>
                <p className="text-2xl font-bold text-white">
                  {data.best_sectors.s3.time.toFixed(3)}s
                </p>
              </div>
              <div className="text-right">
                <p className="text-xs text-gray-400">Best by</p>
                <p className="text-sm font-semibold text-white">
                  #{data.best_sectors.s3.vehicle}
                </p>
                <p className="text-xs text-yellow-400">Lap {data.best_sectors.s3.lap}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Comparison */}
        <div className="mt-6 glass-inner p-4 rounded-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-gray-400 mb-1">Current Best Lap</p>
              <p className="text-lg font-bold text-gray-300">
                {data.actual_best_lap.toFixed(3)}s
              </p>
            </div>
            <div className="flex items-center gap-2">
              <Zap className="w-5 h-5 text-toyota-red" />
              <div className="text-right">
                <p className="text-xs text-gray-400">Achievable Gain</p>
                <p className="text-xl font-bold text-toyota-red">
                  -{data.improvement_potential.toFixed(3)}s
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
