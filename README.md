# 🏎️ GR-Pilot: AI-Powered Race Engineering Platform

<div align="center">

![GR-Pilot Banner](https://img.shields.io/badge/Toyota-GR_Cup_Series-EB0A1E?style=for-the-badge&logo=toyota&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![React](https://img.shields.io/badge/React-18.0-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Three.js](https://img.shields.io/badge/Three.js-3D_Viz-black?style=for-the-badge&logo=three.js&logoColor=white)

**Transform raw telemetry into actionable race intelligence with machine learning**

[Features](#-key-features) • [Architecture](#-architecture) • [ML Pipeline](#-machine-learning-pipeline) • [Installation](#-installation) • [API Reference](#-api-reference)

</div>

---

## 🎯 Overview

**GR-Pilot** is a comprehensive AI-powered race engineering platform designed for the **Toyota GR Cup Series**. It transforms raw telemetry data from the **Circuit of the Americas (COTA)** into actionable insights, helping drivers and engineers optimize performance through advanced analytics, machine learning, and real-time 3D visualization.

Unlike traditional telemetry analysis tools that simply display data, GR-Pilot employs **machine learning models trained on real race data** to detect anomalies, predict lap times, classify driving styles, and provide personalized improvement recommendations.

### 🏆 What Makes GR-Pilot Unique?

| Feature | Traditional Tools | GR-Pilot |
|---------|------------------|----------|
| Data Visualization | Static charts | **Interactive 3D race replay** |
| Anomaly Detection | Manual review | **ML-powered Isolation Forest** |
| Lap Comparison | Side-by-side graphs | **AI-generated insights** |
| Driver Feedback | Generic tips | **Personalized Driver DNA profile** |
| Performance Prediction | None | **XGBoost lap time prediction** |
| Weather Integration | Separate system | **Multi-dataset fusion with grip modeling** |

---

## ✨ Key Features

### 🎮 Immersive 3D Race Visualization
Experience the race like never before with our **Three.js-powered 3D visualization engine**:
- **Real-time car positioning** using dead reckoning from speed and steering telemetry
- **Dynamic camera angles** - follow cam, orbit, and bird's eye view
- **Track recreation** from GPS coordinates with accurate elevation changes
- **Lap replay controls** - play, pause, speed adjustment (1x-20x), and lap selection

### 🧠 Machine Learning Pipeline

#### 1. Anomaly Detection (Isolation Forest)
Our unsupervised ML model identifies unusual driving patterns that humans might miss:
- **Sudden braking events** - detects panic braking vs. planned deceleration
- **Erratic steering corrections** - identifies oversteer/understeer recovery moments
- **Throttle-brake overlap** - flags potential mechanical issues or technique problems
- **Speed anomalies** - catches wheel spin and lock-up events

```python
# Example: Anomaly types detected
{
    "type": "sudden_braking",
    "explanation": "Brake pressure changed by 45.2 units - possible late braking",
    "distance": 1245.6,
    "severity": "high"
}
```

#### 2. Lap Time Prediction (XGBoost)
Predict lap times from driving style features:
- Trained on **50+ engineered features** from telemetry
- Provides **feature importance** to understand what affects lap time most
- Generates **personalized improvement suggestions** based on your weaknesses

#### 3. Driver DNA Clustering (K-Means)
Classify driving styles into distinct profiles:
- **Aggressive Attacker** - Late braking, high throttle aggression
- **Smooth Operator** - Consistent inputs, tire preservation focus
- **Balanced Racer** - Adaptable, good all-around technique
- **Conservative Driver** - Safe approach with room for improvement

### 📊 Advanced Analytics Dashboard

#### Real-Time Telemetry Panel
- **Speed** - Current, max, average with trend indicators
- **RPM** - Engine utilization with optimal range highlighting
- **Throttle** - Application percentage with aggression scoring
- **Brake Pressure** - Front/rear distribution analysis
- **Steering Angle** - Input smoothness evaluation
- **Gear** - Shift point optimization suggestions

#### Interactive Charts (Recharts)
- Speed vs Distance traces with comparison overlay
- Throttle/Brake application timing analysis
- RPM utilization histograms
- Sector time breakdowns

#### Track Map Visualization
- 2D SVG track representation
- Real-time car position indicator
- Color-coded speed zones
- Anomaly location markers

### 🌤️ Weather & Grip Fusion

GR-Pilot integrates **real weather data** with telemetry to calculate a **dynamic Grip Index**:

```
Grip Index = f(Track Temp, Humidity, Tire Wear, Driving Intensity)
```

- **Track Temperature Impact** - Optimal grip around 30-45°C
- **Humidity Factor** - Lower humidity = better grip
- **Tire Degradation Model** - Cumulative stress calculation per tire
- **Critical Zone Identification** - Warns when grip margin is low

### 🗣️ AI Race Engineer Assistant

Natural language interface powered by **Groq LLaMA 3.3 70B**:

> "Where am I losing time compared to my best lap?"

The AI analyzes your telemetry and responds with specific, actionable insights:

> "You're losing 0.8 seconds in Turn 11 exit. Your throttle application is 15% lower than your best lap at this point. The data shows you're lifting earlier - try maintaining throttle through the apex and applying full throttle 10 meters earlier."

### 📋 Comprehensive Reporting

Generate professional race reports with:
- **Lap Statistics** - All key metrics summarized
- **Anomaly Summary** - Critical moments highlighted
- **AI Engineer Summary** - Natural language performance review
- **Improvement Priorities** - Ranked action items
- **Export Options** - HTML (styled) and JSON formats

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (React 18)                       │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐ │
│  │  3D View │  │ Telemetry│  │  Charts  │  │   AI Chatbot     │ │
│  │ Three.js │  │  Panel   │  │ Recharts │  │   Interface      │ │
│  └──────────┘  └──────────┘  └──────────┘  └──────────────────┘ │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐ │
│  │ Driver   │  │   Grip   │  │  Sector  │  │  Risk Heatmap    │ │
│  │   DNA    │  │  Index   │  │ Analysis │  │  Visualization   │ │
│  └──────────┘  └──────────┘  └──────────┘  └──────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │ REST API
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      BACKEND (FastAPI)                           │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                    API Endpoints                             ││
│  │  /api/lap/{n}  /api/anomalies  /api/driver_dna  /api/chat   ││
│  └─────────────────────────────────────────────────────────────┘│
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                  ML Pipeline                                 ││
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐││
│  │  │  Isolation  │ │   XGBoost   │ │   K-Means Clustering    │││
│  │  │   Forest    │ │  Regressor  │ │   (Driver Styles)       │││
│  │  │ (Anomalies) │ │ (Lap Time)  │ │                         │││
│  │  └─────────────┘ └─────────────┘ └─────────────────────────┘││
│  └─────────────────────────────────────────────────────────────┘│
│  ┌─────────────────────────────────────────────────────────────┐│
│  │              Feature Engineering Pipeline                    ││
│  │  Rolling Stats │ Derivatives │ Zone Aggregation │ Braking   ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DATA LAYER                                  │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────────┐ │
│  │  Telemetry   │  │   Weather    │  │   Sector Timing        │ │
│  │  (50Hz CAN)  │  │   Conditions │  │   (Official Results)   │ │
│  └──────────────┘  └──────────────┘  └────────────────────────┘ │
│                    COTA Race 2 Dataset                          │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🤖 Machine Learning Pipeline

### Feature Engineering

We extract **50+ features** from raw telemetry to feed our ML models:

```
backend/ml/
├── __init__.py
├── feature_engineering.py    # 50+ feature extraction
├── anomaly_model.py          # Isolation Forest
├── lap_predictor.py          # XGBoost regression
├── driver_clustering.py      # K-Means clustering
└── train_models.py           # Model training script
```

#### Rolling Statistics (Window Sizes: 5, 10, 20)
```python
- {metric}_rolling_mean_{window}
- {metric}_rolling_std_{window}
- {metric}_rolling_min_{window}
- {metric}_rolling_max_{window}
```

#### Derivative Features
```python
- {metric}_rate          # First derivative (rate of change)
- {metric}_acceleration  # Second derivative (jerk)
```

#### Specialized Features
```python
# Braking Analysis
- is_braking, brake_intensity, brake_buildup_rate
- trail_braking (brake + steering combination)
- braking_event_count

# Throttle Analysis
- is_full_throttle, is_partial_throttle, is_lift_off
- throttle_rate, throttle_aggression

# Cornering Analysis
- is_cornering, corner_direction
- estimated_lateral_g, steering_rate, steering_smoothness
- at_corner_entry, at_corner_exit

# Zone-Based Aggregations (Track divided into 10 zones)
- speed_zone_mean, speed_zone_std, speed_zone_max
- throttle_zone_mean, brake_zone_mean
```

### Model Training

```bash
# Train all models on COTA Race 2 data
cd backend
python -m ml.train_models
```

**Output:**
```
Loading telemetry from R2_cota_telemetry_data.csv...
Loaded 500000 rows
Found 15 laps

[1/3] Training Anomaly Detector (Isolation Forest)...
✓ Anomaly detector saved (contamination=3%)

[2/3] Training Lap Time Predictor (XGBoost)...
✓ Lap predictor saved (MAE=1.24s, R2=0.89)

[3/3] Training Driver Style Clusterer (K-Means)...
✓ Driver clusterer saved (5 clusters identified)

Models saved in: backend/ml/trained_models/
```

### Model Persistence

Trained models are serialized using pickle and automatically loaded on API startup:

```
ml/trained_models/
├── anomaly_detector.pkl    # Isolation Forest + StandardScaler
├── lap_predictor.pkl       # XGBoost + feature importance
└── driver_clusterer.pkl    # K-Means + PCA + cluster profiles
```

---

## 📦 Installation

### Prerequisites

- Python 3.10+
- Node.js 18+
- npm or yarn

### Backend Setup

```bash
# Clone the repository
git clone https://github.com/your-org/gr-pilot.git
cd gr-pilot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
cd backend
pip install -r requirements.txt

# Set environment variables
export GROQ_API_KEY="your-groq-api-key"  # For AI assistant
# On Windows: set GROQ_API_KEY=your-groq-api-key

# Train ML models (first time only)
python -m ml.train_models

# Start the API server
python main.py
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### Access the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

---

## 📡 API Reference

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/laps` | GET | List all available laps |
| `/api/lap/{lap}` | GET | Get telemetry for specific lap |
| `/api/track` | GET | Get track outline coordinates |
| `/api/weather` | GET | Get weather conditions |

### ML-Powered Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/driver_dna/{lap}` | GET | Get ML-classified driving style profile |
| `/api/anomalies/{lap}` | GET | Detect anomalies using Isolation Forest |
| `/api/predict_laptime/{lap}` | GET | Predict lap time with XGBoost |
| `/api/ml_status` | GET | Check status of loaded ML models |

### Analysis Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/grip_index/{lap}` | GET | Calculate grip index (weather + telemetry fusion) |
| `/api/sectors/{lap}` | GET | Get sector times with official timing data |
| `/api/risk_heatmap/{lap}` | GET | Calculate spin/lock-up risk zones |
| `/api/tire_stress/{lap}` | GET | Estimate tire wear per corner |
| `/api/compare/{lap1}/{lap2}` | GET | Compare two laps side by side |
| `/api/suggestions/{lap}` | GET | Get AI improvement suggestions |
| `/api/report/{lap}` | GET | Generate comprehensive lap report |

### AI Assistant

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/chat` | POST | Query the AI race engineer |

**Request Body:**
```json
{
    "message": "Why was my sector 2 slower than the best lap?",
    "lap": 5
}
```

**Response:**
```json
{
    "response": "In Sector 2, you lost 0.6 seconds primarily due to...",
    "plot_type": "speed"
}
```

---

## 📊 Data Sources

GR-Pilot is built on **real race data** from the Toyota GR Cup Series at Circuit of the Americas:

| Dataset | Description | Size |
|---------|-------------|------|
| `R2_cota_telemetry_data.csv` | 50Hz CAN bus telemetry | ~2GB |
| `26_Weather_Race 2.CSV` | Track & ambient conditions | 1MB |
| `23_AnalysisEnduranceWithSections.CSV` | Official sector times | 5MB |
| `COTA_lap_time_R2.csv` | Lap timing data | 500KB |

### Telemetry Channels

| Channel | Description | Unit |
|---------|-------------|------|
| `speed` | Vehicle speed | km/h |
| `nmot` | Engine RPM | rpm |
| `ath` | Throttle position | % |
| `pbrake_f` | Front brake pressure | bar |
| `pbrake_r` | Rear brake pressure | bar |
| `Steering_Angle` | Steering wheel angle | degrees |
| `gear` | Current gear | 1-6 |
| `accx_can` | Longitudinal acceleration | g |
| `accy_can` | Lateral acceleration | g |

---

## 🛠️ Technology Stack

### Frontend
- **React 18** - UI framework with hooks
- **TypeScript** - Type-safe development
- **Three.js / React Three Fiber / Drei** - 3D visualization
- **Recharts** - Interactive charting
- **Tailwind CSS** - Utility-first styling
- **Zustand** - State management
- **Axios** - HTTP client
- **Lucide React** - Icon library

### Backend
- **FastAPI** - High-performance async API
- **Pandas / NumPy** - Data processing
- **Scikit-learn** - ML algorithms (Isolation Forest, K-Means, StandardScaler)
- **XGBoost** - Gradient boosting for regression
- **Groq API** - LLaMA 3.3 70B for AI assistant
- **Uvicorn** - ASGI server

### ML Pipeline
- **Feature Engineering** - 50+ custom features from raw telemetry
- **Isolation Forest** - Unsupervised anomaly detection
- **XGBoost Regressor** - Lap time prediction with feature importance
- **K-Means Clustering** - Driver style classification into 5 profiles
- **StandardScaler** - Feature normalization
- **PCA** - Dimensionality reduction for visualization

---

## 🎛️ View Modes

### 1. Race View
- 3D race visualization with real-time car position
- Live telemetry gauges
- Track map with speed-colored racing line
- Weather panel

### 2. Analysis View
- Driver DNA profile
- Grip Index visualization
- Sector analysis with time deltas
- Anomaly detection results
- Risk heatmap
- Tire stress monitoring
- Improvement suggestions
- Report export

### 3. Compare View
- Side-by-side lap comparison
- Speed delta graphs
- Cumulative time delta
- 3D visualization overlay

---

## 🚀 Future Roadmap

- [ ] **Real-time streaming** - Live telemetry during sessions
- [ ] **Multi-driver comparison** - Compare across different drivers
- [ ] **Predictive tire strategy** - ML-based pit stop optimization
- [ ] **Voice interaction** - Speech-to-text AI queries
- [ ] **Mobile companion app** - Quick insights on the go
- [ ] **Historical trend analysis** - Season-long performance tracking

---

---

## 🔧 Engineering Methodology: Behind the Code

GR-Pilot is not just visualizing data; it's engineering logic. We applied professional motorsport principles to ensure our insights are physically accurate and strategically valuable.

### 1. Spatial vs. Temporal Synchronization
Traditional tools compare laps by **Time**, causing data misalignment when one car is faster.
* **Our Solution:** We implemented **Spatial Indexing** using `Laptrigger_lapdist_dls` (Distance).
* **Impact:** This ensures that when we compare Turn 1 braking points, we are comparing the exact same meter of asphalt, regardless of approach speed.

### 2. The "Penalty Propagation" Algorithm
We don't just look at corner speed; we analyze **momentum loss**.
* **Logic:** A mistake in Corner Entry creates a deficit that propagates down the entire following straight.
* **Implementation:** Our physics engine calculates the integral of velocity difference over distance ($\Delta v \cdot d$) to show the *true* cost of a mistake, not just the instantaneous delta.

### 3. Tire Load & Grip Budgeting (G-G Diagram)
Understanding the Toyota GR86's limit requires analyzing the Friction Circle.
* **Logic:** We fuse `accx` (Longitudinal) and `accy` (Lateral) G-forces to calculate total tire load.
* **Detection:** If `Steering_Angle` is high but `Lateral_G` is plateauing, our ML model flags this as **"Understeer/Scrubbing"**—a critical tire-killing behavior in endurance racing.

### 4. Why Race 2 Data? (Strategic Selection)
We specifically trained our models on **COTA Race 2** data.
* **Rubber Evolution:** Race 2 represents a "rubbered-in" track with higher grip levels, providing a more accurate "Ultimate Benchmark" for physics limits.
* **Driver Adaptation:** By Race 2, drivers are pushing limits rather than learning the track, making anomalies "true errors" rather than "learning noise."

---

## 📁 Project Structure

```
GR-Pilot-Toyota/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── requirements.txt        # Python dependencies
│   └── ml/
│       ├── __init__.py
│       ├── feature_engineering.py
│       ├── anomaly_model.py
│       ├── lap_predictor.py
│       ├── driver_clustering.py
│       ├── train_models.py
│       └── trained_models/     # Serialized ML models
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Scene3D.tsx
│   │   │   ├── RacingCar.tsx
│   │   │   ├── TelemetryPanel.tsx
│   │   │   ├── TelemetryCharts.tsx
│   │   │   ├── TrackMap.tsx
│   │   │   ├── ChatBot.tsx
│   │   │   ├── DriverDNA.tsx
│   │   │   ├── GripIndex.tsx
│   │   │   ├── SectorAnalysis.tsx
│   │   │   ├── RiskHeatmap.tsx
│   │   │   ├── TireStress.tsx
│   │   │   └── ...
│   │   ├── store/
│   │   │   └── useStore.ts     # Zustand state
│   │   ├── api/
│   │   │   └── index.ts        # API client
│   │   └── App.tsx             # Main application
│   └── package.json
├── src/                        # Legacy Python modules
│   ├── data_loader.py
│   ├── analytics.py
│   ├── dead_reckoning.py
│   └── ai_assistant.py
└── README.md
```

---

## 👥 Team

Built with ❤️ for the **Hack the Track presented by Toyota GR 2025** Hackathon

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**GR-Pilot** - *Where Data Meets the Racing Line*

![Toyota GR](https://img.shields.io/badge/Powered_by-Toyota_GR_Cup_Data-EB0A1E?style=flat-square)
![Made with AI](https://img.shields.io/badge/Enhanced_with-Machine_Learning-00A67E?style=flat-square)

**🏁 Unleash the Data. Engineer Victory. 🏁**
> **Developer Note:** > "In motorsport, data is the voice of the car. We built GR-Pilot not to replace the engineer, but to give them a megaphone." 
> *Developed with passion for the Toyota Gazoo Racing philosophy.*
</div>
