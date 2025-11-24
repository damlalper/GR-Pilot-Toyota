import { useState, useEffect } from 'react';
import { useStore } from '../store/useStore';
import { fetchGripIndex } from '../api';
import { Gauge, Loader2, Thermometer, Droplets, Wind } from 'lucide-react';
import { ComponentExplanation } from './ComponentExplanation';

interface GripData {
  lap: number;
  overall_grip_index: number;
  weather_factors: {
    track_temp: number;
    ambient_temp: number;
    humidity: number;
    temp_factor: number;
    humidity_factor: number;
  };
  critical_zones_count: number;
  recommendation: string;
}

export function GripIndex() {
  const { currentLap } = useStore();
  const [data, setData] = useState<GripData | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (!currentLap) return;
    setIsLoading(true);
    fetchGripIndex(currentLap)
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

  const gripIndex = data.overall_grip_index;
  const gripColor = gripIndex >= 80 ? 'text-green-400' : gripIndex >= 60 ? 'text-yellow-400' : 'text-red-400';
  const gripBg = gripIndex >= 80 ? 'from-green-500' : gripIndex >= 60 ? 'from-yellow-500' : 'from-red-500';
  const gripLevel = gripIndex >= 80 ? 'Excellent' : gripIndex >= 60 ? 'Good' : 'Limited';

  return (
    <div className="glass rounded-xl p-4">
      <div className="flex items-center gap-2 mb-4">
        <div className={`w-8 h-8 rounded-lg bg-gradient-to-br ${gripBg} to-gray-700 flex items-center justify-center`}>
          <Gauge className="w-5 h-5 text-white" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <h3 className="font-medium text-white">Grip Index</h3>
            <ComponentExplanation componentName="grip_index" />
          </div>
          <p className="text-xs text-gray-400">Weather + Telemetry Fusion</p>
        </div>
      </div>

      {/* Main Grip Score */}
      <div className="text-center mb-4">
        <div className={`text-4xl font-bold ${gripColor}`}>{gripIndex.toFixed(1)}%</div>
        <div className="text-sm text-gray-400 uppercase">{gripLevel} Grip</div>
      </div>

      {/* Grip Bar */}
      <div className="h-3 bg-white/10 rounded-full overflow-hidden mb-4">
        <div
          className={`h-full bg-gradient-to-r ${gripBg} to-transparent transition-all duration-500`}
          style={{ width: `${gripIndex}%` }}
        />
      </div>

      {/* Weather Factors */}
      <div className="grid grid-cols-3 gap-2 mb-4">
        <div className="p-2 rounded-lg bg-white/5 text-center">
          <Thermometer className="w-4 h-4 mx-auto text-orange-400 mb-1" />
          <div className="text-sm font-bold text-white">{data.weather_factors.track_temp.toFixed(1)}°C</div>
          <div className="text-xs text-gray-500">Track</div>
        </div>
        <div className="p-2 rounded-lg bg-white/5 text-center">
          <Wind className="w-4 h-4 mx-auto text-blue-400 mb-1" />
          <div className="text-sm font-bold text-white">{data.weather_factors.ambient_temp.toFixed(1)}°C</div>
          <div className="text-xs text-gray-500">Ambient</div>
        </div>
        <div className="p-2 rounded-lg bg-white/5 text-center">
          <Droplets className="w-4 h-4 mx-auto text-cyan-400 mb-1" />
          <div className="text-sm font-bold text-white">{data.weather_factors.humidity.toFixed(1)}%</div>
          <div className="text-xs text-gray-500">Humidity</div>
        </div>
      </div>

      {/* Critical Zones */}
      <div className="p-3 rounded-lg bg-white/5 border border-white/10 mb-3">
        <p className="text-xs text-gray-400 mb-1">Critical Zones</p>
        <p className="text-sm text-white">
          {data.critical_zones_count} {data.critical_zones_count === 1 ? 'zone' : 'zones'} with grip demand exceeding available grip
        </p>
      </div>

      {/* Recommendation */}
      <div className="p-2 rounded-lg bg-toyota-red/10 border border-toyota-red/30">
        <p className="text-xs text-toyota-red">{data.recommendation}</p>
      </div>
    </div>
  );
}
