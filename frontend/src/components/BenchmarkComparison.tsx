import { useEffect, useState } from 'react';
import { useStore } from '../store/useStore';
import { api } from '../api';
import { GitCompare, TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts';

interface MicroSector {
  segment: number;
  delta_seconds: number;
  cumulative_delta: number;
  status: string;
}

interface BenchmarkData {
  lap: number;
  current_lap_time: number;
  reference_type: string;
  reference_name: string;
  reference_time: number;
  delta: number;
  percentage_difference: number;
  micro_sectors: MicroSector[];
  overall_status: string;
  areas_to_improve: Array<{
    sector: string;
    time_loss: number;
  }>;
}

export function BenchmarkComparison() {
  const currentLap = useStore((state) => state.currentLap);
  const [benchmarkData, setBenchmarkData] = useState<BenchmarkData | null>(null);
  const [referenceType, setReferenceType] = useState<string>('personal_best');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchBenchmark = async () => {
      if (!currentLap) return;
      setLoading(true);
      try {
        const response = await api.get(`/api/training/benchmark/${currentLap}/vs/${referenceType}`);
        setBenchmarkData(response.data);
      } catch (error) {
        console.error('Error fetching benchmark:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchBenchmark();
  }, [currentLap, referenceType]);

  if (loading) {
    return (
      <div className="glass rounded-xl p-6">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-toyota-red"></div>
        </div>
      </div>
    );
  }

  if (!benchmarkData) {
    return (
      <div className="glass rounded-xl p-6">
        <div className="flex items-center gap-3 mb-4">
          <GitCompare className="w-6 h-6 text-toyota-red" />
          <h3 className="text-lg font-semibold text-white">Benchmark Comparison</h3>
        </div>
        <p className="text-gray-400 text-sm">Select a lap to compare against benchmarks</p>
      </div>
    );
  }

  const getDeltaIcon = (status: string) => {
    if (status === 'faster') return <TrendingUp className="w-5 h-5 text-green-500" />;
    if (status === 'slower') return <TrendingDown className="w-5 h-5 text-red-500" />;
    return <Minus className="w-5 h-5 text-gray-500" />;
  };

  const getDeltaColor = (delta: number) => {
    if (delta < 0) return '#22c55e';
    if (delta > 0) return '#ef4444';
    return '#6b7280';
  };

  // Prepare data for micro-sector chart (show every 5th segment to reduce clutter)
  const chartData = benchmarkData.micro_sectors
    .filter((_, idx) => idx % 5 === 0)
    .map((sector) => ({
      segment: sector.segment,
      delta: sector.delta_seconds,
      cumulative: sector.cumulative_delta
    }));

  return (
    <div className="glass rounded-xl p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <GitCompare className="w-6 h-6 text-toyota-red" />
          <h3 className="text-lg font-semibold text-white">Benchmark Comparison</h3>
        </div>
        <div className="px-3 py-1 rounded-full bg-white/5">
          <span className="text-xs text-gray-400">Lap {benchmarkData.lap}</span>
        </div>
      </div>

      {/* Reference Type Selector */}
      <div className="grid grid-cols-4 gap-2 mb-4">
        {[
          { value: 'personal_best', label: 'Personal Best' },
          { value: 'track_record', label: 'Track Record' },
          { value: 'perfect', label: 'Perfect Lap' },
          { value: 'peer', label: 'Peer Average' }
        ].map((ref) => (
          <button
            key={ref.value}
            onClick={() => setReferenceType(ref.value)}
            className={`px-3 py-2 rounded-lg text-xs font-semibold transition ${
              referenceType === ref.value
                ? 'bg-toyota-red text-white'
                : 'bg-white/5 text-gray-400 hover:bg-white/10'
            }`}
          >
            {ref.label}
          </button>
        ))}
      </div>

      {/* Comparison Summary */}
      <div className="grid grid-cols-3 gap-3 mb-4">
        <div className="bg-white/5 rounded-lg p-3">
          <p className="text-xs text-gray-400 mb-1">Your Time</p>
          <p className="text-lg font-bold text-white">{benchmarkData.current_lap_time.toFixed(3)}s</p>
        </div>
        <div className="bg-white/5 rounded-lg p-3">
          <p className="text-xs text-gray-400 mb-1">{benchmarkData.reference_name}</p>
          <p className="text-lg font-bold text-blue-400">{benchmarkData.reference_time.toFixed(3)}s</p>
        </div>
        <div className="bg-white/5 rounded-lg p-3">
          <div className="flex items-center gap-2 mb-1">
            {getDeltaIcon(benchmarkData.overall_status)}
            <p className="text-xs text-gray-400">Delta</p>
          </div>
          <p
            className="text-lg font-bold"
            style={{ color: getDeltaColor(benchmarkData.delta) }}
          >
            {benchmarkData.delta >= 0 ? '+' : ''}
            {benchmarkData.delta.toFixed(3)}s
          </p>
          <p className="text-xs text-gray-500 mt-1">
            ({benchmarkData.percentage_difference >= 0 ? '+' : ''}
            {benchmarkData.percentage_difference.toFixed(2)}%)
          </p>
        </div>
      </div>

      {/* Micro-Sector Delta Chart */}
      <div className="mb-4">
        <h4 className="text-sm font-semibold text-gray-400 mb-2">Micro-Sector Analysis</h4>
        <div className="h-48">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.1)" />
              <XAxis
                dataKey="segment"
                stroke="#9ca3af"
                tick={{ fill: '#9ca3af', fontSize: 10 }}
                label={{ value: 'Track Segment', position: 'insideBottom', offset: -5, fill: '#6b7280', fontSize: 10 }}
              />
              <YAxis
                stroke="#9ca3af"
                tick={{ fill: '#9ca3af', fontSize: 10 }}
                label={{ value: 'Delta (s)', angle: -90, position: 'insideLeft', fill: '#6b7280', fontSize: 10 }}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'rgba(0, 0, 0, 0.8)',
                  border: '1px solid rgba(255, 255, 255, 0.1)',
                  borderRadius: '8px',
                  color: '#fff'
                }}
                formatter={(value: any) => [`${value >= 0 ? '+' : ''}${value.toFixed(3)}s`, 'Delta']}
              />
              <ReferenceLine y={0} stroke="#6b7280" strokeDasharray="3 3" />
              <Bar
                dataKey="delta"
                fill="#eb0a1e"
                radius={[4, 4, 0, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Areas to Improve */}
      <div className="space-y-2">
        <h4 className="text-sm font-semibold text-gray-400 uppercase">Top Areas to Improve</h4>
        {benchmarkData.areas_to_improve.slice(0, 5).map((area, idx) => (
          <div
            key={idx}
            className="flex items-center justify-between bg-red-500/10 rounded-lg p-2 border border-red-500/20"
          >
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold text-red-400">#{idx + 1}</span>
              <span className="text-sm text-gray-300">{area.sector}</span>
            </div>
            <span className="text-sm font-bold text-red-400">
              +{area.time_loss.toFixed(3)}s
            </span>
          </div>
        ))}
      </div>

      {/* Action Button */}
      <div className="mt-4 pt-4 border-t border-white/10">
        <button className="w-full px-4 py-2 bg-blue-500 text-white rounded-lg font-semibold hover:bg-blue-600 transition flex items-center justify-center gap-2">
          <GitCompare className="w-4 h-4" />
          View Full Comparison
        </button>
      </div>
    </div>
  );
}
