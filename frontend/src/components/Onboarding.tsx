import { useState, useEffect } from 'react';
import { ChevronRight, ChevronLeft, X, Zap, Target, Brain, TrendingUp, Sparkles, Play } from 'lucide-react';

interface OnboardingProps {
  onComplete: () => void;
}

const steps = [
  {
    id: 1,
    icon: Sparkles,
    iconColor: 'text-yellow-400',
    bgGradient: 'from-yellow-500/20 via-orange-500/10 to-red-500/20',
    title: 'Welcome to GR-Pilot',
    subtitle: 'Your AI Racing Engineer',
    description: 'Transform raw racing data into winning insights. We analyze every millisecond of your lap to help you drive faster.',
    visual: (
      <div className="relative w-64 h-64 mx-auto">
        <div className="absolute inset-0 bg-gradient-to-br from-toyota-red/30 to-yellow-400/30 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute inset-8 bg-gradient-to-br from-toyota-red to-yellow-400 rounded-full flex items-center justify-center">
          <Sparkles className="w-24 h-24 text-white animate-bounce" />
        </div>
      </div>
    ),
  },
  {
    id: 2,
    icon: Target,
    iconColor: 'text-blue-400',
    bgGradient: 'from-blue-500/20 via-cyan-500/10 to-blue-500/20',
    title: 'Every Mistake, Instantly Found',
    subtitle: 'Smart Anomaly Detection',
    description: 'Our AI spots every late brake, rough corner entry, and wasted opportunity — even ones you didn\'t notice. Think of it like having an expert coach watching your every move.',
    visual: (
      <div className="relative w-full h-64 flex items-center justify-center">
        <div className="absolute w-48 h-48 border-4 border-blue-500/30 rounded-full animate-ping"></div>
        <div className="absolute w-32 h-32 border-4 border-red-500/50 rounded-full"></div>
        <Target className="w-16 h-16 text-toyota-red animate-pulse z-10" />
        <div className="absolute top-8 right-8 w-3 h-3 bg-red-500 rounded-full animate-bounce"></div>
        <div className="absolute bottom-12 left-12 w-3 h-3 bg-orange-500 rounded-full animate-bounce delay-100"></div>
        <div className="absolute top-16 left-16 w-3 h-3 bg-yellow-500 rounded-full animate-bounce delay-200"></div>
      </div>
    ),
  },
  {
    id: 3,
    icon: Zap,
    iconColor: 'text-purple-400',
    bgGradient: 'from-purple-500/20 via-pink-500/10 to-purple-500/20',
    title: 'The Butterfly Effect',
    subtitle: 'Why Small Mistakes Cost Big Time',
    description: 'A slow corner exit doesn\'t just hurt that corner — it costs you speed down the entire next straight. We calculate the real damage so you know where to focus.',
    visual: (
      <div className="relative w-full h-64 flex items-center justify-center">
        <div className="absolute left-8">
          <div className="w-12 h-12 bg-yellow-500/20 rounded-full flex items-center justify-center">
            <div className="w-6 h-6 bg-yellow-500 rounded-full"></div>
          </div>
          <p className="text-xs text-gray-400 mt-2">Slow exit</p>
        </div>
        <div className="absolute left-1/2 transform -translate-x-1/2 flex items-center gap-2">
          <ChevronRight className="w-6 h-6 text-toyota-red animate-pulse" />
          <ChevronRight className="w-6 h-6 text-toyota-red animate-pulse delay-75" />
          <ChevronRight className="w-6 h-6 text-toyota-red animate-pulse delay-150" />
        </div>
        <div className="absolute right-8">
          <div className="w-16 h-16 bg-red-500/20 rounded-full flex items-center justify-center">
            <div className="w-10 h-10 bg-red-500 rounded-full"></div>
          </div>
          <p className="text-xs text-gray-400 mt-2">Big time loss</p>
        </div>
      </div>
    ),
  },
  {
    id: 4,
    icon: Brain,
    iconColor: 'text-green-400',
    bgGradient: 'from-green-500/20 via-emerald-500/10 to-green-500/20',
    title: 'AI That Speaks Your Language',
    subtitle: 'No Engineering Degree Required',
    description: 'Ask anything in plain English. "Why am I losing time in sector 2?" or "How can I improve my braking?" — our AI explains it like a coach, not a textbook.',
    visual: (
      <div className="relative w-full h-64 flex flex-col items-center justify-center gap-4">
        <div className="bg-blue-600 rounded-2xl p-3 max-w-xs rounded-br-sm">
          <p className="text-sm text-white">Why am I slow in turn 3?</p>
        </div>
        <div className="bg-white/10 rounded-2xl p-3 max-w-xs rounded-bl-sm">
          <p className="text-sm text-gray-200">You're braking too early! Try carrying more speed into the corner...</p>
        </div>
        <Brain className="w-8 h-8 text-green-400 animate-pulse" />
      </div>
    ),
  },
  {
    id: 5,
    icon: TrendingUp,
    iconColor: 'text-orange-400',
    bgGradient: 'from-orange-500/20 via-red-500/10 to-orange-500/20',
    title: 'Your Perfect Lap Awaits',
    subtitle: 'Data-Driven Performance',
    description: 'See exactly how much faster you could go by combining your best sectors. Track your progress lap by lap, sector by sector. Turn data into trophies.',
    visual: (
      <div className="relative w-full h-64 flex items-center justify-center">
        <svg viewBox="0 0 200 120" className="w-full h-48">
          <polyline
            points="10,100 50,80 90,85 130,60 170,65 190,40"
            fill="none"
            stroke="url(#gradient)"
            strokeWidth="3"
            strokeLinecap="round"
            className="animate-draw"
          />
          <defs>
            <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#ef4444" />
              <stop offset="50%" stopColor="#f59e0b" />
              <stop offset="100%" stopColor="#10b981" />
            </linearGradient>
          </defs>
          <circle cx="190" cy="40" r="6" fill="#10b981" className="animate-pulse" />
        </svg>
        <div className="absolute bottom-4 right-4 bg-green-500/20 rounded-lg px-3 py-1 border border-green-500/30">
          <p className="text-sm text-green-400 font-bold">↑ Faster</p>
        </div>
      </div>
    ),
  },
];

export function Onboarding({ onComplete }: OnboardingProps) {
  const [currentStep, setCurrentStep] = useState(0);
  const [showSkipConfirm, setShowSkipConfirm] = useState(false);

  const currentStepData = steps[currentStep];
  const isLastStep = currentStep === steps.length - 1;

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'ArrowRight' && !isLastStep) {
        handleNext();
      } else if (e.key === 'ArrowLeft' && currentStep > 0) {
        handlePrev();
      } else if (e.key === 'Enter' && isLastStep) {
        handleComplete();
      } else if (e.key === 'Escape') {
        handleSkip();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [currentStep, isLastStep]);

  const handleNext = () => {
    if (isLastStep) {
      handleComplete();
    } else {
      setCurrentStep(prev => prev + 1);
    }
  };

  const handlePrev = () => {
    setCurrentStep(prev => Math.max(0, prev - 1));
  };

  const handleComplete = () => {
    localStorage.setItem('onboarding_completed', 'true');
    onComplete();
  };

  const handleSkip = () => {
    if (!showSkipConfirm) {
      setShowSkipConfirm(true);
      setTimeout(() => setShowSkipConfirm(false), 3000);
    } else {
      handleComplete();
    }
  };

  const Icon = currentStepData.icon;

  return (
    <div className="fixed inset-0 z-50 bg-gradient-to-br from-gray-900 via-black to-gray-900 flex items-center justify-center overflow-hidden">
      {/* Background animated gradients */}
      <div className={`absolute inset-0 bg-gradient-to-br ${currentStepData.bgGradient} transition-all duration-1000`}></div>
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(239,68,68,0.1),transparent_50%)] animate-pulse-slow"></div>

      {/* Skip button */}
      <button
        onClick={handleSkip}
        className="absolute top-6 right-6 z-10 px-4 py-2 rounded-lg bg-white/5 hover:bg-white/10 text-gray-400 hover:text-white transition-all duration-200 flex items-center gap-2 group"
        aria-label="Skip onboarding tour"
      >
        {showSkipConfirm ? (
          <>
            <span className="text-sm">Click again to skip</span>
            <X className="w-4 h-4" />
          </>
        ) : (
          <>
            <span className="text-sm">Skip</span>
            <ChevronRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
          </>
        )}
      </button>

      {/* Main content */}
      <div className="relative z-10 max-w-4xl w-full px-8 py-12">
        <div className="bg-black/40 backdrop-blur-xl rounded-3xl border border-white/10 shadow-2xl overflow-hidden">
          {/* Step indicator */}
          <div className="px-8 pt-8 pb-4">
            <div className="flex items-center justify-center gap-2">
              {steps.map((_, index) => (
                <div
                  key={index}
                  className={`h-1.5 rounded-full transition-all duration-300 ${
                    index === currentStep
                      ? 'w-12 bg-toyota-red'
                      : index < currentStep
                      ? 'w-8 bg-white/30'
                      : 'w-8 bg-white/10'
                  }`}
                  role="progressbar"
                  aria-valuenow={index === currentStep ? 100 : 0}
                  aria-valuemin={0}
                  aria-valuemax={100}
                  aria-label={`Step ${index + 1} of ${steps.length}`}
                />
              ))}
            </div>
          </div>

          {/* Content */}
          <div className="px-8 py-8 min-h-[500px] flex flex-col items-center justify-center">
            {/* Icon */}
            <div className={`w-20 h-20 rounded-2xl bg-gradient-to-br ${currentStepData.bgGradient} flex items-center justify-center mb-6 transform hover:scale-110 transition-transform duration-300`}>
              <Icon className={`w-10 h-10 ${currentStepData.iconColor}`} />
            </div>

            {/* Title */}
            <h2 className="text-4xl font-bold text-white text-center mb-2 animate-fade-in">
              {currentStepData.title}
            </h2>

            {/* Subtitle */}
            <p className="text-xl text-toyota-red font-semibold text-center mb-6 animate-fade-in delay-100">
              {currentStepData.subtitle}
            </p>

            {/* Visual */}
            <div className="mb-8 animate-fade-in delay-200">
              {currentStepData.visual}
            </div>

            {/* Description */}
            <p className="text-lg text-gray-300 text-center max-w-2xl leading-relaxed animate-fade-in delay-300">
              {currentStepData.description}
            </p>
          </div>

          {/* Navigation */}
          <div className="px-8 pb-8 flex items-center justify-between gap-4">
            <button
              onClick={handlePrev}
              disabled={currentStep === 0}
              className="px-6 py-3 rounded-xl bg-white/5 hover:bg-white/10 text-white disabled:opacity-30 disabled:cursor-not-allowed transition-all duration-200 flex items-center gap-2 group"
              aria-label="Previous step"
            >
              <ChevronLeft className="w-5 h-5 group-hover:-translate-x-1 transition-transform" />
              <span className="font-medium">Back</span>
            </button>

            <div className="text-sm text-gray-400" aria-live="polite">
              Step {currentStep + 1} of {steps.length}
            </div>

            <button
              onClick={handleNext}
              className="px-8 py-3 rounded-xl bg-gradient-to-r from-toyota-red to-red-700 hover:from-red-700 hover:to-toyota-red text-white font-bold transition-all duration-200 flex items-center gap-2 group shadow-lg shadow-toyota-red/30"
              aria-label={isLastStep ? 'Start using GR-Pilot' : 'Next step'}
            >
              <span className="text-lg">
                {isLastStep ? 'Start Racing' : 'Next'}
              </span>
              {isLastStep ? (
                <Play className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              ) : (
                <ChevronRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              )}
            </button>
          </div>
        </div>

        {/* Keyboard shortcuts hint */}
        <div className="mt-6 text-center">
          <p className="text-xs text-gray-500">
            Use <kbd className="px-2 py-1 bg-white/10 rounded text-white">←</kbd> and <kbd className="px-2 py-1 bg-white/10 rounded text-white">→</kbd> to navigate
          </p>
        </div>
      </div>
    </div>
  );
}
