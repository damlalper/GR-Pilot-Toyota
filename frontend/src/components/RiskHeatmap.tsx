import { useState, useEffect } from 'react';
import { useStore } from '../store/useStore';
import { fetchRiskHeatmap } from '../api';
import { AlertTriangle, Loader2, MapPin } from 'lucide-react';
import { ComponentExplanation } from './ComponentExplanation';

interface RiskData {
  lap: number;
  overall_risk: number;
  risk_level: string;
  zones: Array<{
    zone_id: number;
    distance_start: number;
    distance_end: number;
    risk_score: number;
    risk_type: string;
    factors: string[];
  }>;
  high_risk_count: number;
  medium_risk_count: number;
  recommendations: string[];
}

export function RiskHeatmap() {
  const { currentLap } = useStore();
  const [data, setData] = useState<RiskData | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (!currentLap) return;
    setIsLoading(true);
    fetchRiskHeatmap(currentLap)
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

  if (!data || !data.zones) return null;

  const getRiskColor = (score: number) => {
    if (score >= 70) return 'bg-red-500';
    if (score >= 40) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  const getRiskTextColor = (score: number) => {
    if (score >= 70) return 'text-red-400';
    if (score >= 40) return 'text-yellow-400';
    return 'text-green-400';
  };

  return (
    <div className="glass rounded-xl p-4">
      <div className="flex items-center gap-2 mb-4">
        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-red-500 to-orange-600 flex items-center justify-center">
          <AlertTriangle className="w-5 h-5 text-white" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <h3 className="font-medium text-white">Risk Heatmap</h3>
            <ComponentExplanation componentName="risk_heatmap" />
          </div>
          <p className="text-xs text-gray-400">Spin/Lock-up risk analysis</p>
        </div>
      </div>

      {/* Overall Risk Score */}
      <div className="text-center mb-4">
        <div className={`text-4xl font-bold ${getRiskTextColor(data.overall_risk)}`}>
          {data.overall_risk}%
        </div>
        <div className="text-sm text-gray-400 uppercase">{data.risk_level} Risk</div>
      </div>

      {/* Risk Summary */}
      <div className="grid grid-cols-2 gap-2 mb-4">
        <div className="p-2 rounded-lg bg-red-500/20 text-center">
          <div className="text-lg font-bold text-red-400">{data.high_risk_count}</div>
          <div className="text-xs text-gray-400">High Risk Zones</div>
        </div>
        <div className="p-2 rounded-lg bg-yellow-500/20 text-center">
          <div className="text-lg font-bold text-yellow-400">{data.medium_risk_count}</div>
          <div className="text-xs text-gray-400">Medium Risk Zones</div>
        </div>
      </div>

      {/* Risk Zones Heatmap Bar */}
      <div className="mb-4">
        <p className="text-xs text-gray-400 mb-2">Track Risk Distribution</p>
        <div className="h-6 rounded-lg overflow-hidden flex">
          {data.zones.map((zone) => (
            <div
              key={zone.zone_id}
              className={`${getRiskColor(zone.risk_score)} transition-all hover:opacity-80`}
              style={{ flex: 1 }}
              title={`Zone ${zone.zone_id}: ${zone.risk_score}% - ${zone.risk_type}`}
            />
          ))}
        </div>
        <div className="flex justify-between text-xs text-gray-500 mt-1">
          <span>Start</span>
          <span>Finish</span>
        </div>
      </div>

      {/* High Risk Zones Detail */}
      <div className="space-y-2 mb-4">
        <p className="text-xs text-gray-400">Critical Zones</p>
        {data.zones
          .filter(z => z.risk_score >= 60)
          .slice(0, 3)
          .map((zone) => (
            <div key={zone.zone_id} className="p-2 rounded-lg bg-white/5 flex items-start gap-2">
              <MapPin className={`w-4 h-4 mt-0.5 ${getRiskTextColor(zone.risk_score)}`} />
              <div className="flex-1">
                <div className="flex justify-between">
                  <span className="text-sm text-white">Zone {zone.zone_id}</span>
                  <span className={`text-sm font-bold ${getRiskTextColor(zone.risk_score)}`}>
                    {zone.risk_score}%
                  </span>
                </div>
                <p className="text-xs text-gray-400 capitalize">{zone.risk_type}</p>
                {zone.factors && zone.factors.length > 0 && (
                  <div className="flex flex-wrap gap-1 mt-1">
                    {zone.factors.map((f, i) => (
                      <span key={i} className="text-xs px-1 py-0.5 rounded bg-white/10 text-gray-300">
                        {f}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}
      </div>

      {/* Recommendations */}
      {data.recommendations && data.recommendations.length > 0 && (
        <div className="border-t border-white/10 pt-3">
          <p className="text-xs text-gray-400 mb-2">Safety Tips</p>
          <ul className="space-y-1">
            {data.recommendations.slice(0, 2).map((rec, i) => (
              <li key={i} className="text-xs text-gray-300 flex items-start gap-1">
                <span className="text-orange-400">!</span>
                {rec}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Single Recommendation String */}
      {data.recommendation && !data.recommendations && (
        <div className="border-t border-white/10 pt-3">
          <p className="text-xs text-gray-400 mb-2">Safety Tip</p>
          <p className="text-xs text-gray-300 flex items-start gap-1">
            <span className="text-orange-400">!</span>
            {data.recommendation}
          </p>
        </div>
      )}
    </div>
  );
}
