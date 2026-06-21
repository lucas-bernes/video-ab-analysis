# A/B Creative Analytics Prototype for Video Ads

## Overview
This MVP compares A/B video ad creatives using API data to generate business-facing insights and hypotheses.

### Key Features
- **API-First**: Works with API-returned metadata and performance metrics (no raw video processing)
- **Normalization**: Converts nested API responses into clean domain models
- **Comparison**: Compares variant A vs B across multiple KPIs
- **Business-Ready**: Generates actionable hypotheses and recommendations

### Tech Stack
- **Python 3.9+**
- **Pydantic**: Data validation and serialization
- **Pandas**: Data analysis and manipulation
- **Streamlit**: Interactive dashboard (coming soon)

## Project Structure

```
Marketing Video AB Analysis/
├── README.md                  # This file
├── requirements.txt           # Python dependencies
├── .gitignore                 # Git ignore patterns
├── app/
│   ├── __init__.py
│   ├── config.py              # Constants and configuration
│   ├── models/
│   │   ├── __init__.py
│   │   ├── api_models.py      # Pydantic models for API responses
│   │   └── domain_models.py   # Normalized business models
│   ├── services/
│   │   ├── __init__.py
│   │   └── comparison_service.py   # A/B comparison logic (TBD)
│   ├── utils/
│   │   ├── __init__.py
│   │   └── validators.py      # Custom validators (TBD)
│   └── main.py                # Entry point (TBD)
├── tests/
│   ├── __init__.py
│   ├── test_models.py         # Model tests (TBD)
│   └── test_services.py       # Service tests (TBD)
└── notebooks/
    └── analysis.ipynb         # Exploratory analysis (TBD)
```

## Getting Started

### Installation
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Usage Example
```python
from app.models import APIExperiment, CreativeMetrics
from app.config import DEFAULT_KPI

# Parse API response into domain models
experiment = APIExperiment.parse_obj(api_data)
# ... comparison logic (TBD)
```

## Design Principles
1. **Separation of Concerns**: API models ↔ Domain models ↔ Services
2. **Type Safety**: Extensive use of Pydantic for validation
3. **Extensibility**: Easy to add new KPIs, platforms, and creative types
4. **Testability**: Pure functions and dependency injection ready
5. **Interview-Friendly**: Clear structure, well-documented, modular

## Next Steps
- [ ] Implement `ComparisonService` for A/B analysis
- [ ] Add statistical significance testing
- [ ] Build Streamlit dashboard
- [ ] Add integration tests
- [ ] Connect to real API endpoints
