import { useMemo } from 'react';
import { useStore } from '../store/useStore';
import { MapPin } from 'lucide-react';
import { ComponentExplanation } from './ComponentExplanation';

export function TrackMap() {
  const { lapData, currentIndex } = useStore();

  const { trackPoints, carPosition, bounds } = useMemo(() => {
    if (!lapData?.data || lapData.data.length === 0) {
      return { trackPoints: [], carPosition: null, bounds: { minX: 0, maxX: 100, minY: 0, maxY: 100 } };
    }

    const minX = Math.min(...lapData.data.map((p) => p.WorldPositionX));
    const maxX = Math.max(...lapData.data.map((p) => p.WorldPositionX));
    const minY = Math.min(...lapData.data.map((p) => p.WorldPositionY));
    const maxY = Math.max(...lapData.data.map((p) => p.WorldPositionY));

    const padding = 20;
    const width = 300;
    const height = 200;

    const scaleX = (width - padding * 2) / (maxX - minX || 1);
    const scaleY = (height - padding * 2) / (maxY - minY || 1);
    const scale = Math.min(scaleX, scaleY);

    const points = lapData.data.map((p, i) => ({
      x: padding + (p.WorldPositionX - minX) * scale,
      y: height - padding - (p.WorldPositionY - minY) * scale,
      speed: p.speed,
      index: i,
    }));

    const idx = Math.min(currentIndex, lapData.data.length - 1);
    const car = points[idx];

    return {
      trackPoints: points,
      carPosition: car,
      bounds: { minX, maxX, minY, maxY },
    };
  }, [lapData, currentIndex]);

  const maxSpeed = useMemo(() => {
    if (!lapData?.data) return 200;
    return Math.max(...lapData.data.map((p) => p.speed || 0));
  }, [lapData]);

  const getSpeedColor = (speed: number) => {
    const ratio = speed / maxSpeed;
    if (ratio > 0.8) return '#EB0A1E';
    if (ratio > 0.6) return '#ffa500';
    if (ratio > 0.4) return '#ffff00';
    return '#00ff88';
  };

  if (trackPoints.length === 0) {
    return (
      <div className="glass rounded-xl p-4 h-full flex items-center justify-center">
        <p className="text-gray-400">No track data</p>
      </div>
    );
  }

  // Create SVG path
  const pathD = trackPoints
    .map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`)
    .join(' ') + ' Z';

  return (
    <div className="glass rounded-xl p-4">
      <div className="flex items-center gap-2 mb-3">
        <h4 className="text-sm font-medium text-gray-300 flex items-center gap-2">
          <MapPin className="w-4 h-4 text-toyota-red" />
          Track Map
        </h4>
        <ComponentExplanation componentName="track_map" />
      </div>

      <svg
        viewBox="0 0 300 200"
        className="w-full h-auto"
        style={{ background: 'rgba(0,0,0,0.3)', borderRadius: '8px' }}
      >
        {/* Track outline */}
        <path
          d={pathD}
          fill="none"
          stroke="#333"
          strokeWidth="12"
          strokeLinecap="round"
          strokeLinejoin="round"
        />

        {/* Track surface */}
        <path
          d={pathD}
          fill="none"
          stroke="#2a2a2a"
          strokeWidth="10"
          strokeLinecap="round"
          strokeLinejoin="round"
        />

        {/* Speed-colored racing line */}
        {trackPoints.slice(0, -1).map((point, i) => (
          <line
            key={i}
            x1={point.x}
            y1={point.y}
            x2={trackPoints[i + 1].x}
            y2={trackPoints[i + 1].y}
            stroke={getSpeedColor(point.speed)}
            strokeWidth="3"
            strokeLinecap="round"
          />
        ))}

        {/* Start/Finish line */}
        {trackPoints.length > 0 && (
          <circle
            cx={trackPoints[0].x}
            cy={trackPoints[0].y}
            r="6"
            fill="#ffffff"
            stroke="#000"
            strokeWidth="2"
          />
        )}

        {/* Car position */}
        {carPosition && (
          <>
            {/* Glow effect */}
            <circle
              cx={carPosition.x}
              cy={carPosition.y}
              r="12"
              fill="rgba(235, 10, 30, 0.3)"
            />
            {/* Car marker */}
            <circle
              cx={carPosition.x}
              cy={carPosition.y}
              r="6"
              fill="#EB0A1E"
              stroke="#fff"
              strokeWidth="2"
            />
          </>
        )}

        {/* Speed legend */}
        <g transform="translate(10, 170)">
          <rect x="0" y="0" width="60" height="20" fill="rgba(0,0,0,0.5)" rx="4" />
          <rect x="5" y="5" width="10" height="10" fill="#00ff88" />
          <text x="18" y="13" fill="#999" fontSize="8">Slow</text>
          <rect x="35" y="5" width="10" height="10" fill="#EB0A1E" />
          <text x="48" y="13" fill="#999" fontSize="8">Fast</text>
        </g>
      </svg>

      {/* Progress indicator */}
      <div className="mt-3">
        <div className="flex justify-between text-xs text-gray-400 mb-1">
          <span>Progress</span>
          <span>{Math.round((currentIndex / (trackPoints.length - 1)) * 100)}%</span>
        </div>
        <div className="h-1.5 bg-gray-800 rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-toyota-red to-orange-500 transition-all duration-100"
            style={{ width: `${(currentIndex / (trackPoints.length - 1)) * 100}%` }}
          />
        </div>
      </div>
    </div>
  );
}
