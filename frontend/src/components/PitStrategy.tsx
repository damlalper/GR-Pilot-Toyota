import { useEffect, useState } from 'react';
import { useStore } from '../store/useStore';
import { api } from '../api';
import { Flag, Fuel, TrendingDown, AlertTriangle, CheckCircle, Clock } from 'lucide-react';

interface Strategy {
  name: string;
  pit_lap: number;
  description: string;
  pros: string;
  cons: string;
  tire_at_pit: number;
  fuel_at_pit: number;
}

interface PitStrategyData {
  current_lap: number;
  race_laps: number;
  laps_remaining: number;
  recommendation: string;
  urgency: 'low' | 'medium' | 'high' | 'critical';
  optimal_pit_lap: number;
  tire_analysis: {
    current_condition: number;
    degradation_rate: number;
    degradation_pct_per_lap: number;
    laps_on_current_tires: number;
    estimated_critical_lap: number;
  };
  fuel_analysis: {
    fuel_remaining: number;
    fuel_per_lap: number;
    laps_of_fuel_remaining: number;
    fuel_critical_lap: number;
  };
  strategy_options: Strategy[];
  undercut_window: number;
  overcut_window: number;
  caution_strategy: string;
  weather_impact: {
    track_temp: number;
    temp_multiplier: number;
    impact: string;
  };
  lap_time_trend: Array<{ lap: number; time: number; avg_speed: number }>;
}

export function PitStrategy() {
  const currentLap = useStore((state) => state.currentLap);
  const [strategyData, setStrategyData] = useState<PitStrategyData | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchStrategy = async () => {
      if (!currentLap) return;
      setLoading(true);
      try {
        const response = await api.get(`/pit_strategy/${currentLap}`);
        setStrategyData(response.data);
      } catch (error) {
        console.error('Error fetching pit strategy:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchStrategy();
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

  if (!strategyData) {
    return (
      <div className="glass rounded-xl p-6">
        <div className="flex items-center gap-3 mb-4">
          <Flag className="w-6 h-6 text-toyota-red" />
          <h3 className="text-lg font-semibold text-white">Pit Strategy Simulator</h3>
        </div>
        <p className="text-gray-400 text-sm">Select a lap to view pit strategy</p>
      </div>
    );
  }

  const urgencyColors = {
    low: { bg: 'bg-green-500/20', text: 'text-green-400', border: 'border-green-500' },
    medium: { bg: 'bg-yellow-500/20', text: 'text-yellow-400', border: 'border-yellow-500' },
    high: { bg: 'bg-orange-500/20', text: 'text-orange-400', border: 'border-orange-500' },
    critical: { bg: 'bg-red-500/20', text: 'text-red-400', border: 'border-red-500' },
  };

  const urgencyStyle = urgencyColors[strategyData.urgency];

  return (
    <div className="glass rounded-xl p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Flag className="w-6 h-6 text-toyota-red" />
          <h3 className="text-lg font-semibold text-white">Pit Strategy Simulator</h3>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-400">Lap</span>
          <span className="text-lg font-bold text-white">{strategyData.current_lap}</span>
          <span className="text-xs text-gray-400">/ {strategyData.race_laps}</span>
        </div>
      </div>

      {/* Main Recommendation */}
      <div
        className={`${urgencyStyle.bg} ${urgencyStyle.border} border-l-4 rounded-lg p-4`}
      >
        <div className="flex items-start gap-3">
          <AlertTriangle className={`w-5 h-5 ${urgencyStyle.text} mt-0.5`} />
          <div className="flex-1">
            <div className="flex items-center justify-between mb-2">
              <h4 className={`font-semibold ${urgencyStyle.text}`}>Strategy Recommendation</h4>
              <span
                className={`text-xs px-2 py-1 rounded-full ${urgencyStyle.bg} ${urgencyStyle.text} border ${urgencyStyle.border}`}
              >
                {strategyData.urgency.toUpperCase()}
              </span>
            </div>
            <p className="text-white font-medium">{strategyData.recommendation}</p>
            <p className="text-gray-400 text-sm mt-2">
              Optimal pit window: Lap {strategyData.optimal_pit_lap}
            </p>
          </div>
        </div>
      </div>

      {/* Tire & Fuel Status */}
      <div className="grid grid-cols-2 gap-4">
        {/* Tire Status */}
        <div className="bg-white/5 rounded-lg p-4 space-y-3">
          <div className="flex items-center gap-2">
            <TrendingDown className="w-4 h-4 text-blue-400" />
            <h4 className="text-sm font-semibold text-gray-400">TIRE CONDITION</h4>
          </div>
          <div className="space-y-2">
            <div className="flex items-end gap-2">
              <span className="text-3xl font-bold text-white">
                {strategyData.tire_analysis.current_condition.toFixed(0)}
              </span>
              <span className="text-sm text-gray-400 mb-1">%</span>
            </div>
            <div className="w-full bg-white/10 rounded-full h-2">
              <div
                className={`h-full rounded-full transition-all duration-500 ${
                  strategyData.tire_analysis.current_condition > 60
                    ? 'bg-green-500'
                    : strategyData.tire_analysis.current_condition > 30
                    ? 'bg-yellow-500'
                    : 'bg-red-500'
                }`}
                style={{ width: `${strategyData.tire_analysis.current_condition}%` }}
              />
            </div>
            <div className="text-xs text-gray-400 space-y-1">
              <p>Degradation: {strategyData.tire_analysis.degradation_pct_per_lap.toFixed(2)}% / lap</p>
              <p>Critical at: Lap {strategyData.tire_analysis.estimated_critical_lap}</p>
            </div>
          </div>
        </div>

        {/* Fuel Status */}
        <div className="bg-white/5 rounded-lg p-4 space-y-3">
          <div className="flex items-center gap-2">
            <Fuel className="w-4 h-4 text-amber-400" />
            <h4 className="text-sm font-semibold text-gray-400">FUEL STATUS</h4>
          </div>
          <div className="space-y-2">
            <div className="flex items-end gap-2">
              <span className="text-3xl font-bold text-white">
                {strategyData.fuel_analysis.fuel_remaining.toFixed(1)}
              </span>
              <span className="text-sm text-gray-400 mb-1">L</span>
            </div>
            <div className="w-full bg-white/10 rounded-full h-2">
              <div
                className="h-full rounded-full bg-amber-500 transition-all duration-500"
                style={{
                  width: `${(strategyData.fuel_analysis.fuel_remaining / 60) * 100}%`,
                }}
              />
            </div>
            <div className="text-xs text-gray-400 space-y-1">
              <p>Consumption: {strategyData.fuel_analysis.fuel_per_lap.toFixed(2)}L / lap</p>
              <p>
                Remaining: {strategyData.fuel_analysis.laps_of_fuel_remaining.toFixed(1)} laps
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Strategy Options */}
      <div className="space-y-3">
        <h4 className="text-sm font-semibold text-gray-400 uppercase tracking-wider">
          Strategy Options
        </h4>
        <div className="space-y-2">
          {strategyData.strategy_options.map((strategy, idx) => (
            <div
              key={idx}
              className="bg-white/5 hover:bg-white/10 transition-colors rounded-lg p-4 border border-white/10"
            >
              <div className="flex items-center justify-between mb-2">
                <h5 className="font-semibold text-white">{strategy.name}</h5>
                <span className="text-sm text-toyota-red font-bold">
                  LAP {strategy.pit_lap}
                </span>
              </div>
              <p className="text-xs text-gray-400 mb-3">{strategy.description}</p>
              <div className="grid grid-cols-2 gap-3 text-xs">
                <div>
                  <p className="text-green-400 mb-1">✓ {strategy.pros}</p>
                  <p className="text-red-400">✗ {strategy.cons}</p>
                </div>
                <div className="text-right text-gray-400">
                  <p>Tire: {strategy.tire_at_pit.toFixed(0)}%</p>
                  <p>Fuel: {strategy.fuel_at_pit.toFixed(1)}L</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Undercut/Overcut Windows */}
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-3">
          <div className="flex items-center gap-2 mb-2">
            <Clock className="w-4 h-4 text-blue-400" />
            <h5 className="text-xs font-semibold text-blue-400 uppercase">Undercut Window</h5>
          </div>
          <p className="text-2xl font-bold text-white">Lap {strategyData.undercut_window}</p>
          <p className="text-xs text-gray-400 mt-1">Pit early to gain position</p>
        </div>

        <div className="bg-purple-500/10 border border-purple-500/30 rounded-lg p-3">
          <div className="flex items-center gap-2 mb-2">
            <Clock className="w-4 h-4 text-purple-400" />
            <h5 className="text-xs font-semibold text-purple-400 uppercase">Overcut Window</h5>
          </div>
          <p className="text-2xl font-bold text-white">Lap {strategyData.overcut_window}</p>
          <p className="text-xs text-gray-400 mt-1">Stay out longer</p>
        </div>
      </div>

      {/* Caution Strategy */}
      <div className="bg-yellow-500/10 border-l-4 border-yellow-500 rounded p-3">
        <div className="flex items-center gap-2 mb-1">
          <AlertTriangle className="w-4 h-4 text-yellow-400" />
          <h5 className="text-xs font-semibold text-yellow-400 uppercase">
            Caution (Yellow Flag) Strategy
          </h5>
        </div>
        <p className="text-sm text-white">{strategyData.caution_strategy}</p>
      </div>

      {/* Weather Impact */}
      <div className="bg-white/5 rounded-lg p-3 text-xs text-gray-400">
        <p>
          <span className="font-semibold">Track Temp:</span> {strategyData.weather_impact.track_temp}°C
        </p>
        <p>
          <span className="font-semibold">Impact:</span> {strategyData.weather_impact.impact}
        </p>
      </div>
    </div>
  );
}
