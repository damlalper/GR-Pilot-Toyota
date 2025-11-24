import axios from 'axios';
import { LapData, TrackData } from '../types';

// Use environment variable for API URL, fallback to localhost for development
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  timeout: 30000,
});

export const fetchLaps = async (): Promise<number[]> => {
  const response = await api.get('/api/laps');
  return response.data;
};

export const fetchLapData = async (lap: number, points = 500): Promise<LapData> => {
  const response = await api.get(`/api/lap/${lap}`, { params: { points } });
  return response.data;
};

export const fetchTrackData = async (): Promise<TrackData> => {
  const response = await api.get('/api/track');
  return response.data;
};

export const fetchWeather = async () => {
  const response = await api.get('/api/weather');
  return response.data;
};

export const sendChatMessage = async (message: string, lap?: number) => {
  const response = await api.post('/api/chat', { message, lap });
  return response.data;
};

// New API endpoints
export const fetchBestLap = async () => {
  const response = await api.get('/api/best_lap');
  return response.data;
};

export const fetchAnomalies = async (lap: number, refLap?: number, threshold = 15) => {
  const params: Record<string, unknown> = { threshold };
  if (refLap) params.ref_lap = refLap;
  const response = await api.get(`/api/anomalies/${lap}`, { params });
  return response.data;
};

export const fetchLapComparison = async (lap1: number, lap2: number, points = 200) => {
  const response = await api.get(`/api/compare/${lap1}/${lap2}`, { params: { points } });
  return response.data;
};

export const fetchSuggestions = async (lap: number) => {
  const response = await api.get(`/api/suggestions/${lap}`);
  return response.data;
};

export const fetchReport = async (lap: number) => {
  const response = await api.get(`/api/report/${lap}`);
  return response.data;
};

// Unique winning features
export const fetchDriverDNA = async (lap: number) => {
  const response = await api.get(`/api/driver_dna/${lap}`);
  return response.data;
};

export const fetchGripIndex = async (lap: number) => {
  const response = await api.get(`/api/grip_index/${lap}`);
  return response.data;
};

export const fetchSectors = async (lap: number) => {
  const response = await api.get(`/api/sectors/${lap}`);
  return response.data;
};

export const fetchRiskHeatmap = async (lap: number) => {
  const response = await api.get(`/api/risk_heatmap/${lap}`);
  return response.data;
};

export const fetchTireStress = async (lap: number) => {
  const response = await api.get(`/api/tire_stress/${lap}`);
  return response.data;
};

// Missing exports
export const fetchBestLaps = async () => {
  const response = await api.get('/api/best_laps');
  return response.data;
};

export const fetchMLValidation = async () => {
  const response = await api.get('/api/ml/validation');
  return response.data;
};

export const fetchPerfectLap = async (laps: number[]) => {
  const response = await api.post('/api/perfect_lap', { laps });
  return response.data;
};

export const fetchCPI = async (lap: number) => {
  const response = await api.get(`/cpi/${lap}`);
  return response.data;
};

export const fetchPitStrategy = async (lap: number, raceLaps = 30) => {
  const response = await api.get(`/pit_strategy/${lap}`, { params: { race_laps: raceLaps } });
  return response.data;
};

export const fetchRaceStory = async (lap: number) => {
  const response = await api.get(`/race_story/${lap}`);
  return response.data;
};

export const fetchComponentExplanation = async (component: string, lap: number) => {
  const response = await api.get(`/api/component_explanation/${component}/${lap}`);
  return response.data;
};

export { api };
