import { useMemo } from 'react';
import { useStore } from '../store/useStore';
import { Target, AlertTriangle } from 'lucide-react';
import { ComponentExplanation } from './ComponentExplanation';

interface GGPoint {
  lateralG: number;
  longitudinalG: number;
  speed: number;
  distance: number;
  totalG: number;
  isOverLimit: boolean;
}

export function GGDiagram() {
  const { lapData, currentIndex } = useStore();

  const ggData = useMemo(() => {
    if (!lapData?.data || lapData.data.length === 0) return null;

    const points: GGPoint[] = [];
    const sampleStep = Math.max(1, Math.floor(lapData.data.length / 200)); // Sample 200 points

    for (let i = 0; i < lapData.data.length; i += sampleStep) {
      const point = lapData.data[i];
      const lateralG = point.accy_can || 0;
      const longitudinalG = point.accx_can || 0;
      const totalG = Math.sqrt(lateralG * lateralG + longitudinalG * longitudinalG);

      points.push({
        lateralG,
        longitudinalG,
        speed: point.speed || 0,
        distance: point.distance || 0,
        totalG,
        isOverLimit: totalG > 1.2, // GR86 limit ~1.2G
      });
    }

    return points;
  }, [lapData]);

  const currentPoint = useMemo(() => {
    if (!lapData?.data || !currentIndex) return null;
    const point = lapData.data[Math.min(currentIndex, lapData.data.length - 1)];
    return {
      lateralG: point.accy_can || 0,
      longitudinalG: point.accx_can || 0,
      totalG: Math.sqrt(
        (point.accy_can || 0) ** 2 + (point.accx_can || 0) ** 2
      ),
    };
  }, [lapData, currentIndex]);

  if (!ggData) return null;

  const maxG = 1.5; // Display range
  const scale = 100; // Pixels per G
  const centerX = 150;
  const centerY = 150;

  // Calculate grip limit circle (1.2G for GR86)
  const gripLimit = 1.2;

  // Stats
  const overLimitPoints = ggData.filter(p => p.isOverLimit).length;
  const utilizationPercent = ((ggData.reduce((sum, p) => sum + p.totalG, 0) / ggData.length) / gripLimit * 100);

  return (
    <div className="glass rounded-xl p-4">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-cyan-600 flex items-center justify-center">
            <Target className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="font-medium text-white">G-G Diagram</h3>
              <ComponentExplanation componentName="gg_diagram" />
            </div>
            <p className="text-xs text-gray-400">Friction circle analysis</p>
          </div>
        </div>
      </div>

      {/* Stats Bar */}
      <div className="grid grid-cols-2 gap-2 mb-4">
        <div className="p-2 rounded-lg bg-blue-500/20 text-center">
          <div className="text-sm font-bold text-blue-400">{utilizationPercent.toFixed(1)}%</div>
          <div className="text-xs text-gray-400">Grip Utilization</div>
        </div>
        <div className="p-2 rounded-lg bg-red-500/20 text-center">
          <div className="text-sm font-bold text-red-400">{overLimitPoints}</div>
          <div className="text-xs text-gray-400">Over Limit Events</div>
        </div>
      </div>

      {/* G-G Plot */}
      <div className="relative bg-black/30 rounded-lg p-4">
        <svg width="300" height="300" className="mx-auto">
          {/* Grid lines */}
          <line x1={centerX} y1="0" x2={centerX} y2="300" stroke="#333" strokeWidth="1" />
          <line x1="0" y1={centerY} x2="300" y2={centerY} stroke="#333" strokeWidth="1" />

          {/* Grid circles (0.5G, 1.0G, 1.5G) */}
          <circle cx={centerX} cy={centerY} r={scale * 0.5} fill="none" stroke="#2a2a2a" strokeWidth="1" />
          <circle cx={centerX} cy={centerY} r={scale * 1.0} fill="none" stroke="#3a3a3a" strokeWidth="1" strokeDasharray="4" />
          <circle cx={centerX} cy={centerY} r={scale * 1.5} fill="none" stroke="#2a2a2a" strokeWidth="1" />

          {/* Grip limit circle (1.2G) */}
          <circle
            cx={centerX}
            cy={centerY}
            r={scale * gripLimit}
            fill="none"
            stroke="#eb0a1e"
            strokeWidth="2"
            strokeDasharray="8 4"
          />

          {/* Data points */}
          {ggData.map((point, i) => {
            const x = centerX + point.lateralG * scale;
            const y = centerY - point.longitudinalG * scale; // Invert Y for screen coordinates

            const color = point.isOverLimit
              ? '#ef4444' // Red for over limit
              : point.totalG > 1.0
              ? '#f59e0b' // Orange for high usage
              : '#22c55e'; // Green for safe

            return (
              <circle
                key={i}
                cx={x}
                cy={y}
                r="2"
                fill={color}
                opacity="0.6"
              />
            );
          })}

          {/* Current point (larger, animated) */}
          {currentPoint && (
            <>
              <circle
                cx={centerX + currentPoint.lateralG * scale}
                cy={centerY - currentPoint.longitudinalG * scale}
                r="8"
                fill="none"
                stroke="#00ffff"
                strokeWidth="2"
              >
                <animate
                  attributeName="r"
                  values="6;10;6"
                  dur="1.5s"
                  repeatCount="indefinite"
                />
              </circle>
              <circle
                cx={centerX + currentPoint.lateralG * scale}
                cy={centerY - currentPoint.longitudinalG * scale}
                r="4"
                fill="#00ffff"
              />
            </>
          )}

          {/* Axis labels */}
          <text x={centerX + scale * 1.3} y={centerY + 5} fill="#666" fontSize="12" textAnchor="middle">
            +Lat
          </text>
          <text x={centerX - scale * 1.3} y={centerY + 5} fill="#666" fontSize="12" textAnchor="middle">
            -Lat
          </text>
          <text x={centerX + 5} y={centerY - scale * 1.3} fill="#666" fontSize="12" textAnchor="start">
            +Long
          </text>
          <text x={centerX + 5} y={centerY + scale * 1.3} fill="#666" fontSize="12" textAnchor="start">
            -Long
          </text>
        </svg>

        {/* Legend */}
        <div className="absolute top-2 right-2 bg-black/60 p-2 rounded text-xs space-y-1">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-green-500" />
            <span className="text-gray-300">Safe (&lt;1.0G)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-orange-500" />
            <span className="text-gray-300">High (1.0-1.2G)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-red-500" />
            <span className="text-gray-300">Over Limit (&gt;1.2G)</span>
          </div>
          <div className="flex items-center gap-2 pt-1 border-t border-white/10">
            <div className="w-3 h-3 rounded-full border-2 border-toyota-red" />
            <span className="text-toyota-red font-semibold">Grip Limit</span>
          </div>
        </div>
      </div>

      {/* Current G-Force Display */}
      {currentPoint && (
        <div className="mt-4 grid grid-cols-3 gap-2">
          <div className="p-2 rounded-lg bg-white/5 text-center">
            <div className="text-xs text-gray-400 mb-1">Lateral G</div>
            <div className="text-lg font-bold text-cyan-400">{currentPoint.lateralG.toFixed(2)}</div>
          </div>
          <div className="p-2 rounded-lg bg-white/5 text-center">
            <div className="text-xs text-gray-400 mb-1">Long. G</div>
            <div className="text-lg font-bold text-green-400">{currentPoint.longitudinalG.toFixed(2)}</div>
          </div>
          <div className="p-2 rounded-lg bg-white/5 text-center">
            <div className="text-xs text-gray-400 mb-1">Total G</div>
            <div className={`text-lg font-bold ${currentPoint.totalG > gripLimit ? 'text-red-400' : 'text-white'}`}>
              {currentPoint.totalG.toFixed(2)}
            </div>
          </div>
        </div>
      )}

      {/* Engineering Note */}
      {overLimitPoints > 10 && (
        <div className="mt-3 p-2 rounded-lg bg-red-500/20 border border-red-500/30">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-red-400" />
            <p className="text-xs text-red-300">
              <span className="font-semibold">{overLimitPoints} tire scrub events detected.</span> Excessive lateral G
              combined with steering angle causes premature tire wear.
            </p>
          </div>
        </div>
      )}

      {/* Formula */}
      <div className="mt-3 text-xs text-gray-500 italic text-center">
        Total G = √(Lateral² + Longitudinal²) | GR86 Limit ≈ 1.2G
      </div>
    </div>
  );
}
