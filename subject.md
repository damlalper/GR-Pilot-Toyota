# GR-Pilot: The AI Debrief Assistant (Geliştirilmiş ve UI Odaklı)

🏎️ **Overview**  
GR-Pilot, Circuit of the Americas (COTA) telemetri verilerini kullanarak pilot ve mühendisler için **AI destekli post-race analiz** sunar. Sistem, veriyi **interaktif görselleştirmeler + doğal dil tavsiyeler** ile birleştirerek yarış sonrası kararları hızlandırır.  

---

🎯 **Project Goals**  

- Yarış sonrası analiz süresini **saatlerden saniyelere** indirmek.  
- Karmaşık veriyi **insan dostu, aksiyon alınabilir içgörüler** hâline getirmek.  
- **Generative AI + motorsport telemetri verisi** ile benzersiz bir analiz deneyimi sunmak.  
- UI/UX tasarımıyla kullanıcı deneyimini **öncelikli** hale getirmek.  

---

⚙️ **Core Features (UI ve Görsellik Odaklı)**

### 1. Anomaly Detection (Anomali Tespiti)  
- **UI:** Interaktif pist haritası, kırmızı noktalarla anomali gösterimi. Hover ile detaylı bilgi popup’ı.  
- **AI:** Hız düşüşleri, gereksiz frenleme, lastik aşınması, pit stop hataları gibi stratejik verileri tespit eder.  
- **Extra:** Pit stop ve lastik aşınması bilgisi grafik üzerinde görselleştirilir.  
- **Jüri Katkısı:** Dataset etkili kullanımı ve veri görselleştirme kriterlerini güçlendirir.  

### 2. Perfect Lap Comparison (Mükemmel Tur Karşılaştırması)  
- **UI:** Sol panel: en iyi tur, sağ panel: pilotun turu, **side-by-side** interaktif grafik.  
- **AI:** Farklar doğal dil ile açıklanır:  
  > “Turn 7’de rakibinden 0.4s geç kaldın, çıkış hızın düşmüş. Tire aşınması %5 artmış.”  
- **Extra:** Lastik aşınması ve fren basıncı farkları da metin ve görsel olarak sunulur.  
- **Jüri Katkısı:** Tasarım ve UX, frontend/backend dengesi kriterlerini güçlendirir.  

### 3. Natural Language Query (Doğal Dil Sorgu)  
- **UI:** Chat widget alt köşede, gerçek zamanlı sohbet deneyimi.  
- **AI:** Kullanıcı sorularını anlar ve pilot + mühendis perspektifinde yanıtlar üretir:  
  > “Neden 15. turda yavaşladım?”  
  Yanıt:  
  > “Lastik basıncın %10 düştü, Turn 9’da frenleme fazlaydı. Pit stop stratejisi önerisi: 12. turda pite gir.”  
- **Extra:** Yanıtlar **jargon + basit dil** dengesiyle sunulur.  
- **Jüri Katkısı:** Datasetin benzersiz uygulaması ve AI etkileşimi ile yüksek not alır.  

### 4. Suggested Improvements (Stratejik Öneriler)  
- AI, gelecekteki yarışlar için **aksiyon alınabilir tavsiyeler** sunar:  
  > “Turn 12’de biraz erken çık, lastiğin daha uzun ömürlü olur ve çıkış hızın artar.”  
- **Jüri Katkısı:** Potansiyel etki ve topluluk faydası kriterlerini güçlendirir.  

### 5. Summary Report (Özet Rapor)  
- PDF/HTML rapor: anomali noktaları, AI yorumları, pit stop ve strateji önerileri.  
- **Extra:** Görseller, tablolar ve renk kodlamalarıyla okunabilirliği artırır.  

---

🛠️ **Tech Stack**

- **Frontend / Dashboard:** Streamlit, Plotly (interactive), D3.js (ek görselleştirme)  
- **Backend / Data Processing:** Pandas, Numpy, JSON verisi  
- **AI Layer:** OpenAI API veya Gemini API  
- **Design:** Toyota Racing renk paleti (kırmızı, siyah, beyaz), minimal UI  

---

📊 **Data Application (TRD Dataset Kullanımı)**

- **Dataset:** Telemetri, lastik aşınması, frenleme, pit stop, tur zamanı  
- **Preprocessing:**  
  - Tur normalizasyonu  
  - Hız, fren, lastik aşınması ve pit stop verilerinden **anomaly ve fark tespiti**  
  - AI inputu için JSON formatına çevirme  
- **Jüri Katkısı:** Datasetler etkili ve kategorilere uygun şekilde uygulanıyor; benzersiz görselleştirme ile öne çıkıyor.  

---

🎨 **Design & UI Concept**

- **Minimalist ve modern:** Clean, Apple vari tasarım  
- **Track map:** Anomali noktaları + hover ile detaylar  
- **Lap comparison:** Side-by-side interaktif grafik  
- **Chat widget:** Alt köşede kolay erişim  
- **Color palette:** Toyota Racing – kırmızı, siyah, beyaz  
- **Jüri Katkısı:** UX/UI ve frontend/backend dengesi yüksek, deneyimi zenginleştiriyor.  

---

🛣️ **Roadmap**

| Hafta | Görevler |
|-------|----------|
| Week 1 | Veri ön işleme, temel dashboard, grafikler |
| Week 2 | AI pipeline, anomaly detection, NLP summary |
| Week 3 | Streamlit UI, Perfect Lap, Chatbox |
| Week 4 | Suggested improvements, test, demo video |

---

💡 **Jüri Kriterleri Karşılamaları**

1. **Application of the TRD Datasets:**  
   - Telemetri + pit stop + lastik verileri aktif olarak kullanılıyor, benzersiz görselleştirme ile sunuluyor.  

2. **Design:**  
   - Minimalist UI, interaktif grafikler, chatbox ve dashboard entegrasyonu. Frontend & backend dengesi yüksek.  

3. **Potential Impact:**  
   - Toyota Racing topluluğu için hızlı ve anlaşılır veri analizi sağlar.  
   - Motorsport topluluğu ve veri bilimi alanında geniş potansiyel fayda.  

4. **Quality of the Idea:**  
   - Yaratıcı ve özgün AI tabanlı post-race analiz.  
   - Mevcut çözümlerden **daha hızlı, görselliği yüksek ve kullanıcı dostu**.  
