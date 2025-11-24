import { useState, useEffect } from 'react';
import {
  Header,
  Controls,
  Scene3D,
  Scene3DCompare,
  TelemetryPanel,
  TelemetryCharts,
  TrackMap,
  ChatBot,
  AnomalyOverlay,
  LapComparison,
  SuggestionsPanel,
  WeatherPanel,
  ReportExport,
  DriverDNA,
  GripIndex,
  SectorAnalysis,
  RiskHeatmap,
  TireStress,
  CompositePerformanceIndex,
  PitStrategy,
  RaceStoryTimeline,
  BestLaps,
  MLValidation,
  ButterflyEffect,
  GGDiagram,
  PerfectLap,
  Training,
} from './components';
import { Onboarding } from './components/Onboarding';
import { LayoutGrid, GitCompare, BarChart3, Target } from 'lucide-react';

type ViewMode = 'race' | 'analysis' | 'compare' | 'training';

function App() {
  const [viewMode, setViewMode] = useState<ViewMode>('race');
  const [showOnboarding, setShowOnboarding] = useState(false);

  // Always show onboarding on first load (reset on every page refresh)
  useEffect(() => {
    // Clear onboarding flag to show it every time
    localStorage.removeItem('onboarding_completed');
    setShowOnboarding(true);
  }, []);

  const handleOnboardingComplete = () => {
    setShowOnboarding(false);
  };

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <Header />

      {/* View Mode Tabs */}
      <div className="container mx-auto px-4 pt-4">
        <div className="flex gap-2 mb-4">
          <button
            onClick={() => setViewMode('race')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
              viewMode === 'race'
                ? 'bg-toyota-red text-white'
                : 'bg-white/5 text-gray-400 hover:bg-white/10'
            }`}
          >
            <LayoutGrid className="w-4 h-4" />
            Race View
          </button>
          <button
            onClick={() => setViewMode('analysis')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
              viewMode === 'analysis'
                ? 'bg-toyota-red text-white'
                : 'bg-white/5 text-gray-400 hover:bg-white/10'
            }`}
          >
            <BarChart3 className="w-4 h-4" />
            Analysis
          </button>
          <button
            onClick={() => setViewMode('compare')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
              viewMode === 'compare'
                ? 'bg-toyota-red text-white'
                : 'bg-white/5 text-gray-400 hover:bg-white/10'
            }`}
          >
            <GitCompare className="w-4 h-4" />
            Compare
          </button>
          <button
            onClick={() => setViewMode('training')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
              viewMode === 'training'
                ? 'bg-toyota-red text-white'
                : 'bg-white/5 text-gray-400 hover:bg-white/10'
            }`}
          >
            <Target className="w-4 h-4" />
            Training
          </button>
        </div>
      </div>

      {/* Main Content */}
      <main className="flex-1 container mx-auto px-4 pb-4">
        {/* Controls */}
        <div className="mb-4">
          <Controls />
        </div>

        {/* Race View */}
        {viewMode === 'race' && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
            {/* Left Column - 3D View */}
            <div className="lg:col-span-8 space-y-4">
              {/* 3D Scene */}
              <div className="h-[500px]">
                <Scene3D />
              </div>

              {/* Quick CPI Overview */}
              <div className="grid grid-cols-2 gap-4">
                <CompositePerformanceIndex />
                <PitStrategy />
              </div>

              {/* Charts */}
              <TelemetryCharts />
            </div>

            {/* Right Column - Panels */}
            <div className="lg:col-span-4 space-y-4">
              <TelemetryPanel />
              <TrackMap />
              <WeatherPanel />
            </div>
          </div>
        )}

        {/* Analysis View */}
        {viewMode === 'analysis' && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
            {/* Left Column - Anomalies & Suggestions */}
            <div className="lg:col-span-8 space-y-4">
              {/* CPI (Composite Performance Index) */}
              <CompositePerformanceIndex />

              {/* Best Laps & Perfect Lap */}
              <div className="grid grid-cols-2 gap-4">
                <BestLaps />
                <PerfectLap />
              </div>

              {/* Driver DNA & Grip Index */}
              <div className="grid grid-cols-2 gap-4">
                <DriverDNA />
                <GripIndex />
              </div>

              {/* Race Story Timeline */}
              <RaceStoryTimeline />

              {/* Sector Analysis */}
              <SectorAnalysis />

              {/* Anomalies & Suggestions */}
              <AnomalyOverlay />
              <SuggestionsPanel />

              {/* Butterfly Effect - Advanced Analysis */}
              <ButterflyEffect />

              {/* Telemetry Charts */}
              <TelemetryCharts />

              {/* GG Diagram - G-Force Analysis */}
              <GGDiagram />
            </div>

            {/* Right Column */}
            <div className="lg:col-span-4 space-y-4">
              <TelemetryPanel />

              {/* Pit Strategy Simulator */}
              <PitStrategy />

              {/* ML Validation Dashboard */}
              <MLValidation />

              {/* Risk & Tire Analysis */}
              <RiskHeatmap />
              <TireStress />

              {/* Track Map */}
              <TrackMap />

              {/* Report Export */}
              <ReportExport />
            </div>
          </div>
        )}

        {/* Compare View */}
        {viewMode === 'compare' && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
            {/* Left Column - Comparison */}
            <div className="lg:col-span-8 space-y-4">
              <LapComparison />
              <div className="h-[400px]">
                <Scene3DCompare />
              </div>
            </div>

            {/* Right Column */}
            <div className="lg:col-span-4 space-y-4">
              <AnomalyOverlay />
              <SuggestionsPanel />
              <WeatherPanel />
            </div>
          </div>
        )}

        {/* Training View */}
        {viewMode === 'training' && <Training />}
      </main>

      {/* Footer */}
      <footer className="glass border-t border-white/10 py-3">
        <div className="container mx-auto px-4 flex items-center justify-between">
          <p className="text-xs text-gray-500">
            GR-Pilot Analytics Dashboard &copy; 2024 Toyota GR Cup Series
          </p>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
            <span className="text-xs text-gray-500">Connected</span>
          </div>
        </div>
      </footer>

      {/* Floating Chat */}
      <ChatBot />

      {/* Onboarding */}
      {showOnboarding && <Onboarding onComplete={handleOnboardingComplete} />}
    </div>
  );
}

export default App;
