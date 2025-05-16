# Prescription and Culture Data Processing Pipeline – Technical Reference

This pipeline processes antimicrobial prescription and microbiology culture data from hospital systems. It combines multiple data sources into a structured JSON format per patient, linking treatments with relevant cultures using configurable time windows.

The pipeline is modular, configuration-driven, and supports flexible column mappings and optional data sources.

---

## Table of Contents

1. [Overview](#overview)  
2. [Project Structure](#project-structure)  
3. [Installation](#installation)  
4. [Configuration](#configuration)  
5. [Data Sources](#data-sources)  
6. [Processing Steps](#processing-steps)  
7. [Running the Pipeline](#running-the-pipeline)  
8. [Test Scenarios](#test-scenarios)  
9. [Output Format](#output-format)  
10. [Customization](#customization)  
11. [Error Handling](#error-handling)  
12. [Best Practices](#best-practices)  
13. [Limitations](#limitations)

---

## Overview

The pipeline ingests the following input data:

- **Prescriptions** (required)
- **Cultures** (required)
- **Admissions** (optional)
- **Order specifications** (optional)

It then:
1. Groups prescriptions into treatments (within 24h of each other)
2. Matches relevant cultures using time windows
3. Links treatments to admissions if available
4. Outputs structured JSON grouped by patient

---

## Project Structure

```
martijnsiepel01-dynamic_atmt/
├── data/
│   ├── raw/                 # Scenario input data (CSV)
│   ├── processed/           # Generated JSON outputs
│   └── generate_test_data.py
├── src/
│   ├── config.yaml          # Default configuration
│   ├── main.py              # Entry point
│   └── core/
│       ├── config_loader.py
│       └── data_processor.py
├── test_scenarios/
│   ├── minimal/
│   ├── alternative/
│   ├── extended/
│   └── test_scenarios.md
└── docs/
    └── reference.md         # ← This file
```

---

## Installation

1. Requirements:
   - Python 3.9+
   - pandas ≥ 1.5.0
   - pyyaml ≥ 6.0.0
   - numpy < 2.0.0

2. Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Configuration

All settings are controlled via a YAML file. Each scenario has its own config in `test_scenarios/{scenario}/config.yaml`.

### Structure

```yaml
data_sources:
  prescriptions:
    enabled: true
    file_path: "data/raw/extended/mmi_MedicatieVoorschrift.csv"
    columns:
      required:
        patient_id: "Pseudo_id"
        ...
      optional:
        specialty: "SpecialismeOmschrijving"
        ...
```

Each source has:
- `enabled`: whether to load it
- `file_path`: path to CSV file
- `columns.required`: must map all internal required fields
- `columns.optional`: any extra fields to pass through

### Time Window Settings

```yaml
analysis_options:
  culture_time_windows:
    default:
      hours_before: 72
      hours_after: 24
    intra_abdominal:
      hours_before: 72
      hours_after: 48
```

---

## Data Sources

### Required

#### Prescriptions
| Internal Name         | Description                          |
|-----------------------|--------------------------------------|
| patient_id            | Unique patient identifier            |
| patient_contact_id    | Hospital contact/admission ID        |
| start_datetime        | When prescription starts             |
| stop_datetime         | When prescription ends               |
| prescription_datetime | When it was ordered                  |
| medication_name       | Generic name of the antibiotic       |

#### Cultures
| Internal Name      | Description                           |
|--------------------|---------------------------------------|
| patient_id         | Unique patient identifier             |
| sample_datetime    | Timestamp of culture collection       |
| material_category  | Type/category of sample (e.g., blood) |

### Optional

#### Admissions
| Internal Name      | Description                    |
|--------------------|--------------------------------|
| admission_start    | Timestamp of admission start   |
| admission_end      | Timestamp of discharge         |

#### Order Specifications
| Internal Name   | Description                       |
|------------------|----------------------------------|
| order_id         | Unique prescription/order ID     |
| question_id      | The question asked               |
| answer           | The recorded answer              |

---

## Processing Steps

### 1. Load and Validate Configuration
Ensures all required column mappings are present per enabled source.

### 2. Load CSV Files
- Columns are renamed to internal names
- Extra columns are dropped
- Timestamps are parsed to `datetime`

### 3. Group Prescriptions into Treatments
Prescriptions are grouped when:
- They belong to the same patient and contact
- They are within 24 hours of each other

### 4. Match Cultures to Treatment Start
Cultures are selected when:
- `patient_id` matches
- `sample_datetime` is within the configured window around treatment start

### 5. Link Order Specifications
If available, order specifications are matched by:
- `patient_id`, `patient_contact_id`, and `order_id`

---

## Running the Pipeline

Run the pipeline using a config:

```bash
python src/main.py --config test_scenarios/extended/config.yaml
```

Or use the default:

```bash
python src/main.py --config src/config.yaml
```

To generate synthetic input data:

```bash
python data/generate_test_data.py
```

---

## Test Scenarios

Each scenario lives under `test_scenarios/` and uses its own config file + generated data in `data/raw/`.

| Scenario    | Prescriptions | Cultures | Admissions | Orders | Custom Names | Extra Fields |
|-------------|---------------|----------|------------|--------|--------------|---------------|
| Minimal     | ✅             | ✅        | ❌          | ❌      | English       | No            |
| Alternative | ✅             | ✅        | ❌          | ❌      | Hospital-style | No            |
| Extended    | ✅             | ✅        | ✅          | ✅      | Dutch         | Yes           |

---

## Output Format

Each run generates a `.json` file (default: `grouped_treatments_and_cultures.json`):

### Example Structure

```json
{
  "PSEUDO_1": {
    "admissions": [
      {
        "patient_contact_id": "CONTACT_1409",
        "admission_start": "2023-01-01 10:00:00",
        "admission_end": "2023-01-10 12:00:00",
        "treatments": [
          {
            "treatment_id": 0,
            "treatment_start": "2023-01-01 10:00:00",
            "treatment_end": "2023-01-07 10:00:00",
            "prescriptions": [
              {
                "medication_name": "DOXYCILINE",
                "start_datetime": "2023-01-01 10:00:00",
                ...
              }
            ],
            "treatment_cultures": [
              {
                "sample_datetime": "2023-01-01 08:00:00",
                "material_category": "Bloed",
                "culture_result": "Positief"
              }
            ]
          }
        ]
      }
    ]
  }
}
```

---

## Customization

### Adding New Optional Columns
- Add them to `columns.optional` in the config
- No code changes needed if passthrough is sufficient

### Adding a New Data Source
1. Add it under `data_sources` in config
2. Add a loader to `DataProcessor.load_data_sources()` if needed

### Changing Grouping Logic
- Modify `_create_treatment_groups()` in `data_processor.py`

### Modifying Culture Matching Windows
Edit `analysis_options.culture_time_windows` in your config file.

---

## Error Handling

Handled internally:
- Missing config sections or required columns → `ConfigurationError`
- Missing files → graceful exit
- Timestamp parsing errors → `NaT` values skipped
- Optional sources can be disabled cleanly

---

## Best Practices

- Validate your config before running
- Run small test scenarios before scaling up
- Keep test configs under `test_scenarios/` for clarity
- Use `generate_test_data.py` to simulate new cases

---

## Limitations

1. Assumes data is in `.csv` format (UTF-8 encoded)
2. Timestamp fields must be parseable to `datetime`
3. Grouping uses a fixed 24-hour gap rule (custom logic must be added manually)
4. Memory usage scales linearly with dataset size

---
