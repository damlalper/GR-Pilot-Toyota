import { useMemo } from 'react';
import { useStore } from '../store/useStore';
import { Gauge, Activity, Zap, Wind } from 'lucide-react';

function SpeedGauge({ value, max }: { value: number; max: number }) {
  const percentage = Math.min((value / max) * 100, 100);
  const circumference = 2 * Math.PI * 45;
  const strokeDashoffset = circumference - (percentage / 100) * circumference * 0.75;

  return (
    <div className="relative w-32 h-32">
      <svg className="w-full h-full -rotate-135" viewBox="0 0 100 100">
        {/* Background arc */}
        <circle
          cx="50"
          cy="50"
          r="45"
          fill="none"
          stroke="#2d2d2d"
          strokeWidth="8"
          strokeDasharray={circumference * 0.75}
          strokeLinecap="round"
        />
        {/* Value arc */}
        <circle
          cx="50"
          cy="50"
          r="45"
          fill="none"
          stroke="url(#speedGradient)"
          strokeWidth="8"
          strokeDasharray={circumference * 0.75}
          strokeDashoffset={strokeDashoffset}
          strokeLinecap="round"
          className="transition-all duration-300"
        />
        <defs>
          <linearGradient id="speedGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#00ff88" />
            <stop offset="50%" stopColor="#ffaa00" />
            <stop offset="100%" stopColor="#EB0A1E" />
          </linearGradient>
        </defs>
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-3xl font-bold text-white">{Math.round(value)}</span>
        <span className="text-xs text-gray-400">km/h</span>
      </div>
    </div>
  );
}

function MetricCard({
  icon: Icon,
  label,
  value,
  unit,
  color,
}: {
  icon: React.ElementType;
  label: string;
  value: string | number;
  unit: string;
  color: string;
}) {
  return (
    <div className="glass rounded-lg p-3 flex items-center gap-3">
      <div className={`p-2 rounded-lg ${color}`}>
        <Icon className="w-5 h-5 text-white" />
      </div>
      <div>
        <p className="text-xs text-gray-400">{label}</p>
        <p className="text-lg font-bold text-white">
          {value} <span className="text-xs text-gray-400">{unit}</span>
        </p>
      </div>
    </div>
  );
}

function ProgressBar({ value, max, label, color }: { value: number; max: number; label: string; color: string }) {
  const percentage = Math.min((value / max) * 100, 100);

  return (
    <div className="space-y-1">
      <div className="flex justify-between text-xs">
        <span className="text-gray-400">{label}</span>
        <span className="text-white font-medium">{Math.round(value)}%</span>
      </div>
      <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
        <div
          className={`h-full ${color} transition-all duration-200`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}

export function TelemetryPanel() {
  const { lapData, currentIndex } = useStore();

  const currentData = useMemo(() => {
    if (!lapData?.data || lapData.data.length === 0) return null;
    const idx = Math.min(currentIndex, lapData.data.length - 1);
    return lapData.data[idx];
  }, [lapData, currentIndex]);

  if (!currentData) {
    return (
      <div className="glass rounded-xl p-4 h-full flex items-center justify-center">
        <p className="text-gray-400">Select a lap to view telemetry</p>
      </div>
    );
  }

  return (
    <div className="glass rounded-xl p-4 space-y-4">
      <h3 className="text-lg font-bold text-white flex items-center gap-2">
        <Activity className="w-5 h-5 text-toyota-red" />
        Live Telemetry
      </h3>

      {/* Speed Gauge */}
      <div className="flex justify-center">
        <SpeedGauge value={currentData.speed || 0} max={300} />
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-2 gap-2">
        <MetricCard
          icon={Gauge}
          label="RPM"
          value={Math.round(currentData.nmot || 0)}
          unit=""
          color="bg-orange-600"
        />
        <MetricCard
          icon={Zap}
          label="Gear"
          value={Math.round(currentData.gear || 0)}
          unit=""
          color="bg-blue-600"
        />
      </div>

      {/* Progress Bars */}
      <div className="space-y-3">
        <ProgressBar
          value={currentData.ath || 0}
          max={100}
          label="Throttle"
          color="bg-green-500"
        />
        <ProgressBar
          value={Math.min((currentData.pbrake_f || 0) * 2, 100)}
          max={100}
          label="Brake"
          color="bg-toyota-red"
        />
      </div>

      {/* Steering */}
      <div className="space-y-1">
        <p className="text-xs text-gray-400">Steering Angle</p>
        <div className="relative h-6 bg-gray-800 rounded-full">
          <div className="absolute inset-y-0 left-1/2 w-0.5 bg-gray-600" />
          <div
            className="absolute top-1/2 -translate-y-1/2 w-4 h-4 bg-toyota-red rounded-full transition-all duration-100"
            style={{
              left: `${50 + (currentData.Steering_Angle || 0) / 5}%`,
              transform: 'translate(-50%, -50%)',
            }}
          />
        </div>
        <div className="flex justify-between text-xs text-gray-500">
          <span>-250°</span>
          <span>{Math.round(currentData.Steering_Angle || 0)}°</span>
          <span>+250°</span>
        </div>
      </div>

      {/* Distance */}
      <div className="pt-2 border-t border-white/10">
        <div className="flex justify-between items-center">
          <div className="flex items-center gap-2">
            <Wind className="w-4 h-4 text-gray-400" />
            <span className="text-xs text-gray-400">Distance</span>
          </div>
          <span className="text-sm font-medium text-white">
            {Math.round(currentData.distance || 0)} m
          </span>
        </div>
      </div>
    </div>
  );
}
