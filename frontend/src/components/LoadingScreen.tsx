import { Car } from 'lucide-react';

export function LoadingScreen() {
  return (
    <div className="fixed inset-0 bg-black z-50 flex items-center justify-center animate-fade-in">
      {/* Animated Background */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-toyota-red/10 via-black to-toyota-red/5 animate-pulse-slow" />
        <div className="racing-stripes absolute inset-0 opacity-10" />
      </div>

      {/* Content */}
      <div className="relative z-10 text-center">
        {/* Logo */}
        <div className="flex justify-center mb-8 animate-scale-in">
          <div className="w-24 h-24 rounded-2xl bg-gradient-to-br from-toyota-red to-red-700 flex items-center justify-center glow-red">
            <Car className="w-14 h-14 text-white animate-pulse" />
          </div>
        </div>

        {/* Text */}
        <h1 className="text-4xl font-bold mb-2 text-glow animate-slide-in">
          GR-<span className="text-toyota-red">Pilot</span>
        </h1>
        <p className="text-gray-400 mb-8 animate-slide-in" style={{ animationDelay: '0.1s' }}>
          Toyota Gazoo Racing Analytics Platform
        </p>

        {/* Loading Bar */}
        <div className="w-64 h-2 bg-white/10 rounded-full overflow-hidden mx-auto animate-slide-in" style={{ animationDelay: '0.2s' }}>
          <div className="h-full bg-gradient-to-r from-toyota-red via-red-500 to-toyota-red animate-loading-bar" />
        </div>

        {/* Status Text */}
        <p className="text-sm text-gray-500 mt-4 animate-pulse">
          Initializing race systems...
        </p>
      </div>

      <style>{`
        @keyframes loading-bar {
          0% {
            transform: translateX(-100%);
          }
          100% {
            transform: translateX(100%);
          }
        }

        .animate-loading-bar {
          animation: loading-bar 1.5s ease-in-out infinite;
        }
      `}</style>
    </div>
  );
}
