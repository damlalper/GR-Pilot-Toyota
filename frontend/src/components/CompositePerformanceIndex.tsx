import { useEffect, useState } from 'react';
import { useStore } from '../store/useStore';
import { api } from '../api';
import { Gauge, TrendingUp, TrendingDown, Activity } from 'lucide-react';

interface CPIData {
  lap: number;
  cpi_score: number;
  rating: string;
  color: string;
  components: {
    [key: string]: number;
  };
  strengths: Array<{ metric: string; score: number }>;
  weaknesses: Array<{ metric: string; score: number }>;
  recommendations: string[];
}

export function CompositePerformanceIndex() {
  const currentLap = useStore((state) => state.currentLap);
  const [cpiData, setCpiData] = useState<CPIData | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchCPI = async () => {
      if (!currentLap) return;
      setLoading(true);
      try {
        const response = await api.get(`/cpi/${currentLap}`);
        setCpiData(response.data);
      } catch (error) {
        console.error('Error fetching CPI:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchCPI();
  }, [currentLap]);

  if (loading) {
    return (
      <div className="glass rounded-xl p-6">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-toyota-red"></div>
        </div>
      </div>
    );
  }

  if (!cpiData) {
    return (
      <div className="glass rounded-xl p-6">
        <div className="flex items-center gap-3 mb-4">
          <Gauge className="w-6 h-6 text-toyota-red" />
          <h3 className="text-lg font-semibold text-white">Composite Performance Index</h3>
        </div>
        <p className="text-gray-400 text-sm">Select a lap to view CPI analysis</p>
      </div>
    );
  }

  const componentEntries = Object.entries(cpiData.components);
  const maxScore = 100;

  return (
    <div className="glass rounded-xl p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Gauge className="w-6 h-6 text-toyota-red" />
          <h3 className="text-lg font-semibold text-white">Composite Performance Index</h3>
        </div>
        <div className="px-3 py-1 rounded-full bg-white/5">
          <span className="text-xs text-gray-400">Lap {cpiData.lap}</span>
        </div>
      </div>

      {/* Main CPI Score */}
      <div className="relative">
        <div className="flex flex-col items-center justify-center py-8">
          {/* Circular Progress */}
          <div className="relative w-48 h-48">
            <svg className="w-full h-full transform -rotate-90">
              {/* Background circle */}
              <circle
                cx="96"
                cy="96"
                r="80"
                stroke="rgba(255, 255, 255, 0.1)"
                strokeWidth="12"
                fill="none"
              />
              {/* Progress circle */}
              <circle
                cx="96"
                cy="96"
                r="80"
                stroke={cpiData.color}
                strokeWidth="12"
                fill="none"
                strokeDasharray={`${(cpiData.cpi_score / 100) * 502.65} 502.65`}
                strokeLinecap="round"
                className="transition-all duration-1000 ease-out"
              />
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <span className="text-5xl font-bold text-white">
                {cpiData.cpi_score}
              </span>
              <span className="text-sm text-gray-400 mt-1">/ 100</span>
              <span
                className="text-xs font-semibold mt-2 px-3 py-1 rounded-full"
                style={{ backgroundColor: cpiData.color + '20', color: cpiData.color }}
              >
                {cpiData.rating}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Component Breakdown */}
      <div className="space-y-3">
        <h4 className="text-sm font-semibold text-gray-400 uppercase tracking-wider">
          Performance Breakdown
        </h4>
        {componentEntries.map(([name, score]) => (
          <div key={name} className="space-y-1">
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-300">{name}</span>
              <span className="font-semibold text-white">{score}%</span>
            </div>
            <div className="w-full bg-white/10 rounded-full h-2 overflow-hidden">
              <div
                className="h-full rounded-full transition-all duration-500"
                style={{
                  width: `${score}%`,
                  backgroundColor:
                    score >= 80
                      ? '#22c55e'
                      : score >= 60
                      ? '#fbbf24'
                      : '#ef4444',
                }}
              />
            </div>
          </div>
        ))}
      </div>

      {/* Strengths & Weaknesses */}
      <div className="grid grid-cols-2 gap-4">
        {/* Strengths */}
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-green-500" />
            <h4 className="text-xs font-semibold text-gray-400 uppercase">Strengths</h4>
          </div>
          <div className="space-y-1">
            {cpiData.strengths.map((item, idx) => (
              <div
                key={idx}
                className="flex items-center justify-between text-xs bg-green-500/10 rounded px-2 py-1"
              >
                <span className="text-green-400">{item.metric}</span>
                <span className="font-semibold text-green-300">{item.score}%</span>
              </div>
            ))}
          </div>
        </div>

        {/* Weaknesses */}
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <TrendingDown className="w-4 h-4 text-red-500" />
            <h4 className="text-xs font-semibold text-gray-400 uppercase">Weaknesses</h4>
          </div>
          <div className="space-y-1">
            {cpiData.weaknesses.map((item, idx) => (
              <div
                key={idx}
                className="flex items-center justify-between text-xs bg-red-500/10 rounded px-2 py-1"
              >
                <span className="text-red-400">{item.metric}</span>
                <span className="font-semibold text-red-300">{item.score}%</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Recommendations */}
      <div className="space-y-2 border-t border-white/10 pt-4">
        <div className="flex items-center gap-2">
          <Activity className="w-4 h-4 text-toyota-red" />
          <h4 className="text-xs font-semibold text-gray-400 uppercase">
            AI Recommendations
          </h4>
        </div>
        <div className="space-y-2">
          {cpiData.recommendations.map((rec, idx) => (
            <div
              key={idx}
              className="text-xs text-gray-300 bg-white/5 rounded px-3 py-2 border-l-2 border-toyota-red"
            >
              {rec}
            </div>
          ))}
        </div>
      </div>

      {/* Formula Info */}
      <div className="text-xs text-gray-500 border-t border-white/10 pt-4">
        <p className="italic">
          CPI = Speed (30%) + Brake (20%) + Throttle (15%) + Tire (15%) + Turn Entry (10%) +
          Consistency (10%)
        </p>
      </div>
    </div>
  );
}
