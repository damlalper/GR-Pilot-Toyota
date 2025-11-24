import { useMemo } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  AreaChart,
  Area,
  ReferenceLine,
} from 'recharts';
import { useStore } from '../store/useStore';
import { TrendingUp, Gauge, Footprints, RotateCw } from 'lucide-react';
import { ComponentExplanation } from './ComponentExplanation';

function ChartCard({
  title,
  icon: Icon,
  children,
}: {
  title: string;
  icon: React.ElementType;
  children: React.ReactNode;
}) {
  return (
    <div className="glass rounded-xl p-4">
      <h4 className="text-sm font-medium text-gray-300 mb-3 flex items-center gap-2">
        <Icon className="w-4 h-4 text-toyota-red" />
        {title}
      </h4>
      <div className="h-40">{children}</div>
    </div>
  );
}

export function TelemetryCharts() {
  const { lapData, currentIndex } = useStore();

  const chartData = useMemo(() => {
    if (!lapData?.data) return [];
    // Sample data for performance
    const step = Math.max(1, Math.floor(lapData.data.length / 100));
    return lapData.data
      .filter((_, i) => i % step === 0)
      .map((point, i) => ({
        index: i,
        distance: Math.round(point.distance),
        speed: point.speed || 0,
        rpm: point.nmot || 0,
        throttle: point.ath || 0,
        brake: (point.pbrake_f || 0) * 2,
        steering: point.Steering_Angle || 0,
      }));
  }, [lapData]);

  const currentDistance = useMemo(() => {
    if (!lapData?.data || lapData.data.length === 0) return 0;
    const idx = Math.min(currentIndex, lapData.data.length - 1);
    return lapData.data[idx].distance || 0;
  }, [lapData, currentIndex]);

  if (chartData.length === 0) {
    return (
      <div className="glass rounded-xl p-4 h-full flex items-center justify-center">
        <p className="text-gray-400">No chart data available</p>
      </div>
    );
  }

  const customTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="glass rounded-lg p-2 text-xs">
          <p className="text-gray-400">Distance: {label}m</p>
          {payload.map((entry: any, index: number) => (
            <p key={index} style={{ color: entry.color }}>
              {entry.name}: {Math.round(entry.value)}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="glass rounded-xl p-4 space-y-4">
      <div className="flex items-center gap-2 mb-4">
        <h3 className="text-lg font-semibold text-white">Telemetry</h3>
        <ComponentExplanation componentName="telemetry_charts" />
      </div>
      {/* Speed Chart */}
      <ChartCard title="Speed (km/h)" icon={TrendingUp}>
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={chartData}>
            <defs>
              <linearGradient id="speedGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#00ffff" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#00ffff" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#333" />
            <XAxis dataKey="distance" stroke="#666" tick={{ fontSize: 10 }} />
            <YAxis stroke="#666" tick={{ fontSize: 10 }} />
            <Tooltip content={customTooltip} />
            <ReferenceLine x={Math.round(currentDistance)} stroke="#EB0A1E" strokeWidth={2} />
            <Area
              type="monotone"
              dataKey="speed"
              stroke="#00ffff"
              fill="url(#speedGradient)"
              strokeWidth={2}
            />
          </AreaChart>
        </ResponsiveContainer>
      </ChartCard>

      {/* RPM Chart */}
      <ChartCard title="RPM" icon={Gauge}>
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={chartData}>
            <defs>
              <linearGradient id="rpmGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#ffa500" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#ffa500" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#333" />
            <XAxis dataKey="distance" stroke="#666" tick={{ fontSize: 10 }} />
            <YAxis stroke="#666" tick={{ fontSize: 10 }} />
            <Tooltip content={customTooltip} />
            <ReferenceLine x={Math.round(currentDistance)} stroke="#EB0A1E" strokeWidth={2} />
            <Area
              type="monotone"
              dataKey="rpm"
              stroke="#ffa500"
              fill="url(#rpmGradient)"
              strokeWidth={2}
            />
          </AreaChart>
        </ResponsiveContainer>
      </ChartCard>

      {/* Throttle & Brake Chart */}
      <ChartCard title="Throttle & Brake" icon={Footprints}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#333" />
            <XAxis dataKey="distance" stroke="#666" tick={{ fontSize: 10 }} />
            <YAxis stroke="#666" tick={{ fontSize: 10 }} domain={[0, 100]} />
            <Tooltip content={customTooltip} />
            <ReferenceLine x={Math.round(currentDistance)} stroke="#EB0A1E" strokeWidth={2} />
            <Line
              type="monotone"
              dataKey="throttle"
              stroke="#00ff00"
              strokeWidth={2}
              dot={false}
              name="Throttle"
            />
            <Line
              type="monotone"
              dataKey="brake"
              stroke="#ff0000"
              strokeWidth={2}
              dot={false}
              name="Brake"
            />
          </LineChart>
        </ResponsiveContainer>
      </ChartCard>

      {/* Steering Chart */}
      <ChartCard title="Steering Angle" icon={RotateCw}>
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={chartData}>
            <defs>
              <linearGradient id="steeringGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#ff00ff" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#ff00ff" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#333" />
            <XAxis dataKey="distance" stroke="#666" tick={{ fontSize: 10 }} />
            <YAxis stroke="#666" tick={{ fontSize: 10 }} />
            <Tooltip content={customTooltip} />
            <ReferenceLine x={Math.round(currentDistance)} stroke="#EB0A1E" strokeWidth={2} />
            <ReferenceLine y={0} stroke="#666" />
            <Area
              type="monotone"
              dataKey="steering"
              stroke="#ff00ff"
              fill="url(#steeringGradient)"
              strokeWidth={2}
            />
          </AreaChart>
        </ResponsiveContainer>
      </ChartCard>
    </div>
  );
}
