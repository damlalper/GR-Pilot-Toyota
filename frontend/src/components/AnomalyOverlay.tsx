import { useEffect, useState } from 'react';
import { useStore } from '../store/useStore';
import { fetchAnomalies } from '../api';
import { AlertTriangle, ChevronDown, ChevronUp } from 'lucide-react';
import { ComponentExplanation } from './ComponentExplanation';

interface Anomaly {
  index: number;
  distance: number;
  anomaly_score: number;
  speed: number;
  throttle: number;
  brake: number;
  steering: number;
  type: string;
  explanation: string;
}

interface AnomalyData {
  user_lap: number;
  detection_method: string;
  anomaly_count: number;
  anomaly_percentage: number;
  total_points: number;
  anomalies: Anomaly[];
}

export function AnomalyOverlay() {
  const { currentLap, lapData } = useStore();
  const [anomalyData, setAnomalyData] = useState<AnomalyData | null>(null);
  const [isExpanded, setIsExpanded] = useState(true);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    const loadAnomalies = async () => {
      if (!currentLap) return;
      setIsLoading(true);
      try {
        const data = await fetchAnomalies(currentLap);
        setAnomalyData(data);
      } catch (error) {
        console.error('Failed to load anomalies:', error);
      } finally {
        setIsLoading(false);
      }
    };
    loadAnomalies();
  }, [currentLap]);

  if (!anomalyData || anomalyData.anomaly_count === 0) {
    return (
      <div className="glass rounded-xl p-4">
        <div className="flex items-center gap-2 text-green-400">
          <AlertTriangle className="w-5 h-5" />
          <span className="font-medium">No Anomalies Detected</span>
        </div>
        <p className="text-xs text-gray-400 mt-1">
          Your lap is performing well compared to the reference.
        </p>
      </div>
    );
  }

  const getPriorityColor = (type: string, score: number) => {
    // Higher negative score = more anomalous
    const absScore = Math.abs(score);
    if (type === 'speed_anomaly' || type === 'throttle_brake_overlap' || absScore > 0.15) return 'bg-red-500';
    if (type === 'steering_correction' || absScore > 0.10) return 'bg-orange-500';
    return 'bg-yellow-500';
  };

  const getSeverity = (type: string, score: number) => {
    const absScore = Math.abs(score);
    if (type === 'speed_anomaly' || type === 'throttle_brake_overlap' || absScore > 0.15) return 'critical';
    if (type === 'steering_correction' || absScore > 0.10) return 'warning';
    return 'minor';
  };

  return (
    <div className="glass rounded-xl overflow-hidden">
      {/* Header */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full p-4 flex items-center justify-between hover:bg-white/5 transition-colors"
      >
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-red-500/20 flex items-center justify-center">
            <AlertTriangle className="w-5 h-5 text-red-400" />
          </div>
          <div className="text-left flex-1">
            <div className="flex items-center gap-2">
              <h3 className="font-bold text-white">Anomaly Detection</h3>
              <ComponentExplanation componentName="anomaly_detection" />
            </div>
            <p className="text-xs text-gray-400">
              {anomalyData.anomaly_count} anomalies ({anomalyData.anomaly_percentage.toFixed(1)}% of lap)
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className="px-2 py-1 rounded-full bg-red-500/20 text-red-400 text-xs font-medium">
            {anomalyData.anomaly_count} issues
          </span>
          {isExpanded ? (
            <ChevronUp className="w-5 h-5 text-gray-400" />
          ) : (
            <ChevronDown className="w-5 h-5 text-gray-400" />
          )}
        </div>
      </button>

      {/* Content */}
      {isExpanded && (
        <div className="px-4 pb-4 space-y-3">
          {/* Summary Bar */}
          <div className="flex gap-2">
            <div className="flex-1 text-center p-2 rounded-lg bg-red-500/10">
              <p className="text-xs text-gray-400">Critical</p>
              <p className="text-lg font-bold text-red-400">
                {anomalyData.anomalies.filter((a) => getSeverity(a.type, a.anomaly_score) === 'critical').length}
              </p>
            </div>
            <div className="flex-1 text-center p-2 rounded-lg bg-orange-500/10">
              <p className="text-xs text-gray-400">Warning</p>
              <p className="text-lg font-bold text-orange-400">
                {anomalyData.anomalies.filter((a) => getSeverity(a.type, a.anomaly_score) === 'warning').length}
              </p>
            </div>
            <div className="flex-1 text-center p-2 rounded-lg bg-yellow-500/10">
              <p className="text-xs text-gray-400">Minor</p>
              <p className="text-lg font-bold text-yellow-400">
                {anomalyData.anomalies.filter((a) => getSeverity(a.type, a.anomaly_score) === 'minor').length}
              </p>
            </div>
          </div>

          {/* Anomaly List */}
          <div className="space-y-2 max-h-60 overflow-y-auto">
            {anomalyData.anomalies.slice(0, 10).map((anomaly, i) => (
              <div
                key={i}
                className="p-3 rounded-lg bg-white/5 hover:bg-white/10 transition-colors cursor-pointer"
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <div className={`w-2 h-2 rounded-full ${getPriorityColor(anomaly.type, anomaly.anomaly_score)}`} />
                    <span className="text-sm font-medium text-white">
                      {Math.round(anomaly.distance)}m
                    </span>
                  </div>
                  <span className="px-2 py-1 rounded-full bg-white/10 text-xs font-medium text-white">
                    {anomaly.type.replace(/_/g, ' ')}
                  </span>
                </div>
                <div className="flex justify-between text-xs mb-2">
                  <span className="text-gray-400">Speed: <span className="text-white">{Math.round(anomaly.speed)} km/h</span></span>
                  <span className="text-gray-400">Throttle: <span className="text-white">{Math.round(anomaly.throttle)}%</span></span>
                  <span className="text-gray-400">Brake: <span className="text-white">{Math.round(anomaly.brake)}</span></span>
                </div>
                <p className="text-xs text-gray-300 italic">{anomaly.explanation}</p>
              </div>
            ))}
          </div>

          {anomalyData.anomaly_count > 10 && (
            <p className="text-xs text-gray-500 text-center">
              + {anomalyData.anomaly_count - 10} more anomalies
            </p>
          )}
        </div>
      )}
    </div>
  );
}
