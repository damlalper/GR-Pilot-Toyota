"""
AI Race Engineer
GPT-4 powered natural language race engineering assistant
"""

import os
from typing import Dict, List, Optional
import logging

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

logger = logging.getLogger(__name__)


class AIRaceEngineer:
    """
    Toyota TRD AI Race Engineer
    Doğal dil ile yarış mühendisliği analizi
    """

    SYSTEM_PROMPT = """You are a professional Toyota Gazoo Racing (TRD) telemetry engineer with 10+ years of experience.

Your communication style:
- Direct, technical, and precise
- Use Toyota-specific terminology:
  - Say "tail out" not "oversteer"
  - Say "brake degradation" not "fade"
  - Say "compound degradation" not "tire wear"
- Provide engineering-focused insights
- No marketing language or fluff
- Short, actionable recommendations

Your expertise:
- Telemetry analysis (speed, brake, throttle, steering)
- Driver coaching and performance optimization
- Setup recommendations
- Race strategy
- Tire management
- Lap time optimization

When analyzing data:
1. Identify the root cause, not just symptoms
2. Quantify the impact (time loss in seconds)
3. Provide specific, measurable recommendations
4. Reference specific turns/sectors when relevant
5. Explain the physics behind the issue

Response format:
- Start with the main finding
- Explain the root cause
- Provide specific recommendation
- Estimate time gain potential

Keep responses under 150 words unless detailed analysis is requested."""

    def __init__(self, api_key: Optional[str] = None, provider: str = "openai"):
        """
        Initialize AI Race Engineer

        Args:
            api_key: API key (None = otomatik env'den al)
            provider: "openai" or "groq"
        """
        self.provider = provider.lower()
        self.client = None
        self.model = None

        if self.provider == "openai":
            if not OPENAI_AVAILABLE:
                raise ImportError("OpenAI library not installed. Install with: pip install openai")

            api_key = api_key or os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OpenAI API key not provided")

            self.client = OpenAI(api_key=api_key)
            self.model = "gpt-4-turbo-preview"
            logger.info("AI Race Engineer initialized with OpenAI GPT-4")

        elif self.provider == "groq":
            if not GROQ_AVAILABLE:
                raise ImportError("Groq library not installed. Install with: pip install groq")

            api_key = api_key or os.getenv("GROQ_API_KEY")
            if not api_key:
                raise ValueError("Groq API key not provided")

            self.client = Groq(api_key=api_key)
            self.model = "mixtral-8x7b-32768"
            logger.info("AI Race Engineer initialized with Groq Mixtral")

        else:
            raise ValueError(f"Unknown provider: {provider}")

        self.conversation_history: List[Dict] = []

    def analyze(
        self,
        query: str,
        context: Optional[Dict] = None,
        temperature: float = 0.3
    ) -> str:
        """
        Analiz yap ve yanıt üret

        Args:
            query: Kullanıcı sorusu
            context: Telemetri data context (opsiyonel)
            temperature: AI temperature (0-1)

        Returns:
            AI response string
        """
        # Context'i prompt'a ekle
        if context:
            context_str = self._format_context(context)
            full_query = f"{context_str}\n\nQuestion: {query}"
        else:
            full_query = query

        # Messages oluştur
        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT}
        ]

        # Conversation history ekle (son 5 mesaj)
        messages.extend(self.conversation_history[-10:])

        # Yeni query ekle
        messages.append({"role": "user", "content": full_query})

        try:
            # API call
            if self.provider == "openai":
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=500
                )
                answer = response.choices[0].message.content

            elif self.provider == "groq":
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=500
                )
                answer = response.choices[0].message.content

            # History'ye ekle
            self.conversation_history.append({"role": "user", "content": full_query})
            self.conversation_history.append({"role": "assistant", "content": answer})

            logger.info(f"AI analysis completed ({len(answer)} chars)")

            return answer

        except Exception as e:
            logger.error(f"AI analysis error: {str(e)}")
            return f"Error: Unable to generate analysis. {str(e)}"

    def _format_context(self, context: Dict) -> str:
        """
        Context dictionary'yi prompt string'e çevir

        Args:
            context: Data context

        Returns:
            Formatted string
        """
        lines = ["=== TELEMETRY CONTEXT ==="]

        if 'lap' in context:
            lines.append(f"Lap: {context['lap']}")

        if 'sector' in context:
            lines.append(f"Sector: {context['sector']}")

        if 'metrics' in context:
            lines.append("\nMetrics:")
            for key, value in context['metrics'].items():
                if isinstance(value, float):
                    lines.append(f"  {key}: {value:.2f}")
                else:
                    lines.append(f"  {key}: {value}")

        if 'anomalies' in context:
            lines.append(f"\nAnomalies Detected: {context['anomalies']}")

        if 'cpi' in context:
            lines.append(f"\nComposite Performance Index: {context['cpi']}/100")

        return "\n".join(lines)

    def quick_analysis(self, issue: str, metrics: Dict) -> str:
        """
        Hızlı analiz (context'siz)

        Args:
            issue: Kısa problem açıklaması
            metrics: Metrik dictionary

        Returns:
            AI response
        """
        context = {'metrics': metrics}
        return self.analyze(issue, context=context)

    def driver_coaching(self, lap_data: Dict) -> str:
        """
        Sürücü coaching tavsiyesi

        Args:
            lap_data: Lap telemetry özeti

        Returns:
            Coaching text
        """
        query = "Analyze this lap and provide driver coaching recommendations."
        context = {'lap': lap_data.get('lap_num'), 'metrics': lap_data}
        return self.analyze(query, context=context)

    def sector_analysis(self, sector_num: int, sector_data: Dict) -> str:
        """
        Sektör analizi

        Args:
            sector_num: Sektör numarası
            sector_data: Sektör metrikleri

        Returns:
            Analysis text
        """
        query = f"What is causing poor performance in Sector {sector_num}?"
        context = {'sector': sector_num, 'metrics': sector_data}
        return self.analyze(query, context=context)

    def setup_recommendation(self, telemetry_summary: Dict) -> str:
        """
        Setup önerisi

        Args:
            telemetry_summary: Telemetri özeti

        Returns:
            Setup recommendation
        """
        query = "Based on this telemetry data, what setup changes would you recommend?"
        context = {'metrics': telemetry_summary}
        return self.analyze(query, context=context)

    def clear_history(self) -> None:
        """Conversation history'yi temizle"""
        self.conversation_history = []
        logger.info("Conversation history cleared")


# Örnek kullanım
if __name__ == "__main__":
    # Test (requires API key in environment)
    try:
        engineer = AIRaceEngineer(provider="groq")  # or "openai"

        # Test query
        context = {
            'lap': 12,
            'metrics': {
                'avg_speed': 145.3,
                'max_brake_pressure': 95,
                'throttle_smoothness': 72,
                'tire_stress': 68,
                'time_loss_vs_best': 0.84
            }
        }

        response = engineer.analyze(
            "Why am I losing 0.84 seconds in Turn 7?",
            context=context
        )

        print(f"AI Engineer Response:\n{response}")

    except Exception as e:
        print(f"Test failed: {e}")
        print("Make sure you have API key in environment variables")
