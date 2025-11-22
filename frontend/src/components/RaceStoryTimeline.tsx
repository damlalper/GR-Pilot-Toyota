import { useEffect, useState } from 'react';
import { useStore } from '../store/useStore';
import { api } from '../api';
import { Clock, AlertTriangle, CheckCircle, Info, TrendingDown, Zap } from 'lucide-react';

interface TimelineEvent {
  time: number;
  distance: number;
  lap_progress: number;
  event_type: string;
  severity: 'info' | 'warning' | 'success';
  title: string;
  description: string;
  metrics: Record<string, number>;
  x: number;
  y: number;
}

interface RaceStoryData {
  lap: number;
  event_count: number;
  lap_rating: string;
  rating_color: string;
  event_summary: {
    oversteer: number;
    speed_loss: number;
    perfect: number;
    braking: number;
  };
  timeline: TimelineEvent[];
  lap_stats: {
    duration: number;
    max_speed: number;
    avg_speed: number;
    distance: number;
  };
}

export function RaceStoryTimeline() {
  const currentLap = useStore((state) => state.currentLap);
  const [storyData, setStoryData] = useState<RaceStoryData | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchStory = async () => {
      if (!currentLap) return;
      setLoading(true);
      try {
        const response = await api.get(`/race_story/${currentLap}`);
        setStoryData(response.data);
      } catch (error) {
        console.error('Error fetching race story:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchStory();
  }, [currentLap]);

  if (loading) {
    return (
      <div className="glass rounded-xl p-6">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-toyota-red"></div>
        </div>
      </div>
    );
  }

  if (!storyData) {
    return (
      <div className="glass rounded-xl p-6">
        <div className="flex items-center gap-3 mb-4">
          <Clock className="w-6 h-6 text-toyota-red" />
          <h3 className="text-lg font-semibold text-white">Race Story Timeline</h3>
        </div>
        <p className="text-gray-400 text-sm">Select a lap to view race story</p>
      </div>
    );
  }

  const getEventIcon = (eventType: string, severity: string) => {
    if (severity === 'warning') return <AlertTriangle className="w-4 h-4 text-yellow-400" />;
    if (severity === 'success') return <CheckCircle className="w-4 h-4 text-green-400" />;
    if (eventType === 'speed_loss') return <TrendingDown className="w-4 h-4 text-red-400" />;
    if (eventType === 'gear_change') return <Zap className="w-4 h-4 text-blue-400" />;
    return <Info className="w-4 h-4 text-gray-400" />;
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'warning':
        return { bg: 'bg-yellow-500/10', border: 'border-yellow-500/30', text: 'text-yellow-400' };
      case 'success':
        return { bg: 'bg-green-500/10', border: 'border-green-500/30', text: 'text-green-400' };
      default:
        return { bg: 'bg-blue-500/10', border: 'border-blue-500/30', text: 'text-blue-400' };
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = (seconds % 60).toFixed(2);
    return mins > 0 ? `${mins}:${secs.padStart(5, '0')}` : `${secs}s`;
  };

  return (
    <div className="glass rounded-xl p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Clock className="w-6 h-6 text-toyota-red" />
          <h3 className="text-lg font-semibold text-white">Race Story Timeline</h3>
        </div>
        <div className="flex items-center gap-3">
          <div
            className="px-3 py-1 rounded-full text-xs font-semibold"
            style={{ backgroundColor: storyData.rating_color + '20', color: storyData.rating_color }}
          >
            {storyData.lap_rating}
          </div>
          <span className="text-xs text-gray-400">Lap {storyData.lap}</span>
        </div>
      </div>

      {/* Lap Stats */}
      <div className="grid grid-cols-4 gap-3">
        <div className="bg-white/5 rounded-lg p-3">
          <p className="text-xs text-gray-400 mb-1">Duration</p>
          <p className="text-lg font-bold text-white">{formatTime(storyData.lap_stats.duration)}</p>
        </div>
        <div className="bg-white/5 rounded-lg p-3">
          <p className="text-xs text-gray-400 mb-1">Max Speed</p>
          <p className="text-lg font-bold text-white">{storyData.lap_stats.max_speed.toFixed(0)}</p>
          <p className="text-xs text-gray-400">km/h</p>
        </div>
        <div className="bg-white/5 rounded-lg p-3">
          <p className="text-xs text-gray-400 mb-1">Avg Speed</p>
          <p className="text-lg font-bold text-white">{storyData.lap_stats.avg_speed.toFixed(0)}</p>
          <p className="text-xs text-gray-400">km/h</p>
        </div>
        <div className="bg-white/5 rounded-lg p-3">
          <p className="text-xs text-gray-400 mb-1">Events</p>
          <p className="text-lg font-bold text-white">{storyData.event_count}</p>
        </div>
      </div>

      {/* Event Summary */}
      <div className="grid grid-cols-4 gap-2">
        <div className="flex items-center gap-2 bg-yellow-500/10 rounded px-3 py-2">
          <AlertTriangle className="w-4 h-4 text-yellow-400" />
          <div>
            <p className="text-xs text-gray-400">Oversteer</p>
            <p className="text-sm font-bold text-yellow-400">{storyData.event_summary.oversteer}</p>
          </div>
        </div>
        <div className="flex items-center gap-2 bg-red-500/10 rounded px-3 py-2">
          <TrendingDown className="w-4 h-4 text-red-400" />
          <div>
            <p className="text-xs text-gray-400">Speed Loss</p>
            <p className="text-sm font-bold text-red-400">{storyData.event_summary.speed_loss}</p>
          </div>
        </div>
        <div className="flex items-center gap-2 bg-green-500/10 rounded px-3 py-2">
          <CheckCircle className="w-4 h-4 text-green-400" />
          <div>
            <p className="text-xs text-gray-400">Perfect</p>
            <p className="text-sm font-bold text-green-400">{storyData.event_summary.perfect}</p>
          </div>
        </div>
        <div className="flex items-center gap-2 bg-blue-500/10 rounded px-3 py-2">
          <Info className="w-4 h-4 text-blue-400" />
          <div>
            <p className="text-xs text-gray-400">Braking</p>
            <p className="text-sm font-bold text-blue-400">{storyData.event_summary.braking}</p>
          </div>
        </div>
      </div>

      {/* Timeline */}
      <div className="space-y-3 max-h-[600px] overflow-y-auto custom-scrollbar">
        <h4 className="text-sm font-semibold text-gray-400 uppercase tracking-wider sticky top-0 bg-[#0a0a0a] py-2">
          Event Timeline
        </h4>
        <div className="relative pl-8">
          {/* Timeline line */}
          <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-white/10"></div>

          {storyData.timeline.map((event, idx) => {
            const colors = getSeverityColor(event.severity);
            return (
              <div key={idx} className="relative mb-4 last:mb-0">
                {/* Timeline dot */}
                <div
                  className={`absolute -left-[1.85rem] top-2 w-3 h-3 rounded-full ${colors.bg} ${colors.border} border-2`}
                ></div>

                {/* Event card */}
                <div
                  className={`${colors.bg} ${colors.border} border rounded-lg p-3 ml-4 hover:bg-white/10 transition-colors`}
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center gap-2">
                      {getEventIcon(event.event_type, event.severity)}
                      <h5 className={`font-semibold text-sm ${colors.text}`}>{event.title}</h5>
                    </div>
                    <div className="flex items-center gap-2 text-xs text-gray-400">
                      <Clock className="w-3 h-3" />
                      <span>{formatTime(event.time)}</span>
                    </div>
                  </div>

                  <p className="text-xs text-gray-300 mb-2">{event.description}</p>

                  <div className="flex items-center justify-between text-xs">
                    <div className="flex gap-3 text-gray-400">
                      <span>Distance: {event.distance.toFixed(0)}m</span>
                      <span>Progress: {event.lap_progress.toFixed(0)}%</span>
                    </div>
                    {Object.keys(event.metrics).length > 0 && (
                      <div className="flex gap-2">
                        {Object.entries(event.metrics).slice(0, 2).map(([key, value]) => (
                          <span key={key} className="text-gray-400">
                            {key}: {typeof value === 'number' ? value.toFixed(1) : value}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {storyData.timeline.length === 0 && (
        <div className="text-center py-8">
          <p className="text-gray-400">No significant events detected in this lap</p>
          <p className="text-xs text-gray-500 mt-2">This indicates a very clean lap!</p>
        </div>
      )}
    </div>
  );
}
