import React, { useEffect, useState } from 'react';
import { api } from '../api';
import { Star, Lock, CloudRain, Users, CircleDot, Gauge, Zap, Play, Shield, Moon } from 'lucide-react';

interface Scenario {
  id: string;
  name: string;
  description: string;
  difficulty: string;
  stars_achieved: number;
  max_stars: number;
  is_locked: boolean;
  requirements: string | null;
  objectives: string[];
  icon: string;
}

interface ScenariosData {
  total_scenarios: number;
  completed_scenarios: number;
  total_stars: number;
  max_stars: number;
  scenarios: Scenario[];
}

export function ScenarioCard() {
  const [scenariosData, setScenariosData] = useState<ScenariosData | null>(null);
  const [loading, setLoading] = useState(false);
  const [selectedScenario, setSelectedScenario] = useState<Scenario | null>(null);

  useEffect(() => {
    const fetchScenarios = async () => {
      setLoading(true);
      try {
        const response = await api.get('/api/training/scenarios');
        setScenariosData(response.data);
      } catch (error) {
        console.error('Error fetching scenarios:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchScenarios();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-48">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-toyota-red"></div>
      </div>
    );
  }

  if (!scenariosData) {
    return <p className="text-gray-400 text-sm">Failed to load scenarios</p>;
  }

  const getIconComponent = (iconName: string) => {
    const icons: Record<string, any> = {
      'cloud-rain': CloudRain,
      'users': Users,
      'circle-dot': CircleDot,
      'gauge': Gauge,
      'zap': Zap,
      'play': Play,
      'shield': Shield,
      'moon': Moon
    };
    return icons[iconName] || Star;
  };

  const getDifficultyColor = (difficulty: string) => {
    if (difficulty === 'Easy') return '#22c55e';
    if (difficulty === 'Medium') return '#fbbf24';
    if (difficulty === 'Hard') return '#f97316';
    return '#ef4444';
  };

  return (
    <div className="space-y-4">
      {/* Progress Summary */}
      <div className="grid grid-cols-4 gap-2">
        <div className="bg-white/5 rounded-lg p-3 text-center">
          <p className="text-2xl font-bold text-white">{scenariosData.total_scenarios}</p>
          <p className="text-xs text-gray-400">Total Scenarios</p>
        </div>
        <div className="bg-white/5 rounded-lg p-3 text-center">
          <p className="text-2xl font-bold text-green-400">{scenariosData.completed_scenarios}</p>
          <p className="text-xs text-gray-400">Completed</p>
        </div>
        <div className="bg-white/5 rounded-lg p-3 text-center">
          <p className="text-2xl font-bold text-yellow-400">
            {scenariosData.total_stars}/{scenariosData.max_stars}
          </p>
          <p className="text-xs text-gray-400">Stars</p>
        </div>
        <div className="bg-white/5 rounded-lg p-3 text-center">
          <p className="text-2xl font-bold text-blue-400">
            {Math.round((scenariosData.completed_scenarios / scenariosData.total_scenarios) * 100)}%
          </p>
          <p className="text-xs text-gray-400">Progress</p>
        </div>
      </div>

      {/* Scenario Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
        {scenariosData.scenarios.map((scenario) => {
          const IconComponent = getIconComponent(scenario.icon);

          return (
            <div
              key={scenario.id}
              className={`bg-white/5 rounded-lg p-4 border transition-all cursor-pointer ${
                scenario.is_locked
                  ? 'border-white/10 opacity-60'
                  : 'border-white/20 hover:border-toyota-red/50 hover:bg-white/10'
              }`}
              onClick={() => !scenario.is_locked && setSelectedScenario(scenario)}
            >
              {/* Header */}
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-2">
                  <div
                    className="w-10 h-10 rounded-lg flex items-center justify-center"
                    style={{ backgroundColor: getDifficultyColor(scenario.difficulty) + '20' }}
                  >
                    {scenario.is_locked ? (
                      <Lock className="w-5 h-5 text-gray-400" />
                    ) : (
                      <IconComponent
                        className="w-5 h-5"
                        style={{ color: getDifficultyColor(scenario.difficulty) }}
                      />
                    )}
                  </div>
                  <div>
                    <h4 className="text-white font-semibold text-sm">{scenario.name}</h4>
                    <span
                      className="text-xs px-2 py-0.5 rounded"
                      style={{
                        backgroundColor: getDifficultyColor(scenario.difficulty) + '20',
                        color: getDifficultyColor(scenario.difficulty)
                      }}
                    >
                      {scenario.difficulty}
                    </span>
                  </div>
                </div>
              </div>

              {/* Description */}
              <p className="text-gray-400 text-xs mb-3">{scenario.description}</p>

              {/* Stars */}
              <div className="flex items-center gap-1 mb-3">
                {[...Array(scenario.max_stars)].map((_, idx) => (
                  <Star
                    key={idx}
                    className={`w-4 h-4 ${
                      idx < scenario.stars_achieved
                        ? 'fill-yellow-400 text-yellow-400'
                        : 'text-gray-600'
                    }`}
                  />
                ))}
              </div>

              {/* Lock Status */}
              {scenario.is_locked && scenario.requirements && (
                <div className="text-xs text-gray-500 bg-white/5 rounded px-2 py-1">
                  <Lock className="w-3 h-3 inline mr-1" />
                  {scenario.requirements}
                </div>
              )}

              {/* Objectives Preview */}
              {!scenario.is_locked && (
                <div className="mt-3 space-y-1">
                  {scenario.objectives.slice(0, 2).map((obj, idx) => (
                    <div key={idx} className="flex items-start gap-2">
                      <div className="w-1.5 h-1.5 rounded-full bg-toyota-red mt-1.5" />
                      <p className="text-xs text-gray-400">{obj}</p>
                    </div>
                  ))}
                  {scenario.objectives.length > 2 && (
                    <p className="text-xs text-gray-500 ml-3.5">+{scenario.objectives.length - 2} more...</p>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Scenario Details Modal */}
      {selectedScenario && (
        <div
          className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
          onClick={() => setSelectedScenario(null)}
        >
          <div
            className="glass rounded-xl p-6 max-w-md w-full"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center gap-3 mb-4">
              {React.createElement(getIconComponent(selectedScenario.icon), {
                className: 'w-8 h-8 text-toyota-red'
              })}
              <h3 className="text-xl font-bold text-white">{selectedScenario.name}</h3>
            </div>

            <p className="text-gray-400 text-sm mb-4">{selectedScenario.description}</p>

            <div className="space-y-3 mb-4">
              <h4 className="text-sm font-semibold text-gray-400 uppercase">Objectives</h4>
              {selectedScenario.objectives.map((obj, idx) => (
                <div key={idx} className="flex items-start gap-2">
                  <div className="w-2 h-2 rounded-full bg-toyota-red mt-1.5" />
                  <p className="text-sm text-gray-300">{obj}</p>
                </div>
              ))}
            </div>

            <div className="flex items-center justify-between pt-4 border-t border-white/10">
              <div className="flex items-center gap-1">
                {[...Array(selectedScenario.max_stars)].map((_, idx) => (
                  <Star
                    key={idx}
                    className={`w-5 h-5 ${
                      idx < selectedScenario.stars_achieved
                        ? 'fill-yellow-400 text-yellow-400'
                        : 'text-gray-600'
                    }`}
                  />
                ))}
              </div>
              <button
                className="px-4 py-2 bg-toyota-red text-white rounded-lg font-semibold hover:bg-red-700 transition"
                onClick={() => setSelectedScenario(null)}
              >
                Start Training
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
