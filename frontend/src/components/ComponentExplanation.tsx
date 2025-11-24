import { useEffect, useState, useRef } from 'react';
import { HelpCircle, X } from 'lucide-react';
import { fetchComponentExplanation } from '../api';
import { useStore } from '../store/useStore';

interface ComponentExplanationProps {
  componentName: string;
  className?: string;
}

interface ExplanationData {
  what_is_it: string;
  why_important: string;
  what_happened: string;
  graph_meaning: string;
}

export function ComponentExplanation({ componentName, className = '' }: ComponentExplanationProps) {
  const { currentLap } = useStore();
  const [isOpen, setIsOpen] = useState(false);
  const [data, setData] = useState<ExplanationData | null>(null);
  const [loading, setLoading] = useState(false);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);

  const loadExplanation = async () => {
    if (!currentLap || data) return; // Only load once
    setLoading(true);
    try {
      const explanation = await fetchComponentExplanation(componentName, currentLap);
      setData(explanation);
    } catch (error) {
      console.error('Failed to load explanation:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen && !data && currentLap) {
      loadExplanation();
    }
  }, [isOpen, currentLap]);

  // Reload when lap changes
  useEffect(() => {
    setData(null);
  }, [currentLap]);

  const handleMouseEnter = () => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
    !data && loadExplanation();
    setIsOpen(true);
  };

  const handleMouseLeave = () => {
    timeoutRef.current = setTimeout(() => {
      setIsOpen(false);
    }, 100);
  };

  return (
    <div
      className={`relative ${className}`}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
    >
      {/* Help Icon Button */}
      <button
        className="p-1.5 rounded-lg bg-white/5 hover:bg-white/10 transition-all duration-200 group"
        title="Hover to learn more"
      >
        <HelpCircle className="w-4 h-4 text-gray-400 group-hover:text-toyota-red transition-colors" />
      </button>

      {/* Explanation Popup */}
      {isOpen && (
        <>
          {/* Backdrop - Solid not transparent */}
          <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-40" />

          {/* Popup - Smaller and more compact */}
          <div className="fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 z-50 w-[85vw] max-w-xl max-h-[70vh] overflow-y-auto">
            <div className="glass rounded-2xl shadow-2xl border border-white/20">
              {/* Header */}
              <div className="bg-gradient-to-r from-toyota-red to-red-700 p-4 rounded-t-2xl flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-white/20 flex items-center justify-center">
                    <HelpCircle className="w-5 h-5 text-white" />
                  </div>
                  <h3 className="text-lg font-bold text-white">Component Explanation</h3>
                </div>
                <button
                  onClick={() => setIsOpen(false)}
                  className="p-2 hover:bg-white/10 rounded-lg transition-colors"
                >
                  <X className="w-5 h-5 text-white" />
                </button>
              </div>

              {/* Content */}
              <div className="p-6 space-y-5">
                {loading ? (
                  <div className="flex items-center justify-center py-12">
                    <div className="animate-spin rounded-full h-12 w-12 border-4 border-toyota-red border-t-transparent"></div>
                  </div>
                ) : data ? (
                  <>
                    {/* What is it */}
                    <div className="space-y-2">
                      <div className="flex items-center gap-2">
                        <div className="w-1 h-6 bg-blue-500 rounded"></div>
                        <h4 className="text-sm font-bold text-blue-400 uppercase tracking-wider">What is it?</h4>
                      </div>
                      <p className="text-gray-200 leading-relaxed pl-3">{data.what_is_it}</p>
                    </div>

                    {/* Why Important */}
                    <div className="space-y-2">
                      <div className="flex items-center gap-2">
                        <div className="w-1 h-6 bg-orange-500 rounded"></div>
                        <h4 className="text-sm font-bold text-orange-400 uppercase tracking-wider">Why Important?</h4>
                      </div>
                      <p className="text-gray-200 leading-relaxed pl-3">{data.why_important}</p>
                    </div>

                    {/* What Happened */}
                    <div className="space-y-2">
                      <div className="flex items-center gap-2">
                        <div className="w-1 h-6 bg-green-500 rounded"></div>
                        <h4 className="text-sm font-bold text-green-400 uppercase tracking-wider">What Happened This Lap?</h4>
                      </div>
                      <div className="pl-3 p-3 rounded-lg bg-green-500/10 border border-green-500/30">
                        <p className="text-gray-200 leading-relaxed">{data.what_happened}</p>
                      </div>
                    </div>

                    {/* Graph Meaning */}
                    <div className="space-y-2">
                      <div className="flex items-center gap-2">
                        <div className="w-1 h-6 bg-purple-500 rounded"></div>
                        <h4 className="text-sm font-bold text-purple-400 uppercase tracking-wider">Graph Meaning</h4>
                      </div>
                      <p className="text-gray-200 leading-relaxed pl-3">{data.graph_meaning}</p>
                    </div>

                    {/* Lap Info */}
                    <div className="pt-4 border-t border-white/10">
                      <p className="text-xs text-gray-500 text-center">
                        Explanation for <span className="text-toyota-red font-semibold">Lap {currentLap}</span>
                      </p>
                    </div>
                  </>
                ) : (
                  <div className="text-center py-8">
                    <p className="text-gray-400">Failed to load explanation</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
