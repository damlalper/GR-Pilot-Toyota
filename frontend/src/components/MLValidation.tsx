import { useEffect, useState } from 'react';
import { Brain, CheckCircle, Activity } from 'lucide-react';
import { fetchMLValidation } from '../api';
import { ComponentExplanation } from './ComponentExplanation';

interface ModelInfo {
  status: string;
  type: string;
  accuracy?: string;
  mae?: string;
  r2_score?: string;
  clusters?: number;
  silhouette_score?: string;
  description: string;
}

interface MLValidationData {
  available: boolean;
  models: {
    anomaly_detector: ModelInfo;
    lap_predictor: ModelInfo;
    driver_clusterer: ModelInfo;
  };
}

export default function MLValidation() {
  const [data, setData] = useState<MLValidationData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      try {
        const result = await fetchMLValidation();
        setData(result);
      } catch (error) {
        console.error('Error loading ML validation:', error);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  if (loading) {
    return (
      <div className="glass p-6 rounded-xl border border-white/10">
        <div className="animate-pulse">
          <div className="h-4 bg-white/10 rounded w-1/3 mb-4"></div>
          <div className="h-64 bg-white/5 rounded"></div>
        </div>
      </div>
    );
  }

  if (!data || !data.available) {
    return (
      <div className="glass p-6 rounded-xl border border-white/10">
        <div className="flex items-center gap-3 mb-4">
          <Brain className="w-5 h-5 text-purple-400" />
          <h3 className="text-lg font-bold text-white">ML Model Validation</h3>
        </div>
        <p className="text-gray-400">ML models are not available</p>
      </div>
    );
  }

  const models = [
    {
      key: 'anomaly_detector',
      name: 'Anomaly Detector',
      icon: Activity,
      color: 'red',
      ...data.models.anomaly_detector
    },
    {
      key: 'lap_predictor',
      name: 'Lap Time Predictor',
      icon: CheckCircle,
      color: 'blue',
      ...data.models.lap_predictor
    },
    {
      key: 'driver_clusterer',
      name: 'Driver Style Classifier',
      icon: Brain,
      color: 'purple',
      ...data.models.driver_clusterer
    }
  ];

  return (
    <div className="glass p-6 rounded-xl border border-white/10">
      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <div className="p-2 bg-purple-500/20 rounded-lg">
          <Brain className="w-5 h-5 text-purple-400" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <h3 className="text-lg font-bold text-white">ML Model Validation</h3>
            <ComponentExplanation componentName="ml_validation" />
          </div>
          <p className="text-sm text-gray-400">Active Machine Learning Models</p>
        </div>
      </div>

      {/* Models Grid */}
      <div className="space-y-4">
        {models.map((model) => (
          <div key={model.key} className="glass-inner p-4 rounded-lg border border-white/10">
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center gap-3">
                <div className={`p-2 bg-${model.color}-500/20 rounded-lg`}>
                  <model.icon className={`w-4 h-4 text-${model.color}-400`} />
                </div>
                <div>
                  <h4 className="font-semibold text-white">{model.name}</h4>
                  <p className="text-xs text-gray-400 mt-1">{model.type}</p>
                </div>
              </div>
              <span className={`px-2 py-1 rounded-full text-xs ${
                model.status === 'loaded' ? 'bg-green-500/20 text-green-400' : 'bg-gray-500/20 text-gray-400'
              }`}>
                {model.status}
              </span>
            </div>

            <p className="text-sm text-gray-300 mb-3">{model.description}</p>

            {/* Model Metrics */}
            <div className="flex flex-wrap gap-3">
              {model.accuracy && (
                <div className="px-3 py-1 rounded-lg bg-white/5">
                  <span className="text-xs text-gray-400">Accuracy: </span>
                  <span className="text-xs text-white font-semibold">{model.accuracy}</span>
                </div>
              )}
              {model.mae && (
                <div className="px-3 py-1 rounded-lg bg-white/5">
                  <span className="text-xs text-gray-400">MAE: </span>
                  <span className="text-xs text-white font-semibold">{model.mae}</span>
                </div>
              )}
              {model.r2_score && (
                <div className="px-3 py-1 rounded-lg bg-white/5">
                  <span className="text-xs text-gray-400">R² Score: </span>
                  <span className="text-xs text-white font-semibold">{model.r2_score}</span>
                </div>
              )}
              {model.clusters && (
                <div className="px-3 py-1 rounded-lg bg-white/5">
                  <span className="text-xs text-gray-400">Clusters: </span>
                  <span className="text-xs text-white font-semibold">{model.clusters}</span>
                </div>
              )}
              {model.silhouette_score && (
                <div className="px-3 py-1 rounded-lg bg-white/5">
                  <span className="text-xs text-gray-400">Silhouette: </span>
                  <span className="text-xs text-white font-semibold">{model.silhouette_score}</span>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
