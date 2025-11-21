import { useState } from 'react';
import { useStore } from '../store/useStore';
import { fetchReport } from '../api';
import { FileText, Download, Loader2, CheckCircle, AlertTriangle } from 'lucide-react';

interface ReportData {
  report_type: string;
  lap_number: number;
  lap_time: number;
  best_lap: number;
  best_lap_time: number;
  statistics: {
    max_speed: number;
    avg_speed: number;
    min_speed: number;
    max_rpm: number;
    avg_rpm: number;
    avg_throttle: number;
    max_brake: number;
    distance: number;
  };
  anomalies: {
    count: number;
    details: Array<{ distance: number; speed_delta: number; reason?: string }>;
  };
  suggestions: Array<{ title: string; description: string; priority: string }>;
  weather: Record<string, unknown>;
  summary: string;
}

export function ReportExport() {
  const { currentLap } = useStore();
  const [report, setReport] = useState<ReportData | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [showPreview, setShowPreview] = useState(false);

  const generateReport = async () => {
    if (!currentLap) return;
    setIsLoading(true);
    try {
      const data = await fetchReport(currentLap);
      setReport(data);
      setShowPreview(true);
    } catch (error) {
      console.error('Failed to generate report:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const downloadAsHTML = () => {
    if (!report) return;

    const htmlContent = `
<!DOCTYPE html>
<html>
<head>
  <title>GR-Pilot Lap Analysis Report - Lap ${report.lap_number}</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #1a1a2e; color: white; padding: 40px; }
    .container { max-width: 800px; margin: 0 auto; }
    .header { text-align: center; margin-bottom: 40px; border-bottom: 2px solid #EB0A1E; padding-bottom: 20px; }
    .header h1 { color: #EB0A1E; margin: 0; }
    .header p { color: #888; margin-top: 10px; }
    .section { background: rgba(255,255,255,0.05); border-radius: 12px; padding: 20px; margin-bottom: 20px; }
    .section h2 { color: #EB0A1E; margin-top: 0; font-size: 18px; border-bottom: 1px solid #333; padding-bottom: 10px; }
    .stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; }
    .stat-card { background: rgba(255,255,255,0.05); border-radius: 8px; padding: 15px; text-align: center; }
    .stat-card .value { font-size: 24px; font-weight: bold; color: #00ffff; }
    .stat-card .label { font-size: 12px; color: #888; margin-top: 5px; }
    .anomaly { background: rgba(235,10,30,0.1); border-left: 3px solid #EB0A1E; padding: 10px 15px; margin: 10px 0; border-radius: 0 8px 8px 0; }
    .suggestion { background: rgba(255,200,0,0.1); border-left: 3px solid #ffc800; padding: 10px 15px; margin: 10px 0; border-radius: 0 8px 8px 0; }
    .summary { background: linear-gradient(135deg, rgba(235,10,30,0.1), rgba(0,0,0,0)); border: 1px solid #EB0A1E; border-radius: 12px; padding: 20px; font-style: italic; }
    .footer { text-align: center; color: #666; margin-top: 40px; padding-top: 20px; border-top: 1px solid #333; }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>🏎️ GR-Pilot Lap Analysis Report</h1>
      <p>Toyota GR Cup Series - Circuit of the Americas</p>
    </div>

    <div class="section">
      <h2>📊 Lap Overview</h2>
      <div class="stats-grid">
        <div class="stat-card">
          <div class="value">${report.lap_number}</div>
          <div class="label">Lap Number</div>
        </div>
        <div class="stat-card">
          <div class="value">${report.lap_time.toFixed(2)}s</div>
          <div class="label">Lap Time</div>
        </div>
        <div class="stat-card">
          <div class="value">${report.best_lap}</div>
          <div class="label">Best Lap</div>
        </div>
        <div class="stat-card">
          <div class="value">${(report.lap_time - report.best_lap_time).toFixed(2)}s</div>
          <div class="label">Delta</div>
        </div>
      </div>
    </div>

    <div class="section">
      <h2>⚡ Performance Statistics</h2>
      <div class="stats-grid">
        <div class="stat-card">
          <div class="value" style="color: #00ff88">${report.statistics.max_speed.toFixed(1)}</div>
          <div class="label">Max Speed (km/h)</div>
        </div>
        <div class="stat-card">
          <div class="value" style="color: #ffa500">${report.statistics.avg_speed.toFixed(1)}</div>
          <div class="label">Avg Speed (km/h)</div>
        </div>
        <div class="stat-card">
          <div class="value" style="color: #ff6b6b">${report.statistics.max_rpm.toFixed(0)}</div>
          <div class="label">Max RPM</div>
        </div>
        <div class="stat-card">
          <div class="value" style="color: #4ecdc4">${report.statistics.avg_throttle.toFixed(1)}%</div>
          <div class="label">Avg Throttle</div>
        </div>
      </div>
    </div>

    <div class="section">
      <h2>⚠️ Anomalies Detected (${report.anomalies.count})</h2>
      ${report.anomalies.details.slice(0, 5).map(a => `
        <div class="anomaly">
          <strong>Distance: ${Math.round(a.distance)}m</strong> - Speed Loss: ${Math.round(a.speed_delta)} km/h
          ${a.reason ? `<br><small>${a.reason}</small>` : ''}
        </div>
      `).join('')}
      ${report.anomalies.count > 5 ? `<p style="color:#888">+ ${report.anomalies.count - 5} more anomalies</p>` : ''}
    </div>

    <div class="section">
      <h2>💡 Improvement Suggestions</h2>
      ${report.suggestions.map(s => `
        <div class="suggestion">
          <strong>${s.title}</strong><br>
          <small>${s.description}</small>
        </div>
      `).join('')}
    </div>

    <div class="section summary">
      <h2>📝 AI Engineer Summary</h2>
      <p>${report.summary}</p>
    </div>

    <div class="footer">
      <p>Generated by GR-Pilot AI Debrief Assistant</p>
      <p>Toyota GR Cup Series Analytics Dashboard</p>
    </div>
  </div>
</body>
</html>`;

    const blob = new Blob([htmlContent], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `GR-Pilot_Lap${report.lap_number}_Report.html`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const downloadAsJSON = () => {
    if (!report) return;
    const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `GR-Pilot_Lap${report.lap_number}_Report.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="glass rounded-xl p-4">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-purple-500/20 flex items-center justify-center">
            <FileText className="w-5 h-5 text-purple-400" />
          </div>
          <div>
            <h3 className="font-medium text-white">Export Report</h3>
            <p className="text-xs text-gray-400">Generate analysis report</p>
          </div>
        </div>
      </div>

      {/* Generate Button */}
      {!showPreview && (
        <button
          onClick={generateReport}
          disabled={isLoading || !currentLap}
          className="w-full py-3 rounded-lg bg-purple-600 hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 transition-colors"
        >
          {isLoading ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              Generating...
            </>
          ) : (
            <>
              <FileText className="w-5 h-5" />
              Generate Report
            </>
          )}
        </button>
      )}

      {/* Report Preview */}
      {showPreview && report && (
        <div className="space-y-4">
          {/* Quick Stats */}
          <div className="grid grid-cols-2 gap-2">
            <div className="p-2 rounded-lg bg-white/5 text-center">
              <p className="text-xs text-gray-400">Lap Time</p>
              <p className="font-bold text-white">{report.lap_time.toFixed(2)}s</p>
            </div>
            <div className="p-2 rounded-lg bg-white/5 text-center">
              <p className="text-xs text-gray-400">Anomalies</p>
              <p className="font-bold text-red-400">{report.anomalies.count}</p>
            </div>
          </div>

          {/* Summary Preview */}
          <div className="p-3 rounded-lg bg-white/5 border border-white/10">
            <p className="text-xs text-gray-400 mb-1">AI Summary</p>
            <p className="text-sm text-gray-300 line-clamp-3">{report.summary}</p>
          </div>

          {/* Download Buttons */}
          <div className="flex gap-2">
            <button
              onClick={downloadAsHTML}
              className="flex-1 py-2 rounded-lg bg-toyota-red hover:bg-toyota-darkRed flex items-center justify-center gap-2 transition-colors"
            >
              <Download className="w-4 h-4" />
              HTML
            </button>
            <button
              onClick={downloadAsJSON}
              className="flex-1 py-2 rounded-lg bg-white/10 hover:bg-white/20 flex items-center justify-center gap-2 transition-colors"
            >
              <Download className="w-4 h-4" />
              JSON
            </button>
          </div>

          {/* Generate New */}
          <button
            onClick={() => setShowPreview(false)}
            className="w-full py-2 rounded-lg bg-white/5 hover:bg-white/10 text-gray-400 text-sm transition-colors"
          >
            Generate New Report
          </button>
        </div>
      )}
    </div>
  );
}
