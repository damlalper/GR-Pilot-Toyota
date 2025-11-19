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

## 🧠 Data Architecture & Implementation Strategy (RACE 2 KULLANILACAK)

#### 📉 Dataset Selection Rationale: Why COTA Race 2?

Projede veri kaynağı olarak özellikle **Race 2 (2. Yarış)** verilerinin seçilmesi, analitik modelin doğruluğunu artırmaya yönelik stratejik bir karardır.

##### 1. Higher Performance Ceiling (Daha Yüksek Performans Limiti)
* **Track Evolution (Pist Evrimi):** Yarış hafta sonu ilerledikçe pist yüzeyi araç lastikleriyle kaplanır ("rubbering in"). Bu durum tutuşu (grip) artırır. Race 2 verileri, fiziksel olarak daha elverişli zemin koşullarını temsil eder.
* **The Ultimate Benchmark:** Zemin daha hızlı olduğu için, Race 2'den elde edilen "Mükemmel Tur" (Perfect Lap), ulaşılması gereken gerçek fiziksel limiti temsil eder. AI modelimiz için en keskin referans noktası budur.

##### 2. Driver Adaptation & Aggression (Adaptasyon ve Agresiflik)
* **No Learning Curve:** Race 1 genellikle pilotların pisti tanıdığı ve temkinli olduğu bir süreçtir. Race 2'de ise pilotlar adaptasyon sürecini tamamlamış ve limitleri zorlamaktadır.
* **Meaningful Errors (Anlamlı Hatalar):** Race 1'deki hatalar genellikle "pisti öğrenme" kaynaklıdır. Race 2'deki hatalar ise "limiti zorlama" kaynaklıdır. AI asistanımızın analiz etmesi gereken asıl değerli senaryolar, bu rekabetçi limit aşımı anlarıdır.

##### 3. Data Consistency (Veri Tutarlılığı)
* Race 2 verilerinde sürüş çizgileri (Racing Lines) daha oturmuş ve stabildir. Bu tutarlılık, **Anomali Tespiti** algoritmamızın "gürültü" (noise) yerine gerçek sürüş hatalarını çok daha yüksek doğrulukla tespit etmesini sağlar.



Projenin temelini oluşturan veri mimarisi, **Toyota Racing Development (TRD)** tarafından sağlanan ham verilerin işlenerek anlamlı içgörülere dönüştürülmesi üzerine kuruludur. 3 farklı veri seti senkronize bir şekilde çalıştırılmaktadır.


### 1. The Backbone: Telemetry Data
**Dosya:** `R2_cota_telemetry_data.csv` (Circuit of the Americas - Race 2)
Projenin analitik motorunu besleyen ana veri kaynağıdır. Tüm grafikler, anomali tespiti ve harita görselleştirmeleri bu veriden çekilir.

* **Senkronizasyon Mantığı (Kritik):**
  * **X-Ekseni:** `Laptrigger_lapdist_dls` (Pist Mesafesi) kullanılır.
  * **Neden?** Zaman (`Time`) değişkeni pilotlar arasında kayma yaratır. Veriler, pist üzerindeki fiziksel konuma (metre) göre hizalanarak (`Spatial Synchronization`) %100 doğru karşılaştırma sağlanır.

* **Kullanılan Parametreler:**
  * **Performans:** `Speed` (Hız Deltası hesaplaması için).
  * **Sürücü Davranışı:**
    * `aps` (Gaz Pedalı %): Çekimser gaz kullanımı tespiti.
    * `pbrake_f` (Ön Fren Basıncı): Erken veya gereksiz sert frenleme tespiti.
    * `Steering_Angle` (Direksiyon): Viraj içi gereksiz düzeltmeler ve oversteer analizi.
  * **Görselleştirme:** `VBOX_Lat_Min` & `VBOX_Long_Minutes` (Streamlit harita katmanı için koordinatlar).

### 2. The Benchmark: Perfect Lap Identification
**Dosya:** `COTA_lap_time_R2.csv`
Binlerce tur arasından referans alınacak "Mükemmel Tur"u (Ghost Car) belirlemek için kullanılır.

* **Algoritma:**
  1. Veri seti `lap_time` değerine göre (ASC) sıralanır.
  2. En düşük zamanlı turun `Lap Number` (Tur No) değeri çekilir (Örn: Tur 14).
  3. Ana telemetri dosyasından sadece bu tura ait veriler filtrelenerek **"Reference Dataset"** oluşturulur.
  4. Kullanıcının seçtiği tur, bu referans veri seti ile üst üste bindirilir (Overlay).

### 3. Context Layer: Environmental Factors
**Dosya:** `26_Weather_Race 2_Anonymized.csv`
Yapay zekanın (LLM) sadece veriyi okumasını değil, bir mühendis gibi bağlam kurmasını sağlar.

* **Kullanım:** `track_temp` (Pist Sıcaklığı) ve `ambient_temp` verileri alınır.
* **Prompt Engineering:**
  > *"Pist sıcaklığı 50°C. Pilotun 7. virajdaki lastik basıncı artışı performans kaybına yol açmış olabilir mi?"*
  Bu bağlam sayesinde AI, "Lastikleriniz aşırı ısınmış, daha yumuşak fren yapın" gibi profesyonel tavsiyeler üretir.

---

## ⚙️ Feature Logic & Data Pipeline

Verilerin özelliklere (Features) dönüşme mantığı aşağıdaki gibidir:

### A. Anomaly Detection Engine
Kullanıcının pist üzerinde nerede en çok zaman kaybettiğini otomatik tespit eder.
* **Mantık:** `(Perfect_Speed - User_Speed) > 15 km/h` VE `Mesafe == Eşit` ise -> **ANOMALY**.
* **Çıktı:** Harita üzerinde ilgili Latitude/Longitude koordinatına kırmızı nokta (Scatter Plot) eklenir.
* **UI:** Hover yapıldığında *"Hız Kaybı: -15km/h. Olası Sebep: Erken Fren"* bilgisi gösterilir.

### B. "Perfect Lap" Visualization
Sürücüye nerede hata yaptığını görsel olarak anlatır.
* **Teknoloji:** Plotly & Streamlit
* **Görsel:** Sol panelde `aps` (Gaz), Sağ panelde `Speed` grafikleri.
* **Fark Gösterimi:** Mükemmel tur ile kullanıcı turu arasındaki alan `fill='tonexty'` ile kırmızıya boyanarak performans kaybı (Delta) vurgulanır.

### C. AI Race Engineer (NLP/Chatbot)
Veriyi doğal dile çeviren RAG-lite yapısı.
1. **Sorgu:** Kullanıcı "Nerede hata yaptım?" der.
2. **Python Backend:** Veriyi tarar, en büyük farkın (Delta) olduğu 3 virajı tespit eder.
3. **JSON Dönüşümü:**
   ```json
   {
     "Turn": 7,
     "Speed_Delta": "-20 km/h",
     "Brake_Pressure_Diff": "+15 bar",
     "Track_Temp": "45C"
   }

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
