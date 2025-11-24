import { useEffect, useState } from 'react';
import { Trophy, TrendingUp, Target, Loader2 } from 'lucide-react';
import { fetchBestLaps } from '../api';
import { useStore } from '../store/useStore';
import { DatasetBadges } from './DatasetBadge';
import { ComponentExplanation } from './ComponentExplanation';

interface BestLap {
  rank: number;
  lap_number: number;
  lap_time: string;
  lap_time_seconds: number;
}

interface BestLapsData {
  vehicle_number: number;
  vehicle: string;
  class: string;
  total_laps: number;
  average_time: string;
  best_laps: BestLap[];
  consistency_score: number;
}

export default function BestLaps() {
  const { selectedLap } = useStore();
  const [data, setData] = useState<BestLapsData | null>(null);
  const [loading, setLoading] = useState(false);
  const [vehicleNumber, setVehicleNumber] = useState(2); // Default vehicle

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      try {
        const result = await fetchBestLaps();
        setData(result);
      } catch (error) {
        console.error('Error loading best laps:', error);
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

  const getConsistencyColor = (score: number) => {
    if (score >= 95) return 'text-green-400';
    if (score >= 90) return 'text-yellow-400';
    return 'text-orange-400';
  };

  return (
    <div className="glass p-6 rounded-xl border border-white/10">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-toyota-red/20 rounded-lg">
            <Trophy className="w-5 h-5 text-toyota-red" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-lg font-bold text-white">Best Laps</h3>
              <ComponentExplanation componentName="best_laps" />
            </div>
            <p className="text-sm text-gray-400">
              Vehicle #{data.vehicle_number} • {data.class}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {/* Vehicle Selector */}
          <select
            value={vehicleNumber}
            onChange={(e) => setVehicleNumber(Number(e.target.value))}
            className="bg-white/5 border border-white/10 rounded-lg px-3 py-1.5 text-sm text-white"
          >
            {[2, 3, 7, 13, 16].map((num) => (
              <option key={num} value={num}>
                Vehicle #{num}
              </option>
            ))}
          </select>
          <DatasetBadges.BestLaps />
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="glass-inner p-3 rounded-lg">
          <div className="flex items-center gap-2 mb-1">
            <Target className="w-4 h-4 text-gray-400" />
            <span className="text-xs text-gray-400">Total Laps</span>
          </div>
          <p className="text-xl font-bold text-white">{data.total_laps}</p>
        </div>

        <div className="glass-inner p-3 rounded-lg">
          <div className="flex items-center gap-2 mb-1">
            <TrendingUp className="w-4 h-4 text-gray-400" />
            <span className="text-xs text-gray-400">Average</span>
          </div>
          <p className="text-xl font-bold text-white">{data.average_time}</p>
        </div>

        <div className="glass-inner p-3 rounded-lg">
          <div className="flex items-center gap-2 mb-1">
            <Trophy className="w-4 h-4 text-gray-400" />
            <span className="text-xs text-gray-400">Consistency</span>
          </div>
          <p className={`text-xl font-bold ${getConsistencyColor(data.consistency_score)}`}>
            {data.consistency_score.toFixed(1)}
          </p>
        </div>
      </div>

      {/* Best Laps List */}
      <div className="space-y-2">
        <h4 className="text-sm font-semibold text-gray-400 mb-3">Top 10 Laps</h4>
        {data.best_laps.map((lap) => (
          <div
            key={lap.rank}
            className={`glass-inner p-3 rounded-lg transition-all cursor-pointer ${
              lap.lap_number === selectedLap
                ? 'border-l-4 border-toyota-red bg-toyota-red/10'
                : 'hover:bg-white/5'
            }`}
            onClick={() => useStore.setState({ selectedLap: lap.lap_number })}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div
                  className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm ${
                    lap.rank === 1
                      ? 'bg-yellow-500/20 text-yellow-400'
                      : lap.rank === 2
                      ? 'bg-gray-400/20 text-gray-300'
                      : lap.rank === 3
                      ? 'bg-orange-500/20 text-orange-400'
                      : 'bg-white/5 text-gray-400'
                  }`}
                >
                  {lap.rank}
                </div>
                <div>
                  <p className="text-white font-medium">Lap {lap.lap_number}</p>
                  <p className="text-xs text-gray-400">
                    {lap.lap_time_seconds.toFixed(3)}s
                  </p>
                </div>
              </div>

              <div className="text-right">
                <p className="text-lg font-mono font-bold text-white">{lap.lap_time}</p>
                {lap.rank === 1 && (
                  <p className="text-xs text-green-400">Personal Best</p>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
