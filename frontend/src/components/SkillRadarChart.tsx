import { useEffect, useState } from 'react';
import { useStore } from '../store/useStore';
import { api } from '../api';
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import { Target, TrendingUp, TrendingDown } from 'lucide-react';

interface SkillData {
  category: string;
  score: number;
  max_score: number;
  rating: string;
  description: string;
}

interface SkillAssessment {
  lap: number;
  overall_score: number;
  overall_rating: string;
  skills: SkillData[];
  strengths: SkillData[];
  weaknesses: SkillData[];
}

export function SkillRadarChart() {
  const currentLap = useStore((state) => state.currentLap);
  const [skillData, setSkillData] = useState<SkillAssessment | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchSkillAssessment = async () => {
      if (!currentLap) return;
      setLoading(true);
      try {
        const response = await api.get(`/api/training/skill_assessment/${currentLap}`);
        setSkillData(response.data);
      } catch (error) {
        console.error('Error fetching skill assessment:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchSkillAssessment();
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

  if (!skillData) {
    return (
      <div className="glass rounded-xl p-6 h-full">
        <div className="flex items-center gap-3 mb-4">
          <Target className="w-6 h-6 text-toyota-red" />
          <h3 className="text-lg font-semibold text-white">Skill Assessment</h3>
        </div>
        <p className="text-gray-400 text-sm">Select a lap to view skill analysis</p>
      </div>
    );
  }

  // Prepare data for radar chart
  const radarData = skillData.skills.map(skill => ({
    skill: skill.category.replace('_', ' '),
    score: skill.score,
    fullMark: skill.max_score
  }));

  // Get color based on overall score
  const getScoreColor = (score: number) => {
    if (score >= 85) return '#22c55e';
    if (score >= 70) return '#fbbf24';
    if (score >= 50) return '#f97316';
    return '#ef4444';
  };

  return (
    <div className="glass rounded-xl p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <Target className="w-6 h-6 text-toyota-red" />
          <h3 className="text-lg font-semibold text-white">Skill Assessment</h3>
        </div>
        <div className="px-3 py-1 rounded-full bg-white/5">
          <span className="text-xs text-gray-400">Lap {skillData.lap}</span>
        </div>
      </div>

      {/* Overall Score */}
      <div className="text-center mb-4">
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/5">
          <span className="text-3xl font-bold" style={{ color: getScoreColor(skillData.overall_score) }}>
            {skillData.overall_score}
          </span>
          <span className="text-gray-400">/100</span>
        </div>
        <p className="text-sm text-gray-400 mt-2">{skillData.overall_rating} Level</p>
      </div>

      {/* Radar Chart */}
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <RadarChart data={radarData}>
            <PolarGrid stroke="rgba(255, 255, 255, 0.1)" />
            <PolarAngleAxis
              dataKey="skill"
              tick={{ fill: '#9ca3af', fontSize: 11 }}
            />
            <PolarRadiusAxis
              angle={90}
              domain={[0, 100]}
              tick={{ fill: '#6b7280', fontSize: 10 }}
            />
            <Radar
              name="Your Score"
              dataKey="score"
              stroke="#eb0a1e"
              fill="#eb0a1e"
              fillOpacity={0.6}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: 'rgba(0, 0, 0, 0.8)',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                borderRadius: '8px',
                color: '#fff'
              }}
            />
          </RadarChart>
        </ResponsiveContainer>
      </div>

      {/* Strengths & Weaknesses */}
      <div className="grid grid-cols-2 gap-3 mt-4">
        {/* Strengths */}
        <div>
          <div className="flex items-center gap-2 mb-2">
            <TrendingUp className="w-4 h-4 text-green-500" />
            <h4 className="text-xs font-semibold text-gray-400 uppercase">Top Skills</h4>
          </div>
          <div className="space-y-1">
            {skillData.strengths.slice(0, 3).map((skill, idx) => (
              <div key={idx} className="text-xs bg-green-500/10 rounded px-2 py-1">
                <span className="text-green-400">{skill.category}</span>
                <span className="text-green-300 float-right font-semibold">{skill.score.toFixed(0)}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Weaknesses */}
        <div>
          <div className="flex items-center gap-2 mb-2">
            <TrendingDown className="w-4 h-4 text-red-500" />
            <h4 className="text-xs font-semibold text-gray-400 uppercase">Focus Areas</h4>
          </div>
          <div className="space-y-1">
            {skillData.weaknesses.slice(0, 3).map((skill, idx) => (
              <div key={idx} className="text-xs bg-red-500/10 rounded px-2 py-1">
                <span className="text-red-400">{skill.category}</span>
                <span className="text-red-300 float-right font-semibold">{skill.score.toFixed(0)}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
