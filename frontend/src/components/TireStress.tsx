import { useState, useEffect } from 'react';
import { useStore } from '../store/useStore';
import { fetchTireStress } from '../api';
import { CircleDot, Loader2 } from 'lucide-react';

interface TireStressData {
  lap: number;
  overall_stress: number;
  stress_level: string;
  tires: {
    front_left: { stress: number; temp: number; wear: number };
    front_right: { stress: number; temp: number; wear: number };
    rear_left: { stress: number; temp: number; wear: number };
    rear_right: { stress: number; temp: number; wear: number };
  };
  factors: {
    brake_stress: number;
    cornering_stress: number;
    acceleration_stress: number;
    track_temp_impact: number;
  };
  estimated_laps_remaining: number;
  recommendation: string;
}

export function TireStress() {
  const { currentLap } = useStore();
  const [data, setData] = useState<TireStressData | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (!currentLap) return;
    setIsLoading(true);
    fetchTireStress(currentLap)
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

  const getStressColor = (stress: number) => {
    if (stress >= 80) return 'text-red-400';
    if (stress >= 60) return 'text-orange-400';
    if (stress >= 40) return 'text-yellow-400';
    return 'text-green-400';
  };

  const getStressBg = (stress: number) => {
    if (stress >= 80) return 'bg-red-500';
    if (stress >= 60) return 'bg-orange-500';
    if (stress >= 40) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  const TireCard = ({ label, tire }: { label: string; tire: { stress: number; temp: number; wear: number } }) => (
    <div className="p-2 rounded-lg bg-white/5 text-center">
      <div className="text-xs text-gray-400 mb-1">{label}</div>
      <div className={`text-lg font-bold ${getStressColor(tire.stress)}`}>{tire.stress}%</div>
      <div className="h-1.5 bg-white/10 rounded-full overflow-hidden mt-1">
        <div className={`h-full ${getStressBg(tire.stress)}`} style={{ width: `${tire.stress}%` }} />
      </div>
      <div className="text-xs text-gray-500 mt-1">{tire.temp}°C</div>
    </div>
  );

  return (
    <div className="glass rounded-xl p-4">
      <div className="flex items-center gap-2 mb-4">
        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-orange-500 to-red-600 flex items-center justify-center">
          <CircleDot className="w-5 h-5 text-white" />
        </div>
        <div>
          <h3 className="font-medium text-white">Tire Stress</h3>
          <p className="text-xs text-gray-400">Wear estimation & analysis</p>
        </div>
      </div>

      {/* Overall Stress */}
      <div className="text-center mb-4">
        <div className={`text-3xl font-bold ${getStressColor(data.overall_stress)}`}>
          {data.overall_stress}%
        </div>
        <div className="text-sm text-gray-400">{data.stress_level} Stress</div>
      </div>

      {/* 4 Tires Grid - Car View */}
      <div className="relative mb-4">
        <div className="grid grid-cols-2 gap-2">
          <TireCard label="FL" tire={data.tires.front_left} />
          <TireCard label="FR" tire={data.tires.front_right} />
          <TireCard label="RL" tire={data.tires.rear_left} />
          <TireCard label="RR" tire={data.tires.rear_right} />
        </div>
        {/* Car outline indicator */}
        <div className="absolute inset-0 pointer-events-none flex items-center justify-center">
          <div className="w-8 h-16 border-2 border-white/20 rounded" />
        </div>
      </div>

      {/* Stress Factors */}
      <div className="grid grid-cols-2 gap-2 mb-4">
        <div className="p-2 rounded-lg bg-white/5">
          <div className="flex justify-between items-center">
            <span className="text-xs text-gray-400">Braking</span>
            <span className="text-sm font-bold text-white">{data.factors.brake_stress}%</span>
          </div>
        </div>
        <div className="p-2 rounded-lg bg-white/5">
          <div className="flex justify-between items-center">
            <span className="text-xs text-gray-400">Cornering</span>
            <span className="text-sm font-bold text-white">{data.factors.cornering_stress}%</span>
          </div>
        </div>
        <div className="p-2 rounded-lg bg-white/5">
          <div className="flex justify-between items-center">
            <span className="text-xs text-gray-400">Acceleration</span>
            <span className="text-sm font-bold text-white">{data.factors.acceleration_stress}%</span>
          </div>
        </div>
        <div className="p-2 rounded-lg bg-white/5">
          <div className="flex justify-between items-center">
            <span className="text-xs text-gray-400">Track Temp</span>
            <span className="text-sm font-bold text-white">{data.factors.track_temp_impact}%</span>
          </div>
        </div>
      </div>

      {/* Laps Remaining */}
      <div className="p-3 rounded-lg bg-gradient-to-r from-toyota-red/20 to-transparent border border-toyota-red/30 mb-3">
        <div className="flex justify-between items-center">
          <span className="text-sm text-gray-300">Est. Laps Remaining</span>
          <span className="text-xl font-bold text-white">{data.estimated_laps_remaining}</span>
        </div>
      </div>

      {/* Recommendation */}
      <div className="p-2 rounded-lg bg-white/5">
        <p className="text-xs text-gray-300">{data.recommendation}</p>
      </div>
    </div>
  );
}
