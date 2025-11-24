# GR-Pilot: The AI Debrief Assistant - PRD

## 1. Overview
**GR-Pilot** is an AI-powered post-race analytics assistant for Toyota GR Cup Series. It transforms raw telemetry data into **interactive dashboards + natural language insights**, allowing pilots and engineers to quickly understand performance, anomalies, and opportunities for improvement.

**Dataset:** Circuit of the Americas telemetry including speed, RPM, gear, tire wear, pit stops, and sector times.

---

## 2. Goals & Success Metrics
### Goals
1. Reduce pilot & engineer post-race analysis from hours to seconds.
2. Translate telemetry data into **human-readable actionable insights**.
3. Combine **Generative AI** with motorsport analytics to create a unique, high-impact tool.

### Success Metrics
- AI provides **accurate anomaly detection** and lap comparisons.
- Dashboard UI is **intuitive and clean**.
- Users can query performance via **Natural Language**.
- Tool can generate **summary reports** with strategic recommendations.

---

## 3. User Stories
### Pilot
- Wants to quickly see **where performance dropped** during a race.
- Wants **natural language explanation** of lap differences.
- Queries specific laps/events via chat and receives actionable feedback.

### Engineer
- Wants to identify **strategic decisions**, e.g., pit stop optimization, tire management.
- Wants **visual and textual summaries** for team meetings.
- Seeks predictive suggestions for **future races**.

---

## 4. Features

### 4.1 Anomaly Detection
- Interactive track map highlighting anomalies (red points).
- Detects **speed drops, braking errors, tire degradation, pit stop anomalies**.
- AI generates textual explanations for each anomaly.

### 4.2 Perfect Lap Comparison
- Side-by-side lap comparison (best lap vs pilot lap).
- AI provides **detailed natural language commentary**, including **timing, braking, tire usage, and exit speed differences**.

### 4.3 Natural Language Query
- Chatbox interface for user queries.
- Users can ask questions like:  
> "Why did I slow down on lap 15?"  
- AI returns context-aware responses:  
> "Your tire pressure dropped 10%, braking was excessive in Turn 9."

### 4.4 Suggested Improvements (Strategic Insights)
- AI recommends **strategic adjustments for future races**, e.g.:  
> "Consider early acceleration on Turn 12 to improve tire lifespan and exit speed."

### 4.5 Summary Report
- Auto-generated PDF/HTML reports combining:
  - Track map anomalies
  - AI textual analysis
  - Suggested strategic improvements

---

## 5. Technical Stack
- **Frontend / Dashboard:** Streamlit
- **Data Processing:** Pandas, Numpy
- **Visualization:** Plotly (interactive track map, graphs)
- **AI Layer:** Gemini API / OpenAI API
- **Data Storage:** JSON-formatted telemetry summaries
- **Optional Enhancements:** Docker container, RAG retrieval for large datasets

---

## 6. UX & Design
- Minimalist, Apple-style clean design
- Track map + anomaly overlays
- Side-by-side lap comparison panel
- Chatbox for queries at bottom-right
- Toyota Racing colors: red, black, white

---

## 7. Roadmap
1. Week 1: Dataset preprocessing + basic dashboard
2. Week 2: AI pipeline for anomaly detection + natural language summaries
3. Week 3: Streamlit UI integration + Perfect Lap comparison + Chatbox
4. Week 4: Suggested improvements + PDF/HTML report generation + testing + demo video

---

## 8. Competitive Advantage
- **Benzersiz:** Telemetry data becomes “talking data”.
- **Trend odaklı:** Generative AI + motorsport.
- **Kolay uygulanabilir:** Backend AI kodu, frontend temiz ve basit.
- **Impact:** Pilot ve mühendisler için **direct decision support**.



---

## 9. Advanced Engineering Modules (The "Winning" Edge)
*(Bu modüller, projeyi standart veri görselleştirmeden profesyonel yarış mühendisliği seviyesine taşır.)*

### 9.1 "Butterfly Effect" Analysis (Exit Speed Propagation)
* **Problem:** Pilotlar genellikle virajın ortasındaki hıza odaklanır, ancak asıl zaman kaybı düzlükte yaşanır.
* **Çözüm:** Algoritma, viraj çıkış hızındaki (Exit Speed) 1 km/s'lik kaybın, takip eden düzlük boyunca kaç metre/saniye kaybına dönüştüğünü hesaplar.
* **AI Output:** "Turn 1 çıkışında 2 km/s yavaşsın. Bu sana virajda 0.1s kaybettirdi ama sonraki düzlükte momentum eksikliğinden **0.4s daha kaybettirdi.** Toplam Ceza: 0.5s."

### 9.2 Tire Stress & Friction Circle Analysis
* **Problem:** GR Cup araçlarında lastik yönetimi kritiktir. Aşırı direksiyon açısı lastiği ısıtır ve öldürür.
* **Mühendislik:** `Lateral G` ve `Steering Angle` verilerinin korelasyonu (Scrubbing effect).
* **Özellik:** Pist haritası üzerinde "Lastik İşkence Bölgeleri" (High Scrub Zones) ısı haritası olarak gösterilir.
* **Metrik:** `Tire_Abuse_Index` = $\int (Steering\_Angle \times Lateral\_G) dt$

### 9.3 The "Frankenstein" Lap (Theoretical Optimal)
* **Konsept:** Veri setindeki tüm turların "Mikro-Sektör" bazında en iyileri birleştirilerek sanal bir tur oluşturulur.
* **Amaç:** Pilota sadece "Geçmişte ne yaptığını" değil, "Mükemmel sürseydi ne yapabileceğini" (Potential Laptime) göstermek.

### 9.4 Spatial Synchronization Engine
* **Teknik Detay:** Veriler zaman (saniye) ekseninde değil, **Mesafe (LapDistance)** ekseninde senkronize edilir.
* **Neden:** Hız farklarından dolayı oluşan zaman kaymalarını (Time Skew) yok eder ve milimetrik karşılaştırma sağlar.