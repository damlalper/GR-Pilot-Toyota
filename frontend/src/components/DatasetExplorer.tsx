import { Database, FileText, Cloud, Activity, TrendingUp } from 'lucide-react';

export function DatasetExplorer() {
  const datasets = [
    {
      name: 'R2_cota_telemetry_data.csv',
      icon: Activity,
      category: 'Telemetry',
      size: '2.4 MB',
      records: '156,842',
      usage: ['Speed Analysis', 'Brake Pressure', 'Throttle Control', 'Gear Selection'],
      components: ['TelemetryCharts', 'DriverDNA', 'GripIndex', 'RiskHeatmap', 'TireStress']
    },
    {
      name: 'COTA_lap_time_R2.csv',
      icon: TrendingUp,
      category: 'Lap Times',
      size: '128 KB',
      records: '1,247',
      usage: ['Best Lap Detection', 'Lap Comparison', 'Performance Trends'],
      components: ['LapComparison', 'BestLaps', 'PerfectLap', 'Controls']
    },
    {
      name: '26_Weather_Race_2.CSV',
      icon: Cloud,
      category: 'Weather',
      size: '64 KB',
      records: '342',
      usage: ['Track Temperature', 'Air Pressure', 'Humidity Analysis'],
      components: ['WeatherPanel', 'GripIndex']
    },
    {
      name: '23_AnalysisEnduranceWithSections.CSV',
      icon: Database,
      category: 'Sectors',
      size: '512 KB',
      records: '8,934',
      usage: ['Sector Times', 'Mini-Sector Analysis', 'Perfect Lap Construction'],
      components: ['SectorAnalysis', 'PerfectLap', 'TrackMap']
    },
    {
      name: '99_Best 10 Laps By Driver.CSV',
      icon: FileText,
      category: 'Benchmark',
      size: '32 KB',
      records: '240',
      usage: ['Driver Benchmarking', 'Top 10 Performance', 'Average Best Times'],
      components: ['BestLaps', 'MLValidation', 'PerfectLap']
    }
  ];

  return (
    <div className="glass rounded-xl p-6 border-2 border-toyota-red/20">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-toyota-red to-red-700 flex items-center justify-center">
          <Database className="w-7 h-7 text-white" />
        </div>
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            TRD Dataset Explorer
            <span className="px-2 py-0.5 rounded-full bg-toyota-red/20 text-toyota-red text-xs font-normal">
              100% Real Data
            </span>
          </h2>
          <p className="text-sm text-gray-400">Toyota Racing Development • Circuit of the Americas</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
        {datasets.map((dataset, i) => {
          const Icon = dataset.icon;
          return (
            <div key={i} className="bg-gradient-to-br from-white/5 to-white/[0.02] rounded-lg p-4 border border-white/10 hover:border-toyota-red/50 transition-all duration-300 hover:shadow-lg hover:shadow-toyota-red/10">
              <div className="flex items-start gap-3 mb-3">
                <div className="w-10 h-10 rounded-lg bg-toyota-red/20 flex items-center justify-center flex-shrink-0">
                  <Icon className="w-5 h-5 text-toyota-red" />
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="font-mono text-xs text-white mb-1 truncate" title={dataset.name}>
                    {dataset.name}
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    <span className="px-2 py-0.5 rounded text-[10px] bg-toyota-red/20 text-toyota-red font-semibold">
                      {dataset.category}
                    </span>
                    <span className="text-[10px] text-gray-500">{dataset.size}</span>
                  </div>
                  <div className="mt-1">
                    <span className="text-xs font-bold text-green-400">{dataset.records}</span>
                    <span className="text-[10px] text-gray-500 ml-1">records</span>
                  </div>
                </div>
              </div>

              <div className="mb-3">
                <p className="text-xs text-gray-400 mb-1.5 font-semibold">Analytics:</p>
                <div className="flex flex-wrap gap-1">
                  {dataset.usage.map((use, j) => (
                    <span key={j} className="px-2 py-0.5 rounded-full bg-white/5 text-[10px] text-gray-300 border border-white/10">
                      {use}
                    </span>
                  ))}
                </div>
              </div>

              <div>
                <p className="text-xs text-gray-400 mb-1.5 font-semibold">Components:</p>
                <div className="flex flex-wrap gap-1">
                  {dataset.components.map((comp, j) => (
                    <span key={j} className="px-2 py-0.5 rounded-full bg-blue-500/20 text-[10px] text-blue-300 border border-blue-500/30">
                      {comp}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Stats Summary */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4 border-t border-white/10 pt-4">
        <div className="text-center p-3 rounded-lg bg-white/5">
          <div className="text-2xl font-bold text-toyota-red">5</div>
          <div className="text-xs text-gray-400 mt-1">TRD Datasets</div>
        </div>
        <div className="text-center p-3 rounded-lg bg-white/5">
          <div className="text-2xl font-bold text-green-400">167K+</div>
          <div className="text-xs text-gray-400 mt-1">Total Records</div>
        </div>
        <div className="text-center p-3 rounded-lg bg-white/5">
          <div className="text-2xl font-bold text-blue-400">15+</div>
          <div className="text-xs text-gray-400 mt-1">Components</div>
        </div>
        <div className="text-center p-3 rounded-lg bg-white/5">
          <div className="text-2xl font-bold text-purple-400">3.1 MB</div>
          <div className="text-xs text-gray-400 mt-1">Data Size</div>
        </div>
        <div className="text-center p-3 rounded-lg bg-white/5">
          <div className="text-2xl font-bold text-yellow-400">100%</div>
          <div className="text-xs text-gray-400 mt-1">TRD Authentic</div>
        </div>
      </div>

      {/* Data Flow Visualization */}
      <div className="mt-4 p-4 rounded-lg bg-gradient-to-r from-toyota-red/10 to-blue-500/10 border border-white/10">
        <div className="flex items-center justify-center gap-2 text-sm">
          <span className="px-3 py-1 rounded-full bg-toyota-red/20 text-toyota-red font-semibold">TRD Data</span>
          <span className="text-gray-500">→</span>
          <span className="px-3 py-1 rounded-full bg-purple-500/20 text-purple-300 font-semibold">ML Processing</span>
          <span className="text-gray-500">→</span>
          <span className="px-3 py-1 rounded-full bg-blue-500/20 text-blue-300 font-semibold">AI Insights</span>
          <span className="text-gray-500">→</span>
          <span className="px-3 py-1 rounded-full bg-green-500/20 text-green-300 font-semibold">Dashboard</span>
        </div>
      </div>
    </div>
  );
}
