import { useState, useEffect } from 'react';
import { useStore } from '../store/useStore';
import { fetchDriverDNA } from '../api';
import { Fingerprint, Loader2 } from 'lucide-react';
import { ComponentExplanation } from './ComponentExplanation';

interface DNAData {
  lap: number;
  driver_type: string;
  driver_description: string;
  dna_scores: {
    aggression: number;
    smoothness: number;
    consistency: number;
    risk_tolerance?: number;
    overall?: number;
  };
  recommendations: string[];
  metrics: any;
}

export function DriverDNA() {
  const { currentLap } = useStore();
  const [data, setData] = useState<DNAData | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (!currentLap) return;
    setIsLoading(true);
    fetchDriverDNA(currentLap)
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

  const styleColors: Record<string, string> = {
    aggressive: 'text-red-400',
    balanced: 'text-yellow-400',
    conservative: 'text-green-400',
    smooth: 'text-blue-400',
  };

  return (
    <div className="glass rounded-xl p-4">
      <div className="flex items-center gap-2 mb-4">
        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
          <Fingerprint className="w-5 h-5 text-white" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <h3 className="font-medium text-white">Driver DNA</h3>
            <ComponentExplanation componentName="driver_dna" />
          </div>
          <p className="text-xs text-gray-400">Driving style fingerprint</p>
        </div>
      </div>

      {/* Driver Style Badge */}
      <div className="text-center mb-4">
        <span className={`text-2xl font-bold uppercase ${styleColors[data.driver_type.toLowerCase()] || 'text-white'}`}>
          {data.driver_type}
        </span>
        <p className="text-xs text-gray-500 mt-1">{data.driver_description}</p>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-3 gap-2 mb-4">
        <div className="p-2 rounded-lg bg-white/5 text-center">
          <div className="text-lg font-bold text-red-400">{data.dna_scores.aggression.toFixed(1)}%</div>
          <div className="text-xs text-gray-500">Aggression</div>
        </div>
        <div className="p-2 rounded-lg bg-white/5 text-center">
          <div className="text-lg font-bold text-blue-400">{data.dna_scores.smoothness.toFixed(1)}%</div>
          <div className="text-xs text-gray-500">Smoothness</div>
        </div>
        <div className="p-2 rounded-lg bg-white/5 text-center">
          <div className="text-lg font-bold text-green-400">{data.dna_scores.consistency.toFixed(1)}%</div>
          <div className="text-xs text-gray-500">Consistency</div>
        </div>
      </div>

      {/* Additional DNA Scores */}
      {(data.dna_scores.risk_tolerance !== undefined || data.dna_scores.overall !== undefined) && (
        <div className="grid grid-cols-2 gap-2 mb-4">
          {data.dna_scores.risk_tolerance !== undefined && (
            <div className="p-2 rounded-lg bg-white/5 text-center">
              <div className="text-lg font-bold text-yellow-400">{data.dna_scores.risk_tolerance.toFixed(1)}%</div>
              <div className="text-xs text-gray-500">Risk Tolerance</div>
            </div>
          )}
          {data.dna_scores.overall !== undefined && (
            <div className="p-2 rounded-lg bg-white/5 text-center">
              <div className="text-lg font-bold text-purple-400">{data.dna_scores.overall.toFixed(1)}%</div>
              <div className="text-xs text-gray-500">Overall</div>
            </div>
          )}
        </div>
      )}

      {/* Recommendations */}
      {data.recommendations.length > 0 && (
        <div className="border-t border-white/10 pt-3">
          <p className="text-xs text-gray-400 mb-2">Recommendations</p>
          <ul className="space-y-1">
            {data.recommendations.slice(0, 2).map((rec, i) => (
              <li key={i} className="text-xs text-gray-300 flex items-start gap-1">
                <span className="text-toyota-red">•</span>
                {rec}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
