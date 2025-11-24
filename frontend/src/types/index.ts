export interface TelemetryPoint {
  distance: number;
  speed: number;
  nmot: number;
  ath: number;
  pbrake_f: number;
  Steering_Angle: number;
  gear: number;
  WorldPositionX: number;
  WorldPositionY: number;
  lat: number;
  lon: number;
  timestamp: string;
  accx_can?: number;
  accy_can?: number;
  ngear?: number;
}

export interface LapData {
  lap: number;
  points: number;
  data: TelemetryPoint[];
  stats: {
    max_speed: number;
    avg_speed: number;
    max_rpm: number;
    distance: number;
  };
}

export interface TrackData {
  track: TelemetryPoint[];
  bounds: {
    minX: number;
    maxX: number;
    minY: number;
    maxY: number;
  };
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  plot_type?: string | null;
}
