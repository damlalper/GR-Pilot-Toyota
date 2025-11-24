import { useEffect, useState } from 'react';
import { useStore } from '../store/useStore';
import { api } from '../api';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts';
import { TrendingUp, AlertCircle } from 'lucide-react';

interface LearningCurveData {
  lap_range: {
    start: number;
    end: number;
    total_laps: number;
  };
  learning_metrics: {
    best_lap_time: number;
    average_lap_time: number;
    total_improvement_seconds: number;
    improvement_rate_per_lap: number;
    consistency_std: number;
  };
  learning_stage: string;
  lap_data: Array<{
    lap: number;
    lap_time: number;
    moving_average: number;
    delta_from_best: number;
  }>;
  plateaus_detected: Array<{
    lap_start: number;
    lap_end: number;
    average_time: number;
  }>;
  breakthrough_prediction: {
    estimated_laps_to_next_pb: number;
    predicted_best_time: number;
  };
}

export function LearningCurve() {
  const currentLap = useStore((state) => state.currentLap);
  const [learningData, setLearningData] = useState<LearningCurveData | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchLearningCurve = async () => {
      if (!currentLap) return;

      // Fetch learning curve for last 20 laps (or from lap 1 to current)
      const startLap = Math.max(1, currentLap - 19);
      const endLap = currentLap;

      setLoading(true);
      try {
        const response = await api.get(`/api/training/learning_curve/${startLap}/${endLap}`);
        setLearningData(response.data);
      } catch (error) {
        console.error('Error fetching learning curve:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchLearningCurve();
  }, [currentLap]);

  if (loading) {
    return (
      <div className="glass rounded-xl p-6 h-full">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-toyota-red"></div>
        </div>
      </div>
    );
  }

  if (!learningData) {
    return (
      <div className="glass rounded-xl p-6 h-full">
        <div className="flex items-center gap-3 mb-4">
          <TrendingUp className="w-6 h-6 text-toyota-red" />
          <h3 className="text-lg font-semibold text-white">Learning Curve</h3>
        </div>
        <p className="text-gray-400 text-sm">Select a lap to view progression</p>
      </div>
    );
  }

  const getStageColor = (stage: string) => {
    if (stage.includes('Rapid')) return '#22c55e';
    if (stage.includes('Steady')) return '#fbbf24';
    if (stage.includes('Fine')) return '#3b82f6';
    return '#ef4444';
  };

  return (
    <div className="glass rounded-xl p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <TrendingUp className="w-6 h-6 text-toyota-red" />
          <h3 className="text-lg font-semibold text-white">Learning Curve</h3>
        </div>
        <div
          className="px-3 py-1 rounded-full text-xs font-semibold"
          style={{
            backgroundColor: getStageColor(learningData.learning_stage) + '20',
            color: getStageColor(learningData.learning_stage)
          }}
        >
          {learningData.learning_stage}
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-3 gap-2 mb-4">
        <div className="bg-white/5 rounded-lg p-2">
          <p className="text-xs text-gray-400">Best Time</p>
          <p className="text-lg font-bold text-white">{learningData.learning_metrics.best_lap_time.toFixed(3)}s</p>
        </div>
        <div className="bg-white/5 rounded-lg p-2">
          <p className="text-xs text-gray-400">Improvement</p>
          <p className="text-lg font-bold text-green-400">
            {learningData.learning_metrics.total_improvement_seconds > 0 ? '-' : '+'}
            {Math.abs(learningData.learning_metrics.total_improvement_seconds).toFixed(2)}s
          </p>
        </div>
        <div className="bg-white/5 rounded-lg p-2">
          <p className="text-xs text-gray-400">Consistency</p>
          <p className="text-lg font-bold text-blue-400">
            ±{learningData.learning_metrics.consistency_std.toFixed(2)}s
          </p>
        </div>
      </div>

      {/* Line Chart */}
      <div className="h-48">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={learningData.lap_data}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.1)" />
            <XAxis
              dataKey="lap"
              stroke="#9ca3af"
              tick={{ fill: '#9ca3af', fontSize: 11 }}
              label={{ value: 'Lap', position: 'insideBottom', offset: -5, fill: '#6b7280', fontSize: 11 }}
            />
            <YAxis
              stroke="#9ca3af"
              tick={{ fill: '#9ca3af', fontSize: 11 }}
              domain={['dataMin - 1', 'dataMax + 1']}
              label={{ value: 'Time (s)', angle: -90, position: 'insideLeft', fill: '#6b7280', fontSize: 11 }}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: 'rgba(0, 0, 0, 0.8)',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                borderRadius: '8px',
                color: '#fff'
              }}
            />
            <ReferenceLine
              y={learningData.learning_metrics.best_lap_time}
              stroke="#22c55e"
              strokeDasharray="3 3"
              label={{ value: 'Best', fill: '#22c55e', fontSize: 10 }}
            />
            <Line
              type="monotone"
              dataKey="lap_time"
              stroke="#eb0a1e"
              strokeWidth={2}
              dot={{ fill: '#eb0a1e', r: 3 }}
            />
            <Line
              type="monotone"
              dataKey="moving_average"
              stroke="#3b82f6"
              strokeWidth={2}
              strokeDasharray="5 5"
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Plateaus Alert */}
      {learningData.plateaus_detected.length > 0 && (
        <div className="mt-4 bg-yellow-500/10 border border-yellow-500/30 rounded-lg p-3">
          <div className="flex items-start gap-2">
            <AlertCircle className="w-4 h-4 text-yellow-500 mt-0.5" />
            <div>
              <p className="text-xs font-semibold text-yellow-500">Plateau Detected</p>
              <p className="text-xs text-gray-400 mt-1">
                Laps {learningData.plateaus_detected[0].lap_start}-{learningData.plateaus_detected[0].lap_end}:
                Consider trying different techniques to break through
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Breakthrough Prediction */}
      <div className="mt-3 text-xs text-gray-400 text-center">
        Next PB predicted in ~{learningData.breakthrough_prediction.estimated_laps_to_next_pb} laps
        ({learningData.breakthrough_prediction.predicted_best_time.toFixed(3)}s)
      </div>
    </div>
  );
}
