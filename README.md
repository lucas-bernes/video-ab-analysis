# A/B Creative Analytics Prototype for Video Ads

## 🎯 Business Problem

Marketing teams run A/B tests on video ad creatives to optimize campaigns, but they lack a centralized way to:
- Compare variant performance across multiple KPIs
- Understand *why* one creative outperforms another
- Extract structured insights from experiment data
- Make data-driven decisions on creative direction

## 🚀 MVP Goal

Build a lightweight prototype that:
1. **Ingests** A/B experiment data via API (metadata + performance metrics)
2. **Normalizes** nested payloads into clean domain models
3. **Compares** Variant A vs B on configurable KPIs (CTR, ROAS, conversion rate, etc.)
4. **Generates** rule-based business insights with confidence scoring
5. **Visualizes** results in an interactive Streamlit dashboard

**Result:** Marketing teams can quickly understand which video creative won, by how much, and why—all without processing raw video files.

---

## 🏗️ Architecture Overview

```
API Data (JSON)
     ↓
┌────────────────────────────────────────────────────────────┐
│  NORMALIZATION LAYER (normalizer.py)                       │
│  • Parse nested API responses                              │
│  • Validate with Pydantic models                           │
│  • Flatten to pandas DataFrames                            │
└────────────────────────────────────────────────────────────┘
     ↓
┌────────────────────────────────────────────────────────────┐
│  COMPARISON ENGINE (comparator.py)                         │
│  • Group by experiment_id                                  │
│  • Compare A vs B on primary KPI                           │
│  • Compute metric deltas & lifts                           │
│  • Detect metadata differences                             │
└────────────────────────────────────────────────────────────┘
     ↓
┌────────────────────────────────────────────────────────────┐
│  INSIGHT GENERATOR (insight_generator.py)                  │
│  • Rule-based analysis                                     │
│  • Hypothesis-driven narratives                            │
│  • Confidence scoring                                      │
└────────────────────────────────────────────────────────────┘
     ↓
┌────────────────────────────────────────────────────────────┐
│  STREAMLIT DASHBOARD (main.py)                             │
│  • Interactive exploration                                 │
│  • Comparison results visualization                        │
│  • Generated insights display                              │
└────────────────────────────────────────────────────────────┘
```

**Data Layers:**
- **API Models** (`api_models.py`): Strict Pydantic validation of API responses
- **Domain Models** (`domain_models.py`): Normalized business objects with computed properties

---

## 📁 Project Structure

```
Marketing Video AB Analysis/
├── README.md                          # This file
├── requirements.txt                   # Python dependencies
├── app/
│   ├── config.py                      # Constants & thresholds
│   ├── main.py                        # Streamlit app entry point
│   ├── models/
│   │   ├── api_models.py              # Pydantic models for API response structure
│   │   └── domain_models.py           # Normalized business models
│   ├── services/
│   │   ├── normalizer.py              # JSON → domain objects + DataFrames
│   │   ├── comparator.py              # A vs B comparison engine
│   │   └── insight_generator.py       # Rule-based insight generation
│   ├── data/
│   │   └── sample_api_response.json   # 3 sample A/B experiments
│   └── utils/
└── tests/
```

---

## 🏃 How to Run Locally

### Prerequisites
- Python 3.9+
- pip or conda

### Installation

```bash
# Clone/navigate to project
cd "Marketing Video AB Analysis"

# Install dependencies
pip install -r requirements.txt
```

### Run the Dashboard

```bash
streamlit run app/main.py
```

The app opens at `http://localhost:8501`

### Interactive Demo

1. Click **"🔄 Load Sample Data"** in the left sidebar
2. Explore **Normalized Data** section (expandable tables)
3. View **A/B Comparison Results** (winner badges, metric deltas)
4. Read **Generated Insights** (business narratives)
5. Try changing **Primary KPI** selector in sidebar

---

## 📊 Sample Output

**Input:** 3 A/B experiments (Facebook, Instagram, YouTube)

**Example Comparison:**
```
Experiment: exp_001 (Q2 2026 SaaS Product Launch)
Winner: Variant B
Primary KPI (CTR): +12.5% lift
  Variant A: 4.8%
  Variant B: 5.4%
  
Secondary Metrics:
  Conversions: +28.6%
  ROAS: +26.0%
  Cost per Click: -2.1%
```

**Example Insight:**
```
Variant B outperformed Variant A with a 12.5% higher CTR. 
Conversion rate also improved significantly, suggesting better downstream engagement. 
The winning variant's shorter duration (15s vs 30s) may have contributed to 
faster value communication. These results are compelling—consider scaling Variant B.

Confidence: HIGH
```

---

## 🎯 Current MVP Scope

### ✅ In Scope
- **Metadata-based analysis** (no raw video processing)
- **API-driven data** (experiment metadata + performance metrics)
- **Normalization pipeline** (nested JSON → domain models → DataFrames)
- **Multi-KPI comparison** (CTR, ROAS, conversion rate, cost metrics, etc.)
- **Rule-based insights** (hypothesis-driven, not causal claims)
- **Interactive dashboard** (Streamlit UI for exploration)
- **Sample data** (3 realistic A/B experiments)

### ❌ Out of Scope (Future Work)
- Raw video file processing
- Computer vision / frame analysis
- Audio analysis or transcription
- Real-time API integration
- Statistical significance testing (t-tests, Bayesian methods)
- User authentication
- Persistent database storage

---

## 🔮 Future Improvements

**Phase 2: Real Data**
- Connect to actual API endpoints (Meta, Google, TikTok ads APIs)
- Real-time experiment tracking
- Historical data archival

**Phase 3: Advanced Analysis**
- Statistical significance testing
- Multivariate test support (A/B/C/n)
- Sequential testing rules (early stopping)
- Segment-level analysis (by audience, geography, device)

**Phase 4: Media Intelligence**
- Computer vision feature extraction (color, text, scene detection)
- OCR for headline/CTA analysis
- Duration sentiment analysis
- Creative recommendation engine

**Phase 5: Productization**
- User authentication & workspaces
- Export reports (PDF, CSV, Slack)
- Scheduled alerts & notifications
- A/B testing calculator (sample size, power)

---

## 💡 Design Principles

1. **Separation of Concerns**
   - API layer, domain layer, service layer, UI layer
   - Each module has a single responsibility

2. **Type Safety**
   - Pydantic validation on all external data
   - Full type hints for IDE support

3. **Interpretability**
   - Code is clear and readable
   - Easy to explain design decisions in interviews
   - Business logic is understandable, not hidden in complex statistics

4. **Extensibility**
   - Adding new KPIs: just update `config.py`
   - Modifying insight rules: edit `insight_generator.py`
   - New metadata fields: extend Pydantic models

---

## 🧪 Example Usage

```python
# 1. Load and normalize data
from app.services import normalize_from_file
data = normalize_from_file("app/data/sample_api_response.json")

# 2. Run comparisons
from app.services import compare_experiments
comparisons = compare_experiments(data, primary_kpi="ctr")

# 3. Generate insights
from app.services import generate_insight
for comparison in comparisons:
    insight = generate_insight(comparison)
    print(insight.headline)
    print(insight.summary)
    print(f"Confidence: {insight.confidence}")
```

---

## 📚 Key Technologies

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Data Validation** | Pydantic | Type-safe API response parsing |
| **Data Analysis** | Pandas | DataFrames for comparison logic |
| **Dashboard** | Streamlit | Interactive web UI |
| **Configuration** | Python modules | Centralized settings & constants |

---

## 🎓 Interview Highlights

✅ **Modular, professional architecture** — Clear layering and separation of concerns  
✅ **Type-safe design** — Pydantic validation prevents data bugs  
✅ **Business-focused insights** — Hypotheses over causal claims  
✅ **Interactive dashboard** — Polished UI demonstrates product thinking  
✅ **Extensible framework** — Easy to add new KPIs and analysis rules  
✅ **Well-documented code** — Clear naming and inline documentation  

---

## 📝 Next Steps

1. **Test the MVP locally** → `streamlit run app/main.py`
2. **Explore sample data** → Click "Load Sample Data" in dashboard
3. **Review code** → Start with `app/models/` then `app/services/`
4. **Extend it** → Try adding a new KPI or insight rule

---

## 📄 License

MIT

---

**Version:** 0.1.0  
**Last Updated:** June 2026  
**Status:** MVP (proof of concept, not production)
