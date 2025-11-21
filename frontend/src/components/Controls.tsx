import { useEffect } from 'react';
import { useStore } from '../store/useStore';
import { fetchLaps, fetchLapData } from '../api';
import { Play, Pause, RotateCcw, ChevronDown, Loader2 } from 'lucide-react';

export function Controls() {
  const {
    laps,
    currentLap,
    lapData,
    isLoading,
    isPlaying,
    playbackSpeed,
    currentIndex,
    setLaps,
    setCurrentLap,
    setLapData,
    setIsLoading,
    setIsPlaying,
    setPlaybackSpeed,
    setCurrentIndex,
  } = useStore();

  // Load laps on mount
  useEffect(() => {
    const loadLaps = async () => {
      try {
        const lapList = await fetchLaps();
        setLaps(lapList);
        if (lapList.length > 0) {
          setCurrentLap(lapList[0]);
        }
      } catch (error) {
        console.error('Failed to load laps:', error);
      }
    };
    loadLaps();
  }, [setLaps, setCurrentLap]);

  // Load lap data when lap changes
  useEffect(() => {
    const loadLapData = async () => {
      if (currentLap === null) return;
      setIsLoading(true);
      try {
        const data = await fetchLapData(currentLap);
        setLapData(data);
        setCurrentIndex(0);
      } catch (error) {
        console.error('Failed to load lap data:', error);
      } finally {
        setIsLoading(false);
      }
    };
    loadLapData();
  }, [currentLap, setLapData, setIsLoading, setCurrentIndex]);

  const handleReset = () => {
    setCurrentIndex(0);
    setIsPlaying(false);
  };

  const speedOptions = [1, 2, 5, 10, 20];

  return (
    <div className="glass rounded-xl p-4">
      <div className="flex flex-wrap items-center gap-4">
        {/* Lap Selector */}
        <div className="relative">
          <label className="text-xs text-gray-400 block mb-1">Select Lap</label>
          <div className="relative">
            <select
              value={currentLap || ''}
              onChange={(e) => setCurrentLap(Number(e.target.value))}
              className="appearance-none bg-white/5 border border-white/10 rounded-lg px-4 py-2 pr-8 text-white focus:outline-none focus:border-toyota-red cursor-pointer"
            >
              {laps.map((lap) => (
                <option key={lap} value={lap} className="bg-gray-900">
                  Lap {lap}
                </option>
              ))}
            </select>
            <ChevronDown className="absolute right-2 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
          </div>
        </div>

        {/* Playback Controls */}
        <div className="flex items-center gap-2">
          <label className="text-xs text-gray-400 block mb-1 sr-only">Controls</label>
          <button
            onClick={() => setIsPlaying(!isPlaying)}
            disabled={isLoading || !lapData}
            className="w-10 h-10 rounded-lg bg-toyota-red hover:bg-toyota-darkRed disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center transition-colors"
          >
            {isPlaying ? (
              <Pause className="w-5 h-5 text-white" />
            ) : (
              <Play className="w-5 h-5 text-white ml-0.5" />
            )}
          </button>
          <button
            onClick={handleReset}
            disabled={isLoading || !lapData}
            className="w-10 h-10 rounded-lg bg-white/10 hover:bg-white/20 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center transition-colors"
          >
            <RotateCcw className="w-5 h-5 text-white" />
          </button>
        </div>

        {/* Speed Selector */}
        <div>
          <label className="text-xs text-gray-400 block mb-1">Speed</label>
          <div className="flex gap-1">
            {speedOptions.map((speed) => (
              <button
                key={speed}
                onClick={() => setPlaybackSpeed(speed)}
                className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                  playbackSpeed === speed
                    ? 'bg-toyota-red text-white'
                    : 'bg-white/5 text-gray-400 hover:bg-white/10'
                }`}
              >
                {speed}x
              </button>
            ))}
          </div>
        </div>

        {/* Progress Slider */}
        <div className="flex-1 min-w-[200px]">
          <label className="text-xs text-gray-400 block mb-1">
            Progress: {lapData ? `${currentIndex + 1} / ${lapData.data.length}` : '-'}
          </label>
          <input
            type="range"
            min={0}
            max={lapData ? lapData.data.length - 1 : 0}
            value={currentIndex}
            onChange={(e) => setCurrentIndex(Number(e.target.value))}
            disabled={!lapData}
            className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-toyota-red disabled:opacity-50"
          />
        </div>

        {/* Loading Indicator */}
        {isLoading && (
          <div className="flex items-center gap-2 text-gray-400">
            <Loader2 className="w-5 h-5 animate-spin" />
            <span className="text-sm">Loading...</span>
          </div>
        )}
      </div>

      {/* Stats Bar */}
      {lapData && (
        <div className="mt-4 pt-4 border-t border-white/10 flex flex-wrap gap-6">
          <div>
            <span className="text-xs text-gray-400">Max Speed</span>
            <p className="text-lg font-bold text-cyan-400">{Math.round(lapData.stats.max_speed)} km/h</p>
          </div>
          <div>
            <span className="text-xs text-gray-400">Avg Speed</span>
            <p className="text-lg font-bold text-green-400">{Math.round(lapData.stats.avg_speed)} km/h</p>
          </div>
          <div>
            <span className="text-xs text-gray-400">Max RPM</span>
            <p className="text-lg font-bold text-orange-400">{Math.round(lapData.stats.max_rpm)}</p>
          </div>
          <div>
            <span className="text-xs text-gray-400">Lap Distance</span>
            <p className="text-lg font-bold text-purple-400">{Math.round(lapData.stats.distance)} m</p>
          </div>
        </div>
      )}
    </div>
  );
}
