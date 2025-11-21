import { useState, useEffect } from 'react';
import { useStore } from '../store/useStore';
import { fetchGripIndex } from '../api';
import { Gauge, Loader2, Thermometer, Droplets, Wind } from 'lucide-react';

interface GripData {
  lap: number;
  grip_index: number;
  grip_level: string;
  factors: {
    track_temp_factor: number;
    ambient_temp_factor: number;
    humidity_factor: number;
    tire_wear_factor: number;
    driving_intensity_factor: number;
  };
  weather: {
    track_temp: number;
    ambient_temp: number;
    humidity: number;
  };
  performance_impact: string;
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

  const gripColor = data.grip_index >= 80 ? 'text-green-400' : data.grip_index >= 60 ? 'text-yellow-400' : 'text-red-400';
  const gripBg = data.grip_index >= 80 ? 'from-green-500' : data.grip_index >= 60 ? 'from-yellow-500' : 'from-red-500';

  return (
    <div className="glass rounded-xl p-4">
      <div className="flex items-center gap-2 mb-4">
        <div className={`w-8 h-8 rounded-lg bg-gradient-to-br ${gripBg} to-gray-700 flex items-center justify-center`}>
          <Gauge className="w-5 h-5 text-white" />
        </div>
        <div>
          <h3 className="font-medium text-white">Grip Index</h3>
          <p className="text-xs text-gray-400">Weather + Telemetry Fusion</p>
        </div>
      </div>

      {/* Main Grip Score */}
      <div className="text-center mb-4">
        <div className={`text-4xl font-bold ${gripColor}`}>{data.grip_index}%</div>
        <div className="text-sm text-gray-400 uppercase">{data.grip_level} Grip</div>
      </div>

      {/* Grip Bar */}
      <div className="h-3 bg-white/10 rounded-full overflow-hidden mb-4">
        <div
          className={`h-full bg-gradient-to-r ${gripBg} to-transparent transition-all duration-500`}
          style={{ width: `${data.grip_index}%` }}
        />
      </div>

      {/* Weather Factors */}
      <div className="grid grid-cols-3 gap-2 mb-4">
        <div className="p-2 rounded-lg bg-white/5 text-center">
          <Thermometer className="w-4 h-4 mx-auto text-orange-400 mb-1" />
          <div className="text-sm font-bold text-white">{data.weather.track_temp}°C</div>
          <div className="text-xs text-gray-500">Track</div>
        </div>
        <div className="p-2 rounded-lg bg-white/5 text-center">
          <Wind className="w-4 h-4 mx-auto text-blue-400 mb-1" />
          <div className="text-sm font-bold text-white">{data.weather.ambient_temp}°C</div>
          <div className="text-xs text-gray-500">Ambient</div>
        </div>
        <div className="p-2 rounded-lg bg-white/5 text-center">
          <Droplets className="w-4 h-4 mx-auto text-cyan-400 mb-1" />
          <div className="text-sm font-bold text-white">{data.weather.humidity}%</div>
          <div className="text-xs text-gray-500">Humidity</div>
        </div>
      </div>

      {/* Performance Impact */}
      <div className="p-3 rounded-lg bg-white/5 border border-white/10">
        <p className="text-xs text-gray-400 mb-1">Performance Impact</p>
        <p className="text-sm text-white">{data.performance_impact}</p>
      </div>

      {/* Recommendation */}
      <div className="mt-3 p-2 rounded-lg bg-toyota-red/10 border border-toyota-red/30">
        <p className="text-xs text-toyota-red">{data.recommendation}</p>
      </div>
    </div>
  );
}
