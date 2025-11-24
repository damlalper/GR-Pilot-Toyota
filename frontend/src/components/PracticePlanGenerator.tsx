import { useEffect, useState } from 'react';
import { useStore } from '../store/useStore';
import { api } from '../api';
import { ClipboardList, Clock, Target, TrendingUp } from 'lucide-react';

interface TrainingDrill {
  id: string;
  name: string;
  description: string;
  duration_minutes: number;
  difficulty: string;
  target_skills: string[];
  current_level: number;
  target_level: number;
  priority: string;
}

interface PracticePlan {
  lap: number;
  overall_level: string;
  plan_generated: string;
  drills: TrainingDrill[];
  estimated_weeks_to_improvement: number;
  focus_areas: string[];
  strengths_to_maintain: string[];
  recommended_session_frequency: string;
  total_weekly_hours: number;
}

export function PracticePlanGenerator() {
  const currentLap = useStore((state) => state.currentLap);
  const [practicePlan, setPracticePlan] = useState<PracticePlan | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchPracticePlan = async () => {
      if (!currentLap) return;
      setLoading(true);
      try {
        const response = await api.post(`/api/training/practice_plan?lap=${currentLap}`);
        setPracticePlan(response.data);
      } catch (error) {
        console.error('Error fetching practice plan:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchPracticePlan();
  }, [currentLap]);

  if (loading) {
    return (
      <div className="glass rounded-xl p-6">
        <div className="flex items-center justify-center h-48">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-toyota-red"></div>
        </div>
      </div>
    );
  }

  if (!practicePlan) {
    return (
      <div className="glass rounded-xl p-6">
        <div className="flex items-center gap-3 mb-4">
          <ClipboardList className="w-6 h-6 text-toyota-red" />
          <h3 className="text-lg font-semibold text-white">Practice Plan</h3>
        </div>
        <p className="text-gray-400 text-sm">Select a lap to generate personalized practice plan</p>
      </div>
    );
  }

  const getDifficultyColor = (difficulty: string) => {
    if (difficulty === 'Easy') return '#22c55e';
    if (difficulty === 'Medium') return '#fbbf24';
    return '#ef4444';
  };

  const getPriorityColor = (priority: string) => {
    if (priority === 'High') return '#ef4444';
    if (priority === 'Medium') return '#fbbf24';
    return '#3b82f6';
  };

  return (
    <div className="glass rounded-xl p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <ClipboardList className="w-6 h-6 text-toyota-red" />
          <h3 className="text-lg font-semibold text-white">Personalized Practice Plan</h3>
        </div>
        <div className="px-3 py-1 rounded-full bg-white/5">
          <span className="text-xs text-gray-400">{practicePlan.overall_level} Level</span>
        </div>
      </div>

      {/* Plan Summary */}
      <div className="grid grid-cols-3 gap-3 mb-4">
        <div className="bg-white/5 rounded-lg p-3">
          <div className="flex items-center gap-2 mb-1">
            <Clock className="w-4 h-4 text-blue-400" />
            <p className="text-xs text-gray-400">Weekly Hours</p>
          </div>
          <p className="text-lg font-bold text-white">{practicePlan.total_weekly_hours.toFixed(1)} hrs</p>
        </div>
        <div className="bg-white/5 rounded-lg p-3">
          <div className="flex items-center gap-2 mb-1">
            <Target className="w-4 h-4 text-green-400" />
            <p className="text-xs text-gray-400">Focus Areas</p>
          </div>
          <p className="text-lg font-bold text-white">{practicePlan.focus_areas.length}</p>
        </div>
        <div className="bg-white/5 rounded-lg p-3">
          <div className="flex items-center gap-2 mb-1">
            <TrendingUp className="w-4 h-4 text-yellow-400" />
            <p className="text-xs text-gray-400">Time to Improve</p>
          </div>
          <p className="text-lg font-bold text-white">{practicePlan.estimated_weeks_to_improvement} weeks</p>
        </div>
      </div>

      {/* Training Drills */}
      <div className="space-y-3">
        <h4 className="text-sm font-semibold text-gray-400 uppercase">Recommended Drills</h4>
        {practicePlan.drills.map((drill) => (
          <div
            key={drill.id}
            className="bg-white/5 rounded-lg p-4 border-l-4"
            style={{ borderLeftColor: getPriorityColor(drill.priority) }}
          >
            <div className="flex items-start justify-between mb-2">
              <div>
                <h5 className="text-white font-semibold text-sm">{drill.name}</h5>
                <p className="text-gray-400 text-xs mt-1">{drill.description}</p>
              </div>
              <div className="flex gap-2">
                <span
                  className="px-2 py-1 rounded text-xs font-semibold"
                  style={{
                    backgroundColor: getDifficultyColor(drill.difficulty) + '20',
                    color: getDifficultyColor(drill.difficulty)
                  }}
                >
                  {drill.difficulty}
                </span>
                <span
                  className="px-2 py-1 rounded text-xs font-semibold"
                  style={{
                    backgroundColor: getPriorityColor(drill.priority) + '20',
                    color: getPriorityColor(drill.priority)
                  }}
                >
                  {drill.priority}
                </span>
              </div>
            </div>

            <div className="flex items-center gap-4 mt-3 text-xs">
              <div className="flex items-center gap-2">
                <Clock className="w-3 h-3 text-gray-400" />
                <span className="text-gray-400">{drill.duration_minutes} min</span>
              </div>
              <div className="flex-1">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-gray-400">Progress Goal</span>
                  <span className="text-white font-semibold">
                    {drill.current_level.toFixed(0)} → {drill.target_level.toFixed(0)}
                  </span>
                </div>
                <div className="w-full bg-white/10 rounded-full h-2">
                  <div
                    className="h-full rounded-full bg-toyota-red"
                    style={{ width: `${(drill.current_level / drill.target_level) * 100}%` }}
                  />
                </div>
              </div>
            </div>

            <div className="mt-2">
              <div className="flex flex-wrap gap-1">
                {drill.target_skills.map((skill, idx) => (
                  <span key={idx} className="text-xs bg-blue-500/20 text-blue-400 px-2 py-0.5 rounded">
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Session Frequency */}
      <div className="mt-4 bg-blue-500/10 border border-blue-500/30 rounded-lg p-3">
        <p className="text-xs text-blue-400 font-semibold mb-1">Recommended Schedule</p>
        <p className="text-xs text-gray-300">{practicePlan.recommended_session_frequency}</p>
      </div>

      {/* Focus Areas */}
      <div className="mt-4 grid grid-cols-2 gap-3">
        <div>
          <p className="text-xs text-gray-400 mb-2">Focus On:</p>
          <div className="space-y-1">
            {practicePlan.focus_areas.map((area, idx) => (
              <div key={idx} className="text-xs bg-red-500/10 text-red-400 px-2 py-1 rounded">
                {area}
              </div>
            ))}
          </div>
        </div>
        <div>
          <p className="text-xs text-gray-400 mb-2">Maintain:</p>
          <div className="space-y-1">
            {practicePlan.strengths_to_maintain.map((strength, idx) => (
              <div key={idx} className="text-xs bg-green-500/10 text-green-400 px-2 py-1 rounded">
                {strength}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
