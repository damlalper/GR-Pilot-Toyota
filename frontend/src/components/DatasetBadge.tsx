import { Database } from 'lucide-react';

interface DatasetBadgeProps {
  dataset: string;
  category?: string;
  className?: string;
}

export function DatasetBadge({ dataset, category, className = '' }: DatasetBadgeProps) {
  return (
    <div className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-toyota-red/10 border border-toyota-red/30 ${className}`}>
      <Database className="w-3.5 h-3.5 text-toyota-red" />
      <div className="flex flex-col items-start">
        <span className="text-[10px] font-semibold text-toyota-red uppercase tracking-wide">
          TRD Dataset
        </span>
        <span className="text-xs text-gray-300 font-medium">
          {dataset}
        </span>
        {category && (
          <span className="text-[9px] text-gray-500">
            {category}
          </span>
        )}
      </div>
    </div>
  );
}

// Preset badges for common datasets
export const DatasetBadges = {
  Telemetry: () => (
    <DatasetBadge
      dataset="R2_cota_telemetry_data.csv"
      category="Telemetry Data"
    />
  ),
  LapTimes: () => (
    <DatasetBadge
      dataset="COTA_lap_time_R2.csv"
      category="Lap Times"
    />
  ),
  Weather: () => (
    <DatasetBadge
      dataset="26_Weather_Race_2.CSV"
      category="Weather Conditions"
    />
  ),
  Sectors: () => (
    <DatasetBadge
      dataset="23_AnalysisEnduranceWithSections.CSV"
      category="Sector Analysis"
    />
  ),
  BestLaps: () => (
    <DatasetBadge
      dataset="99_Best 10 Laps By Driver.CSV"
      category="Benchmark Data"
    />
  ),
  Results: () => (
    <DatasetBadge
      dataset="05_Results by Class GR Cup.CSV"
      category="Race Results"
    />
  ),
};
