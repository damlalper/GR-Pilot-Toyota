# 🚀 GR-Pilot Quick Start Guide

## 📦 Installation

### 1. Dependencies
```bash
pip install -r requirements.txt
```

**Required packages:**
- streamlit==1.31.1
- pandas==2.2.0
- numpy==1.26.3
- plotly==5.18.0
- openai==1.12.0 (optional - for AI)
- groq==0.4.2 (optional - for AI)

---

## 🏃 Running the App

### Basic Run:
```bash
streamlit run app_gr_pilot.py
```

Access at: `http://localhost:8501`

---

## 📊 Using the Dashboard

### Step 1: Upload Data
1. Look at **sidebar** (left)
2. Find "📁 Data Upload" section
3. Click "**Upload Race Telemetry**"
4. Select CSV file (e.g., `telemetry.csv`, `lap_times.csv`)
5. Wait for "✅ Feature engineering complete!"

### Step 2: Explore Pages

#### 🏠 Overview
- View hero metrics (Speed, CPI, Anomalies)
- See lap time evolution chart
- Check speed trace
- Review feature summary

#### 📊 Telemetry Analysis
- Select lap from dropdown
- Choose channels to display
- View multi-channel telemetry overlay
- Check anomaly timeline
- Download filtered data

#### 📈 Performance Index (CPI)
- View CPI gauge and score
- See radar chart breakdown
- Analyze CPI trend across laps
- Compare best vs worst lap

#### 🤖 AI Race Engineer
- Configure API key in sidebar
- Choose provider (OpenAI/Groq)
- Click "Activate AI Engineer"
- Ask questions or use quick buttons
- Chat with context-aware AI

---

## 🎯 Example Usage Workflow

### Scenario: Analyze a race session

1. **Upload telemetry.csv**
   ```
   Columns: TimeStamp, Speed, BrakePressure, Throttle,
            SteeringAngle, LapNumber
   ```

2. **Overview Page:**
   - Check overall CPI → "78/100 (B)"
   - See lap time evolution → Best lap: Lap 12
   - Notice speed consistency → 85/100

3. **Telemetry Analysis:**
   - Select "Lap 12" (best lap)
   - Choose channels: Speed, Brake, Throttle
   - View overlay → Identify smooth brake/throttle transition
   - Check anomalies → 2 minor anomalies detected

4. **CPI Dashboard:**
   - View radar chart → Weak area: Brake Efficiency (58/100)
   - See trend → CPI improving from Lap 1 to Lap 12
   - Compare → Best lap (12): 82/100, Worst lap (3): 68/100

5. **AI Engineer:**
   - Ask: "Why is my brake efficiency low?"
   - AI analyzes context → "Brake pressure 95 bar (optimal: 92)"
   - Recommendation → "Move brake point 8m forward"

---

## 🔑 API Key Configuration (Optional)

For AI Race Engineer:

### OpenAI:
1. Get API key from https://platform.openai.com/api-keys
2. Create `.streamlit/secrets.toml`:
   ```toml
   [openai]
   api_key = "sk-your-key-here"
   ```

### Groq:
1. Get API key from https://console.groq.com/keys
2. Add to `.streamlit/secrets.toml`:
   ```toml
   [groq]
   api_key = "gsk_your-key-here"
   ```

---

## 📁 Sample Data Format

### telemetry.csv
```csv
TimeStamp,Speed,BrakePressure,Throttle,SteeringAngle,LapNumber
2024-01-01 10:00:00,150.5,0,75.2,0.0,1
2024-01-01 10:00:01,155.3,0,80.1,2.5,1
2024-01-01 10:00:02,145.8,85.3,0,15.2,1
```

**Required columns:**
- `Speed` (km/h)
- `LapNumber` (integer)

**Optional columns:**
- `BrakePressure` (bar)
- `Throttle` (%)
- `SteeringAngle` (degrees)
- `TimeStamp` (datetime)

---

## 🎨 Feature Engineering

**Auto-generated metrics:**
1. **Brake Efficiency** - Speed reduction / brake pressure
2. **Throttle Smoothness** - Pedal stability (0-100)
3. **Tire Stress** - Combined load factor
4. **G-Force Magnitude** - Lateral + longitudinal
5. **Turn Entry Quality** - Trail braking coordination
6. **Speed Consistency** - Rolling variance

These appear in "Engineered Features" section.

---

## 📊 Understanding CPI

**Composite Performance Index (0-100):**

```
CPI = 0.25×Speed + 0.20×Brake + 0.15×Throttle +
      0.15×Tire + 0.15×Turn + 0.10×Consistency
```

**Grades:**
- A (90-100): Excellent
- B (80-89): Good
- C (70-79): Average
- D (60-69): Below Average
- F (0-59): Poor

---

## 🚨 Troubleshooting

### Problem: "No data loaded"
**Solution:** Upload CSV from sidebar

### Problem: "API key error" (AI Engineer)
**Solution:** Configure `.streamlit/secrets.toml`

### Problem: Charts not showing
**Solution:** Ensure required columns exist (Speed, LapNumber)

### Problem: Feature engineering slow
**Solution:** Normal for large datasets (>50k rows). Wait 5-10 seconds.

---

## 📈 Tips for Best Results

1. **Data Quality:**
   - Clean CSV (no missing values in critical columns)
   - Consistent sampling rate
   - Valid lap numbers

2. **Performance:**
   - Start with smaller datasets (~10 laps)
   - Use "All Laps" view sparingly
   - Clear browser cache if slow

3. **AI Usage:**
   - Provide specific questions
   - Reference lap/sector numbers
   - Use quick questions as templates

4. **Visualization:**
   - Use lap selector to focus analysis
   - Export charts (right-click → Save image)
   - Zoom in on interesting regions

---

## 🏆 Advanced Features

### Custom CPI Weights (Future)
```python
from analysis.cpi_calculator import CompositePerformanceIndex

cpi = CompositePerformanceIndex(custom_weights={
    'speed': 0.3,  # Prioritize speed
    'brake': 0.25,
    'throttle': 0.15,
    'tire': 0.1,
    'turn': 0.1,
    'consistency': 0.1
})
```

### Export Data
- Telemetry page → "📥 Download Data (CSV)"
- Exports filtered telemetry with features

---

## 📚 Documentation

- **README.md** - Full project overview
- **IMPLEMENTATION_STATUS.md** - Development progress
- **GRAFIK_ENTEGRASYONU_TAMAMLANDI.md** - Chart details
- **implementation_plan_lines_70_120.md** - Video plan

---

## 🆘 Support

**Issues?**
- Check `gr_pilot.log` file
- Read error messages in UI
- Verify data format

**Questions?**
- Review example queries (AI Engineer page)
- Check hover tooltips
- Read metric descriptions

---

## 🎉 Enjoy GR-Pilot!

**Happy Racing! 🏎️**

Made with ❤️ for Toyota TRD
