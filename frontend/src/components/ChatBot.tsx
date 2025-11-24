import { useState, useRef, useEffect } from 'react';
import { useStore } from '../store/useStore';
import { sendChatMessage } from '../api';
import { MessageCircle, Send, X, Bot, User, Loader2 } from 'lucide-react';

export function ChatBot() {
  const { messages, addMessage, isChatOpen, toggleChat, currentLap } = useStore();
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setInput('');
    addMessage({ role: 'user', content: userMessage });
    setIsLoading(true);

    try {
      const response = await sendChatMessage(userMessage, currentLap || undefined);
      addMessage({
        role: 'assistant',
        content: response.response,
        plot_type: response.plot_type,
      });
    } catch (error) {
      addMessage({
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please check if the backend is running.',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const quickQuestions = [
    'Analyze my speed',
    'How is my braking?',
    'Compare throttle usage',
    'Where can I improve?',
  ];

  return (
    <>
      {/* Toggle Button */}
      <button
        onClick={toggleChat}
        className={`fixed bottom-6 right-6 z-50 w-14 h-14 rounded-full flex items-center justify-center shadow-lg transition-all duration-300 ${
          isChatOpen ? 'bg-gray-700 rotate-90' : 'bg-toyota-red hover:bg-toyota-darkRed glow-red'
        }`}
      >
        {isChatOpen ? (
          <X className="w-6 h-6 text-white" />
        ) : (
          <MessageCircle className="w-6 h-6 text-white" />
        )}
      </button>

      {/* Chat Panel */}
      <div
        className={`fixed bottom-24 right-6 z-40 w-[32rem] max-h-[700px] glass rounded-2xl shadow-2xl transition-all duration-300 overflow-hidden ${
          isChatOpen ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4 pointer-events-none'
        }`}
      >
        {/* Header */}
        <div className="bg-gradient-to-r from-toyota-red to-red-700 p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-white/20 flex items-center justify-center">
              <Bot className="w-6 h-6 text-white" />
            </div>
            <div>
              <h3 className="font-bold text-white">GR-Pilot Assistant</h3>
              <p className="text-xs text-white/70">AI Race Engineer</p>
            </div>
          </div>
        </div>

        {/* Messages */}
        <div className="h-[28rem] overflow-y-auto p-4 space-y-4">
          {messages.length === 0 && (
            <div className="text-center py-8">
              <Bot className="w-12 h-12 text-gray-500 mx-auto mb-3" />
              <p className="text-gray-400 text-sm">
                Hi! I'm your AI race engineer. Ask me about your telemetry data.
              </p>
              <div className="mt-4 flex flex-wrap gap-2 justify-center">
                {quickQuestions.map((q, i) => (
                  <button
                    key={i}
                    onClick={() => setInput(q)}
                    className="text-xs px-3 py-1.5 rounded-full bg-white/5 hover:bg-white/10 text-gray-300 transition-colors"
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map((msg, i) => (
            <div
              key={i}
              className={`flex gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}
            >
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                  msg.role === 'user' ? 'bg-blue-600' : 'bg-toyota-red'
                }`}
              >
                {msg.role === 'user' ? (
                  <User className="w-4 h-4 text-white" />
                ) : (
                  <Bot className="w-4 h-4 text-white" />
                )}
              </div>
              <div
                className={`max-w-[85%] rounded-2xl px-4 py-3 ${
                  msg.role === 'user'
                    ? 'bg-blue-600 text-white rounded-br-sm'
                    : 'bg-white/10 text-gray-200 rounded-bl-sm'
                }`}
              >
                <p className="text-sm whitespace-pre-wrap leading-relaxed">{msg.content}</p>
                {msg.plot_type && (
                  <p className="text-xs mt-2 text-gray-400">
                    📊 Suggested chart: {msg.plot_type}
                  </p>
                )}
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="flex gap-3">
              <div className="w-8 h-8 rounded-full bg-toyota-red flex items-center justify-center">
                <Bot className="w-4 h-4 text-white" />
              </div>
              <div className="bg-white/10 rounded-2xl rounded-bl-sm px-4 py-3">
                <Loader2 className="w-5 h-5 text-gray-400 animate-spin" />
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="p-4 border-t border-white/10">
          <div className="flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSend()}
              placeholder="Ask about your lap..."
              className="flex-1 bg-white/5 border border-white/10 rounded-xl px-4 py-2 text-white placeholder-gray-500 focus:outline-none focus:border-toyota-red transition-colors"
            />
            <button
              onClick={handleSend}
              disabled={isLoading || !input.trim()}
              className="w-10 h-10 rounded-xl bg-toyota-red hover:bg-toyota-darkRed disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center transition-colors"
            >
              <Send className="w-5 h-5 text-white" />
            </button>
          </div>
        </div>
      </div>
    </>
  );
}
