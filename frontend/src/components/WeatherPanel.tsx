import { useEffect, useState } from 'react';
import { fetchWeather } from '../api';
import { Cloud, Thermometer, Wind, Droplets, Sun } from 'lucide-react';

interface WeatherData {
  track_temp?: number;
  ambient_temp?: number;
  humidity?: number;
  wind_speed?: number;
  conditions?: string;
  [key: string]: unknown;
}

export function WeatherPanel() {
  const [weather, setWeather] = useState<WeatherData | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    const loadWeather = async () => {
      setIsLoading(true);
      try {
        const data = await fetchWeather();
        setWeather(data);
      } catch (error) {
        console.error('Failed to load weather:', error);
      } finally {
        setIsLoading(false);
      }
    };
    loadWeather();
  }, []);

  if (isLoading) {
    return (
      <div className="glass rounded-xl p-4">
        <div className="flex items-center gap-2 mb-3">
          <Cloud className="w-5 h-5 text-blue-400" />
          <h3 className="font-medium text-white">Weather Conditions</h3>
        </div>
        <div className="animate-pulse space-y-2">
          <div className="h-8 bg-white/5 rounded" />
          <div className="h-8 bg-white/5 rounded" />
        </div>
      </div>
    );
  }

  if (!weather || Object.keys(weather).length === 0) {
    return (
      <div className="glass rounded-xl p-4">
        <div className="flex items-center gap-2 mb-3">
          <Cloud className="w-5 h-5 text-blue-400" />
          <h3 className="font-medium text-white">Weather Conditions</h3>
        </div>
        <p className="text-sm text-gray-400">No weather data available</p>
      </div>
    );
  }

  // Extract common weather fields
  const trackTemp = weather.track_temp || weather.TrackTemp || weather.track_temperature;
  const ambientTemp = weather.ambient_temp || weather.AmbientTemp || weather.air_temp;
  const humidity = weather.humidity || weather.Humidity;
  const windSpeed = weather.wind_speed || weather.WindSpeed;

  return (
    <div className="glass rounded-xl p-4">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-blue-500/20 flex items-center justify-center">
            <Sun className="w-5 h-5 text-yellow-400" />
          </div>
          <div>
            <h3 className="font-medium text-white">Weather</h3>
            <p className="text-xs text-gray-400">Track Conditions</p>
          </div>
        </div>
      </div>

      {/* Weather Grid */}
      <div className="grid grid-cols-2 gap-3">
        {/* Track Temperature */}
        {trackTemp !== undefined && (
          <div className="p-3 rounded-lg bg-orange-500/10 border border-orange-500/20">
            <div className="flex items-center gap-2 mb-1">
              <Thermometer className="w-4 h-4 text-orange-400" />
              <span className="text-xs text-gray-400">Track</span>
            </div>
            <p className="text-xl font-bold text-orange-400">
              {typeof trackTemp === 'number' ? Math.round(trackTemp) : trackTemp}°C
            </p>
          </div>
        )}

        {/* Ambient Temperature */}
        {ambientTemp !== undefined && (
          <div className="p-3 rounded-lg bg-blue-500/10 border border-blue-500/20">
            <div className="flex items-center gap-2 mb-1">
              <Thermometer className="w-4 h-4 text-blue-400" />
              <span className="text-xs text-gray-400">Ambient</span>
            </div>
            <p className="text-xl font-bold text-blue-400">
              {typeof ambientTemp === 'number' ? Math.round(ambientTemp) : ambientTemp}°C
            </p>
          </div>
        )}

        {/* Humidity */}
        {humidity !== undefined && (
          <div className="p-3 rounded-lg bg-cyan-500/10 border border-cyan-500/20">
            <div className="flex items-center gap-2 mb-1">
              <Droplets className="w-4 h-4 text-cyan-400" />
              <span className="text-xs text-gray-400">Humidity</span>
            </div>
            <p className="text-xl font-bold text-cyan-400">
              {typeof humidity === 'number' ? Math.round(humidity) : humidity}%
            </p>
          </div>
        )}

        {/* Wind Speed */}
        {windSpeed !== undefined && (
          <div className="p-3 rounded-lg bg-gray-500/10 border border-gray-500/20">
            <div className="flex items-center gap-2 mb-1">
              <Wind className="w-4 h-4 text-gray-400" />
              <span className="text-xs text-gray-400">Wind</span>
            </div>
            <p className="text-xl font-bold text-gray-300">
              {typeof windSpeed === 'number' ? Math.round(windSpeed) : windSpeed} km/h
            </p>
          </div>
        )}
      </div>

      {/* Impact Note */}
      {trackTemp !== undefined && typeof trackTemp === 'number' && (
        <div className="mt-3 p-2 rounded-lg bg-white/5">
          <p className="text-xs text-gray-400">
            {trackTemp > 45
              ? '⚠️ High track temp - expect reduced grip and faster tire wear'
              : trackTemp > 30
              ? '✓ Optimal track temperature for grip'
              : '❄️ Cool track - tires may need extra warmup'}
          </p>
        </div>
      )}
    </div>
  );
}
