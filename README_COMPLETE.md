# 📊 A/B Creative Analytics Prototype for Video Ads

An MVP for analyzing and comparing A/B video ad creatives using API data. This prototype normalizes experiment data, compares variant performance, and generates business-facing insights.

## 🎯 Project Overview

**Goal:** Build a prototype that helps marketing teams understand which video ad creative variants perform better and why.

**Scope:**
- ✅ Loads API-returned experiment metadata and performance metrics
- ✅ Normalizes nested JSON payloads into clean domain models
- ✅ Compares Variant A vs B across multiple KPIs
- ✅ Generates rule-based business insights
- ✅ Interactive Streamlit dashboard
- ❌ Does NOT process raw video files (API-only)

**Tech Stack:**
- Python 3.9+
- Pydantic (data validation)
- Pandas (data analysis)
- Streamlit (interactive UI)

---

## 📁 Project Structure

```
Marketing Video AB Analysis/
├── README.md                          # This file
├── requirements.txt                   # Python dependencies
├── run.sh                             # Quick start script
│
├── app/
│   ├── __init__.py
│   ├── config.py                      # Constants & configuration
│   ├── main.py                        # ⭐ Streamlit app entry point
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── api_models.py              # Pydantic models for API responses
│   │   └── domain_models.py           # Normalized business models
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── normalizer.py              # Load & normalize API data
│   │   ├── comparator.py              # Compare A vs B variants
│   │   └── insight_generator.py       # Generate business insights
│   │
│   ├── data/
│   │   └── sample_api_response.json   # Example A/B experiment data
│   │
│   └── utils/
│       └── __init__.py
│
└── tests/
    ├── __init__.py
    ├── test_models.py                 # (TBD)
    └── test_services.py               # (TBD)
```

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Or use the quick start script:

```bash
bash run.sh
```

### 2. Run the Streamlit App

```bash
streamlit run app/main.py
```

The app will open in your browser at `http://localhost:8501`

### 3. Load Sample Data

1. Click the **"🔄 Load Sample Data"** button in the left sidebar
2. Explore normalized data in the **"Normalized Data"** section
3. View A/B comparison results in **"A/B Comparison Results"**
4. Read generated insights in **"Generated Insights"**

---

## 🔄 Data Pipeline

### Step 1: Load API Payload
```python
from app.services import normalize_from_file

data = normalize_from_file("app/data/sample_api_response.json")
```

### Step 2: Normalize to Domain Models
The `NormalizedABData` contains:
- Parsed `Experiment` objects (Pydantic models)
- `experiments_df`: Campaign-level metadata
- `variants_df`: Creative asset information
- `metrics_df`: Performance KPIs (CTR, ROAS, spend, etc.)
- `metadata_df`: Creative attributes (duration, hook style, CTA, etc.)

### Step 3: Compare Variants
```python
from app.services import compare_experiments

comparisons = compare_experiments(data, primary_kpi="ctr")
```

Returns list of `ExperimentComparison` objects with:
- Winner variant
- Primary KPI lift
- Secondary metric deltas
- Metadata differences

### Step 4: Generate Insights
```python
from app.services import generate_insight

for comparison in comparisons:
    insight = generate_insight(comparison)
    print(insight.headline)
    print(insight.summary)
```

Returns `InsightResult` with:
- Headline
- Narrative summary (business-friendly tone)
- Key findings (bullet points)
- Confidence level (LOW/MEDIUM/HIGH)

---

## 📊 Example Output

### Comparison Result
```
Winner: Variant B
Primary KPI (CTR): +12.5% lift
  Variant A: 4.8%
  Variant B: 5.4%

Secondary Metrics:
  conversion_rate: +5.8% (3.46% → 3.66%)
  cost_per_click: -3.2%
  roas: +18.4%
```

### Generated Insight
```
Variant B outperformed Variant A with a 12.5% higher CTR. 
Conversion rate also improved, suggesting better downstream engagement. 
The winning variant's shorter duration (15s vs 30s) may have contributed 
to faster value communication. These results are compelling enough to 
consider scaling Variant B.

Confidence: HIGH
```

---

## 🎮 Streamlit App Features

### Sidebar
- **Primary KPI Selection:** Choose KPI to compare on (CTR, ROAS, conversion rate, etc.)
- **Data Loading:** Button to load sample data

### Main Dashboard

1. **Normalized Data Section**
   - Experiments overview table
   - Creative metadata table
   - Performance metrics table

2. **A/B Comparison Results Section**
   - One card per experiment
   - Winner badge
   - Primary + secondary KPI metrics
   - Creative differences
   - Recommendations

3. **Generated Insights Section**
   - Business-focused narratives
   - Key findings
   - Confidence scoring
   - Hypothesis-based framing

---

## 🛠️ Key Modules

### `app/config.py`
Configuration constants:
- Default KPI (`"ctr"`)
- Available KPIs list
- Lift thresholds
- Supported platforms & creative types
- Statistical settings

### `app/models/`
- **`api_models.py`**: Pydantic models matching API response structure
- **`domain_models.py`**: Normalized business models with computed properties

### `app/services/`
- **`normalizer.py`**: Converts nested JSON → domain objects + DataFrames
- **`comparator.py`**: Compares variants, computes deltas & lifts
- **`insight_generator.py`**: Generates business narratives & findings

---

## 📈 Comparison Logic

### Primary KPI Winner
- Variant with higher primary KPI value wins
- Lift = `(B - A) / A × 100%`

### Confidence Scoring
Based on:
- Lift magnitude (strong >10%, moderate >5%)
- Number of supporting metrics
- Metadata differences
- Data completeness

**Confidence Levels:**
- **HIGH**: Strong signal + multiple supporting metrics
- **MEDIUM**: Moderate signal + some secondary confirmation
- **LOW**: Weak signal or limited data

---

## 💡 Insight Generation

Insights are framed as **hypotheses**, not causal claims:
- ✅ "May have contributed..."
- ✅ "Could indicate..."
- ✅ "Suggests..."
- ❌ "Caused..."
- ❌ "Proven..."

Rule-based analysis checks:
1. Primary KPI performance
2. Secondary metrics alignment (conversions, cost efficiency, ROAS)
3. Metadata differences (duration, hook style, CTA type)
4. Threshold-based recommendations

---

## 🧪 Testing

### Manual Testing
```bash
# Load and normalize
python -c "from app.services import normalize_from_file; data = normalize_from_file('app/data/sample_api_response.json'); print(data)"

# Run comparisons
python -c "from app.services import normalize_from_file, compare_experiments; data = normalize_from_file('app/data/sample_api_response.json'); results = compare_experiments(data); print(results[0].summary())"

# Generate insights
python -c "from app.services import normalize_from_file, compare_experiments, generate_insight; data = normalize_from_file('app/data/sample_api_response.json'); results = compare_experiments(data); insight = generate_insight(results[0]); print(insight)"
```

---

## 🎓 Design Principles

1. **Separation of Concerns**
   - API models ↔ Domain models ↔ Services
   - Clear layer boundaries

2. **Type Safety**
   - Pydantic validation on all inputs
   - Full type hints throughout

3. **Extensibility**
   - Easy to add new KPIs
   - Configurable thresholds in `config.py`
   - Modular insight generation rules

4. **Interview-Friendly**
   - Clear structure and naming
   - Well-documented code
   - Simple, readable logic

5. **Business-Focused**
   - Hypothesis-based framing
   - Actionable recommendations
   - Confidence scoring

---

## 📝 Next Steps

- [ ] Add unit tests (`tests/test_models.py`, `tests/test_services.py`)
- [ ] Implement API connector for real data
- [ ] Add statistical significance testing
- [ ] Support more KPI types
- [ ] Export reports (PDF, CSV)
- [ ] Add A/B test duration calculator
- [ ] Implement sequential testing rules

---

## 📚 Sample Data

Pre-loaded sample experiments in `app/data/sample_api_response.json`:

1. **Exp 1: Hook Style** (Facebook)
   - Pattern Interrupt vs Curiosity Gap
   - Result: Pattern interrupt wins on CTR

2. **Exp 2: CTA Button Copy** (Instagram)
   - Urgent ("Buy Now") vs Benefit ("Discover How")
   - Result: Benefit-focused wins on conversion rate

3. **Exp 3: Video Duration** (YouTube)
   - Short form (15s) vs Storytelling (30s)
   - Result: Longer video wins on ROAS

---

## 🤝 Contributing

Guidelines for extending the prototype:

1. **Adding a new KPI:**
   - Add to `AVAILABLE_KPIS` in `config.py`
   - Add calculation logic in `domain_models.py`
   - Comparator will auto-detect it

2. **Modifying insight rules:**
   - Edit `app/services/insight_generator.py`
   - Update thresholds in `InsightGenerator` class
   - Test with sample data

3. **New metadata fields:**
   - Update Pydantic models in `api_models.py`
   - Add to domain models if needed
   - Include in `_compare_metadata()` if business-relevant

---

## 📄 License

MIT (assumed for MVP)

---

## 🔗 Contact

For questions or feedback about this prototype, reach out to the product/marketing analytics team.

---

**Last Updated:** 2026-06-21  
**Version:** 0.1.0
