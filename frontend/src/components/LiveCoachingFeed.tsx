import { useEffect, useState } from 'react';
import { useStore } from '../store/useStore';
import { api } from '../api';
import { MessageCircle, AlertTriangle, CheckCircle, Info, TrendingUp } from 'lucide-react';

interface CoachingCue {
  id: string;
  location: string;
  corner: string | null;
  message: string;
  priority: string;
  expected_gain_seconds: number;
  visual_marker: any;
  category: string;
}

interface CoachingData {
  lap: number;
  total_coaching_points: number;
  total_potential_gain_seconds: number;
  coaching_cues: CoachingCue[];
  summary: {
    high_priority: number;
    medium_priority: number;
    low_priority: number;
  };
}

export function LiveCoachingFeed() {
  const currentLap = useStore((state) => state.currentLap);
  const [coachingData, setCoachingData] = useState<CoachingData | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchCoachingInsights = async () => {
      if (!currentLap) return;
      setLoading(true);
      try {
        const response = await api.get(`/api/training/live_coaching/${currentLap}`);
        setCoachingData(response.data);
      } catch (error) {
        console.error('Error fetching coaching insights:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchCoachingInsights();
  }, [currentLap]);

  if (loading) {
    return (
      <div className="glass rounded-xl p-6">
        <div className="flex items-center justify-center h-48">
          <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-toyota-red"></div>
        </div>
      </div>
    );
  }

  if (!coachingData) {
    return (
      <div className="glass rounded-xl p-6">
        <div className="flex items-center gap-3 mb-4">
          <MessageCircle className="w-6 h-6 text-toyota-red" />
          <h3 className="text-lg font-semibold text-white">Live Coaching</h3>
        </div>
        <p className="text-gray-400 text-sm">Select a lap to view coaching insights</p>
      </div>
    );
  }

  const getPriorityIcon = (priority: string) => {
    if (priority === 'high') return <AlertTriangle className="w-4 h-4" />;
    if (priority === 'medium') return <Info className="w-4 h-4" />;
    return <CheckCircle className="w-4 h-4" />;
  };

  const getPriorityColor = (priority: string) => {
    if (priority === 'high') return { bg: '#ef4444', text: '#fee2e2' };
    if (priority === 'medium') return { bg: '#fbbf24', text: '#fef3c7' };
    return { bg: '#3b82f6', text: '#dbeafe' };
  };

  const getCategoryIcon = (category: string) => {
    return <TrendingUp className="w-3 h-3" />;
  };

  return (
    <div className="glass rounded-xl p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <MessageCircle className="w-6 h-6 text-toyota-red" />
          <h3 className="text-lg font-semibold text-white">Live Coaching</h3>
        </div>
        <div className="px-3 py-1 rounded-full bg-white/5">
          <span className="text-xs text-gray-400">Lap {coachingData.lap}</span>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="bg-green-500/10 border border-green-500/30 rounded-lg p-3 mb-4">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs text-green-400 font-semibold">Potential Gain</p>
            <p className="text-2xl font-bold text-green-300">
              {coachingData.total_potential_gain_seconds.toFixed(2)}s
            </p>
          </div>
          <div className="text-right">
            <p className="text-xs text-gray-400">{coachingData.total_coaching_points} insights</p>
            <div className="flex gap-2 mt-1">
              <span className="text-xs bg-red-500/20 text-red-400 px-2 py-0.5 rounded">
                {coachingData.summary.high_priority} high
              </span>
              <span className="text-xs bg-yellow-500/20 text-yellow-400 px-2 py-0.5 rounded">
                {coachingData.summary.medium_priority} med
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Coaching Cues Feed */}
      <div className="space-y-2 max-h-96 overflow-y-auto">
        {coachingData.coaching_cues.map((cue) => {
          const colors = getPriorityColor(cue.priority);

          return (
            <div
              key={cue.id}
              className="bg-white/5 rounded-lg p-3 border-l-4 hover:bg-white/10 transition"
              style={{ borderLeftColor: colors.bg }}
            >
              {/* Cue Header */}
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-start gap-2">
                  <div
                    className="mt-0.5 p-1 rounded"
                    style={{ backgroundColor: colors.bg + '20', color: colors.bg }}
                  >
                    {getPriorityIcon(cue.priority)}
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <p className="text-white font-semibold text-sm">{cue.location}</p>
                      {cue.corner && (
                        <span className="text-xs bg-white/10 text-gray-400 px-2 py-0.5 rounded">
                          {cue.corner}
                        </span>
                      )}
                    </div>
                    <p className="text-gray-300 text-xs mt-1">{cue.message}</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-green-400 font-bold text-sm">+{cue.expected_gain_seconds.toFixed(2)}s</p>
                </div>
              </div>

              {/* Category Tag */}
              <div className="flex items-center gap-1 mt-2">
                {getCategoryIcon(cue.category)}
                <span className="text-xs text-gray-500 capitalize">{cue.category.replace('_', ' ')}</span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Apply All Button */}
      <button className="w-full mt-4 px-4 py-2 bg-toyota-red text-white rounded-lg font-semibold hover:bg-red-700 transition flex items-center justify-center gap-2">
        <CheckCircle className="w-4 h-4" />
        Apply All Suggestions
      </button>
    </div>
  );
}
