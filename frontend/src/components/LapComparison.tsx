import { useEffect, useState } from 'react';
import { useStore } from '../store/useStore';
import { fetchLapComparison, fetchBestLap } from '../api';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Area,
  AreaChart,
  ReferenceLine,
} from 'recharts';
import { GitCompare, Trophy, Clock, TrendingDown, TrendingUp } from 'lucide-react';

interface ComparisonData {
  lap1: { number: number; time: number; data: Record<string, number[]> };
  lap2: { number: number; time: number; data: Record<string, number[]> };
  delta: { distance: number[]; speed_delta: number[]; cumulative_time_delta: number[] };
  time_difference: number;
}

export function LapComparison() {
  const { currentLap, laps } = useStore();
  const [comparison, setComparison] = useState<ComparisonData | null>(null);
  const [refLap, setRefLap] = useState<number | null>(null);
  const [bestLap, setBestLap] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [activeMetric, setActiveMetric] = useState<'speed' | 'delta'>('speed');

  // Load best lap on mount
  useEffect(() => {
    const loadBestLap = async () => {
      try {
        const data = await fetchBestLap();
        setBestLap(data.best_lap);
        setRefLap(data.best_lap);
      } catch (error) {
        console.error('Failed to load best lap:', error);
      }
    };
    loadBestLap();
  }, []);

  // Load comparison when laps change
  useEffect(() => {
    const loadComparison = async () => {
      if (!currentLap || !refLap || currentLap === refLap) return;
      setIsLoading(true);
      try {
        const data = await fetchLapComparison(currentLap, refLap);
        setComparison(data);
      } catch (error) {
        console.error('Failed to load comparison:', error);
      } finally {
        setIsLoading(false);
      }
    };
    loadComparison();
  }, [currentLap, refLap]);

  // Prepare chart data
  const chartData = comparison
    ? comparison.delta.distance.map((dist, i) => ({
        distance: Math.round(dist),
        userSpeed: comparison.lap1.data.speed?.[i] || 0,
        refSpeed: comparison.lap2.data.speed?.[i] || 0,
        speedDelta: comparison.delta.speed_delta[i],
        timeDelta: comparison.delta.cumulative_time_delta[i] * 1000, // to ms
      }))
    : [];

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = (seconds % 60).toFixed(3);
    return `${mins}:${secs.padStart(6, '0')}`;
  };

  return (
    <div className="glass rounded-xl p-4 space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="font-bold text-white flex items-center gap-2">
          <GitCompare className="w-5 h-5 text-toyota-red" />
          Lap Comparison
        </h3>

        {/* Reference Lap Selector */}
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-400">vs</span>
          <select
            value={refLap || ''}
            onChange={(e) => setRefLap(Number(e.target.value))}
            className="bg-white/5 border border-white/10 rounded-lg px-3 py-1 text-sm text-white focus:outline-none focus:border-toyota-red"
          >
            {laps.map((lap) => (
              <option key={lap} value={lap} className="bg-gray-900">
                Lap {lap} {lap === bestLap ? '(Best)' : ''}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Time Comparison Cards */}
      {comparison && (
        <div className="grid grid-cols-3 gap-3">
          <div className="p-3 rounded-lg bg-blue-500/10 border border-blue-500/20">
            <div className="flex items-center gap-2 mb-1">
              <Clock className="w-4 h-4 text-blue-400" />
              <span className="text-xs text-gray-400">Your Lap {comparison.lap1.number}</span>
            </div>
            <p className="text-lg font-bold text-blue-400">{formatTime(comparison.lap1.time)}</p>
          </div>

          <div className="p-3 rounded-lg bg-green-500/10 border border-green-500/20">
            <div className="flex items-center gap-2 mb-1">
              <Trophy className="w-4 h-4 text-green-400" />
              <span className="text-xs text-gray-400">Reference Lap {comparison.lap2.number}</span>
            </div>
            <p className="text-lg font-bold text-green-400">{formatTime(comparison.lap2.time)}</p>
          </div>

          <div
            className={`p-3 rounded-lg border ${
              comparison.time_difference > 0
                ? 'bg-red-500/10 border-red-500/20'
                : 'bg-green-500/10 border-green-500/20'
            }`}
          >
            <div className="flex items-center gap-2 mb-1">
              {comparison.time_difference > 0 ? (
                <TrendingDown className="w-4 h-4 text-red-400" />
              ) : (
                <TrendingUp className="w-4 h-4 text-green-400" />
              )}
              <span className="text-xs text-gray-400">Delta</span>
            </div>
            <p
              className={`text-lg font-bold ${
                comparison.time_difference > 0 ? 'text-red-400' : 'text-green-400'
              }`}
            >
              {comparison.time_difference > 0 ? '+' : ''}
              {comparison.time_difference.toFixed(3)}s
            </p>
          </div>
        </div>
      )}

      {/* Metric Toggle */}
      <div className="flex gap-2">
        <button
          onClick={() => setActiveMetric('speed')}
          className={`flex-1 py-2 rounded-lg text-sm font-medium transition-colors ${
            activeMetric === 'speed'
              ? 'bg-toyota-red text-white'
              : 'bg-white/5 text-gray-400 hover:bg-white/10'
          }`}
        >
          Speed Comparison
        </button>
        <button
          onClick={() => setActiveMetric('delta')}
          className={`flex-1 py-2 rounded-lg text-sm font-medium transition-colors ${
            activeMetric === 'delta'
              ? 'bg-toyota-red text-white'
              : 'bg-white/5 text-gray-400 hover:bg-white/10'
          }`}
        >
          Time Delta
        </button>
      </div>

      {/* Charts */}
      {isLoading ? (
        <div className="h-48 flex items-center justify-center">
          <div className="animate-spin w-8 h-8 border-2 border-toyota-red border-t-transparent rounded-full" />
        </div>
      ) : chartData.length > 0 ? (
        <div className="h-48">
          <ResponsiveContainer width="100%" height="100%">
            {activeMetric === 'speed' ? (
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                <XAxis dataKey="distance" stroke="#666" tick={{ fontSize: 10 }} />
                <YAxis stroke="#666" tick={{ fontSize: 10 }} />
                <Tooltip
                  contentStyle={{
                    background: 'rgba(0,0,0,0.9)',
                    border: '1px solid #333',
                    borderRadius: '8px',
                  }}
                />
                <Line
                  type="monotone"
                  dataKey="userSpeed"
                  stroke="#3b82f6"
                  strokeWidth={2}
                  dot={false}
                  name="Your Lap"
                />
                <Line
                  type="monotone"
                  dataKey="refSpeed"
                  stroke="#22c55e"
                  strokeWidth={2}
                  dot={false}
                  name="Reference"
                  strokeDasharray="5 5"
                />
              </LineChart>
            ) : (
              <AreaChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                <XAxis dataKey="distance" stroke="#666" tick={{ fontSize: 10 }} />
                <YAxis stroke="#666" tick={{ fontSize: 10 }} />
                <Tooltip
                  contentStyle={{
                    background: 'rgba(0,0,0,0.9)',
                    border: '1px solid #333',
                    borderRadius: '8px',
                  }}
                />
                <ReferenceLine y={0} stroke="#666" />
                <defs>
                  <linearGradient id="deltaGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3} />
                    <stop offset="50%" stopColor="#666" stopOpacity={0} />
                    <stop offset="95%" stopColor="#22c55e" stopOpacity={0.3} />
                  </linearGradient>
                </defs>
                <Area
                  type="monotone"
                  dataKey="timeDelta"
                  stroke="#EB0A1E"
                  fill="url(#deltaGradient)"
                  strokeWidth={2}
                  name="Time Delta (ms)"
                />
              </AreaChart>
            )}
          </ResponsiveContainer>
        </div>
      ) : (
        <div className="h-48 flex items-center justify-center text-gray-400">
          Select different laps to compare
        </div>
      )}

      {/* Legend */}
      {activeMetric === 'speed' && (
        <div className="flex justify-center gap-6 text-xs">
          <div className="flex items-center gap-2">
            <div className="w-3 h-0.5 bg-blue-500" />
            <span className="text-gray-400">Your Lap</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-0.5 bg-green-500 border-dashed" />
            <span className="text-gray-400">Reference (Ghost)</span>
          </div>
        </div>
      )}
    </div>
  );
}
