import { useEffect } from 'react';
import { useStore } from '../store/useStore';
import { SkillRadarChart } from './SkillRadarChart';
import { PracticePlanGenerator } from './PracticePlanGenerator';
import { ScenarioCard } from './ScenarioCard';
import { LiveCoachingFeed } from './LiveCoachingFeed';
import { LearningCurve } from './LearningCurve';
import { BenchmarkComparison } from './BenchmarkComparison';
import { Target, TrendingUp, Award } from 'lucide-react';

export function Training() {
  const currentLap = useStore((state) => state.currentLap);

  useEffect(() => {
    console.log('Training component mounted. Current lap:', currentLap);
  }, [currentLap]);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
      {/* Left Column - Main Training Features */}
      <div className="lg:col-span-8 space-y-4">
        {/* Header */}
        <div className="glass rounded-xl p-6">
          <div className="flex items-center gap-3 mb-2">
            <Target className="w-8 h-8 text-toyota-red" />
            <h2 className="text-2xl font-bold text-white">Driver Coach Studio</h2>
          </div>
          <p className="text-gray-400 text-sm">
            Advanced training system to identify weaknesses, track progress, and accelerate your improvement
          </p>
        </div>

        {/* Skill Assessment & Learning Curve */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <SkillRadarChart />
          <LearningCurve />
        </div>

        {/* Practice Plan Generator */}
        <PracticePlanGenerator />

        {/* Training Scenarios */}
        <div className="glass rounded-xl p-6">
          <div className="flex items-center gap-3 mb-4">
            <Award className="w-6 h-6 text-toyota-red" />
            <h3 className="text-lg font-semibold text-white">Training Scenarios</h3>
          </div>
          <p className="text-gray-400 text-sm mb-4">
            Complete scenario-based challenges to earn stars and unlock advanced training modes
          </p>
          <ScenarioCard />
        </div>

        {/* Benchmark Comparison */}
        <BenchmarkComparison />
      </div>

      {/* Right Column - Live Coaching & Stats */}
      <div className="lg:col-span-4 space-y-4">
        {/* Quick Stats Card */}
        <div className="glass rounded-xl p-6">
          <div className="flex items-center gap-3 mb-4">
            <TrendingUp className="w-6 h-6 text-green-500" />
            <h3 className="text-lg font-semibold text-white">Your Progress</h3>
          </div>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-gray-400 text-sm">Overall Rating</span>
              <span className="text-white font-semibold">Intermediate</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-400 text-sm">Training Hours</span>
              <span className="text-white font-semibold">24.5 hrs</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-400 text-sm">Scenarios Completed</span>
              <span className="text-white font-semibold">3/8</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-400 text-sm">Stars Earned</span>
              <span className="text-white font-semibold">6/24</span>
            </div>
          </div>
        </div>

        {/* Live Coaching Feed */}
        <LiveCoachingFeed />

        {/* Achievement Badges */}
        <div className="glass rounded-xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Recent Achievements</h3>
          <div className="space-y-2">
            <div className="flex items-center gap-3 bg-white/5 rounded-lg p-3">
              <div className="w-10 h-10 rounded-full bg-yellow-500/20 flex items-center justify-center">
                <Award className="w-5 h-5 text-yellow-500" />
              </div>
              <div>
                <p className="text-white text-sm font-semibold">Qualifying Hero</p>
                <p className="text-gray-400 text-xs">Perfect lap achievement</p>
              </div>
            </div>
            <div className="flex items-center gap-3 bg-white/5 rounded-lg p-3">
              <div className="w-10 h-10 rounded-full bg-blue-500/20 flex items-center justify-center">
                <TrendingUp className="w-5 h-5 text-blue-500" />
              </div>
              <div>
                <p className="text-white text-sm font-semibold">Consistency King</p>
                <p className="text-gray-400 text-xs">10 laps within 0.5s</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
