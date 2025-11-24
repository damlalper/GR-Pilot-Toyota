import { useEffect, useState } from 'react';
import { useStore } from '../store/useStore';
import { fetchSuggestions } from '../api';
import { Lightbulb, AlertCircle, CheckCircle, ChevronRight } from 'lucide-react';
import { ComponentExplanation } from './ComponentExplanation';

interface Suggestion {
  type: string;
  title: string;
  description: string;
  priority: 'high' | 'medium' | 'low';
  distance_start?: number;
  distance_end?: number;
  speed_delta?: number;
}

interface SuggestionsData {
  lap: number;
  suggestion_count: number;
  suggestions: Suggestion[];
}

export function SuggestionsPanel() {
  const { currentLap } = useStore();
  const [data, setData] = useState<SuggestionsData | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    const loadSuggestions = async () => {
      if (!currentLap) return;
      setIsLoading(true);
      try {
        const result = await fetchSuggestions(currentLap);
        setData(result);
      } catch (error) {
        console.error('Failed to load suggestions:', error);
      } finally {
        setIsLoading(false);
      }
    };
    loadSuggestions();
  }, [currentLap]);

  const getPriorityIcon = (priority: string) => {
    switch (priority) {
      case 'high':
        return <AlertCircle className="w-4 h-4 text-red-400" />;
      case 'medium':
        return <Lightbulb className="w-4 h-4 text-yellow-400" />;
      default:
        return <CheckCircle className="w-4 h-4 text-green-400" />;
    }
  };

  const getPriorityBg = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'bg-red-500/10 border-red-500/20 hover:bg-red-500/20';
      case 'medium':
        return 'bg-yellow-500/10 border-yellow-500/20 hover:bg-yellow-500/20';
      default:
        return 'bg-green-500/10 border-green-500/20 hover:bg-green-500/20';
    }
  };

  if (isLoading) {
    return (
      <div className="glass rounded-xl p-4">
        <div className="flex items-center gap-2 mb-4">
          <Lightbulb className="w-5 h-5 text-yellow-400" />
          <h3 className="font-bold text-white">AI Suggestions</h3>
        </div>
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin w-6 h-6 border-2 border-yellow-400 border-t-transparent rounded-full" />
        </div>
      </div>
    );
  }

  if (!data || data.suggestions.length === 0) {
    return (
      <div className="glass rounded-xl p-4">
        <div className="flex items-center gap-2 mb-4">
          <Lightbulb className="w-5 h-5 text-yellow-400" />
          <h3 className="font-bold text-white">AI Suggestions</h3>
        </div>
        <div className="text-center py-6">
          <CheckCircle className="w-10 h-10 text-green-400 mx-auto mb-2" />
          <p className="text-gray-400 text-sm">Great job! No improvements needed.</p>
        </div>
      </div>
    );
  }

  const highPriority = data.suggestions.filter((s) => s.priority === 'high');
  const mediumPriority = data.suggestions.filter((s) => s.priority === 'medium');
  const lowPriority = data.suggestions.filter((s) => s.priority === 'low');

  return (
    <div className="glass rounded-xl p-4">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-yellow-500/20 flex items-center justify-center">
            <Lightbulb className="w-5 h-5 text-yellow-400" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="font-bold text-white">AI Suggestions</h3>
              <ComponentExplanation componentName="ai_suggestions" />
            </div>
            <p className="text-xs text-gray-400">{data.suggestion_count} improvements found</p>
          </div>
        </div>
      </div>

      {/* Priority Summary */}
      <div className="flex gap-2 mb-4">
        {highPriority.length > 0 && (
          <span className="px-2 py-1 rounded-full bg-red-500/20 text-red-400 text-xs">
            {highPriority.length} Critical
          </span>
        )}
        {mediumPriority.length > 0 && (
          <span className="px-2 py-1 rounded-full bg-yellow-500/20 text-yellow-400 text-xs">
            {mediumPriority.length} Important
          </span>
        )}
        {lowPriority.length > 0 && (
          <span className="px-2 py-1 rounded-full bg-green-500/20 text-green-400 text-xs">
            {lowPriority.length} Minor
          </span>
        )}
      </div>

      {/* Suggestions List */}
      <div className="space-y-2 max-h-80 overflow-y-auto">
        {data.suggestions.map((suggestion, i) => (
          <div
            key={i}
            className={`p-3 rounded-lg border transition-colors cursor-pointer ${getPriorityBg(
              suggestion.priority
            )}`}
          >
            <div className="flex items-start justify-between">
              <div className="flex items-start gap-2">
                {getPriorityIcon(suggestion.priority)}
                <div>
                  <h4 className="text-sm font-medium text-white">{suggestion.title}</h4>
                  <p className="text-xs text-gray-400 mt-1">{suggestion.description}</p>
                  {suggestion.distance_start !== undefined && (
                    <p className="text-xs text-gray-500 mt-1">
                      Zone: {suggestion.distance_start}m - {suggestion.distance_end}m
                    </p>
                  )}
                </div>
              </div>
              <ChevronRight className="w-4 h-4 text-gray-500 flex-shrink-0" />
            </div>
          </div>
        ))}
      </div>

      {/* Action Hint */}
      <div className="mt-4 pt-3 border-t border-white/10">
        <p className="text-xs text-gray-500 text-center">
          Click on a suggestion to focus on that track section
        </p>
      </div>
    </div>
  );
}
