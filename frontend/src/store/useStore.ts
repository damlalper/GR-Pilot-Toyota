import { create } from 'zustand';
import { LapData, ChatMessage } from '../types';

export interface AppState {
  // Data
  laps: number[];
  currentLap: number | null;
  selectedLap?: number | null;
  lapData: LapData | null;
  comparisonLapData: LapData | null;
  isLoading: boolean;

  // Replay
  isPlaying: boolean;
  playbackSpeed: number;
  currentIndex: number;

  // Chat
  messages: ChatMessage[];
  isChatOpen: boolean;

  // Actions
  setLaps: (laps: number[]) => void;
  setCurrentLap: (lap: number) => void;
  setSelectedLap?: (lap: number | null) => void;
  setLapData: (data: LapData) => void;
  setComparisonLapData: (data: LapData | null) => void;
  setIsLoading: (loading: boolean) => void;
  setIsPlaying: (playing: boolean) => void;
  setPlaybackSpeed: (speed: number) => void;
  setCurrentIndex: (index: number) => void;
  addMessage: (message: ChatMessage) => void;
  toggleChat: () => void;
}

export const useStore = create<AppState>((set) => ({
  laps: [],
  currentLap: null,
  lapData: null,
  comparisonLapData: null,
  isLoading: false,
  isPlaying: false,
  playbackSpeed: 5,
  currentIndex: 0,
  messages: [],
  isChatOpen: false,

  setLaps: (laps) => set({ laps }),
  setCurrentLap: (lap) => set({ currentLap: lap, currentIndex: 0 }),
  setLapData: (data) => set({ lapData: data }),
  setComparisonLapData: (data) => set({ comparisonLapData: data }),
  setIsLoading: (loading) => set({ isLoading: loading }),
  setIsPlaying: (playing) => set({ isPlaying: playing }),
  setPlaybackSpeed: (speed) => set({ playbackSpeed: speed }),
  setCurrentIndex: (index) => set({ currentIndex: index }),
  addMessage: (message) => set((state) => ({ messages: [...state.messages, message] })),
  toggleChat: () => set((state) => ({ isChatOpen: !state.isChatOpen })),
}));
