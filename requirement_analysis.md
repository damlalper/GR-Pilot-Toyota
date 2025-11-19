# GR-Pilot Requirement Analysis

## 1. Functional Requirements

| ID  | Requirement | Description |
|-----|------------|-------------|
| FR-01 | Anomaly Detection | System detects speed drops, braking errors, tire degradation, pit stop anomalies and displays them on track map. |
| FR-02 | Perfect Lap Comparison | Side-by-side lap comparison with AI-generated textual differences. |
| FR-03 | Natural Language Query | Chatbox interface to ask performance questions; AI responds with context-aware insights. |
| FR-04 | Suggested Improvements | AI generates strategic recommendations for future races. |
| FR-05 | Summary Report | Auto-generated PDF/HTML report with anomalies, AI commentary, and suggested improvements. |

## 2. Non-Functional Requirements

| ID  | Requirement | Description |
|-----|------------|-------------|
| NFR-01 | Performance | Dashboard must load and render telemetry data within 2 seconds. |
| NFR-02 | Scalability | System must support full race datasets (~1000+ telemetry points per lap). |
| NFR-03 | Usability | UI must be intuitive for pilots and engineers; minimal learning curve. |
| NFR-04 | Reliability | AI responses should be accurate and contextually relevant. |
| NFR-05 | Maintainability | Backend code modular for easy updates and AI model replacement. |

## 3. Data Requirements
- **Dataset:** Circuit of the Americas telemetry  
- **Fields:** Speed, RPM, Gear, Tire Wear, Pit Stops, Sector Times  
- **Preprocessing:**  
  - Normalize lap data  
  - Detect key events (acceleration, braking, tire wear)  
  - Export JSON summaries for AI input

## 4. AI & System Workflow
1. Preprocessed telemetry data → anomaly detection module
2. Generate JSON summary → AI API
3. AI returns natural language insights for:
   - Anomaly explanation
   - Lap comparison
   - Suggested improvements
4. Frontend (Streamlit + Plotly) displays:
   - Track map
   - Lap comparison panel
   - Chatbox responses
   - Summary report export

## 5. Constraints & Assumptions
- **Constraint:** Real-time live racing not required; post-event analysis only.  
- **Assumption:** AI can process JSON summaries and generate human-readable insights quickly.  
- **Constraint:** UI must be clean and professional, focus on UX over flashy visuals.  
- **Assumption:** Dataset is complete and clean; minor preprocessing required.

## 6. Success Metrics
- AI correctly identifies ≥95% key anomalies
- Summary report generated within ≤5 seconds
- Positive feedback from at least 80% of test users (engineers/pilots)
- UI receives high score in Design/UX evaluation by judges
