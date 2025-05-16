# Test Scenarios Documentation

This directory contains three test scenarios that demonstrate different configurations of the prescription and culture data processing pipeline. Each scenario has its own configuration file and associated synthetic input data.

---

## Folder Structure

```
test_scenarios/
├── minimal/              # Basic input only
│   └── config.yaml
├── alternative/          # Hospital-style column names
│   └── config.yaml
├── extended/             # Full input with extra fields
│   └── config.yaml

data/
├── raw/
│   ├── minimal/
│   │   ├── mmi_MedicatieVoorschrift.csv
│   │   └── kweken.csv
│   ├── alternative/
│   │   ├── mmi_MedicatieVoorschrift.csv
│   │   └── kweken.csv
│   └── extended/
│       ├── mmi_MedicatieVoorschrift.csv
│       ├── OrderSpecificatievraagAntwoord.csv
│       ├── mmi_OpnameDeeltraject.csv
│       └── kweken.csv

└── processed/
    ├── minimal/output.json
    ├── alternative/output.json
    └── extended/output.json
```

---

## Scenario Details

### 🔹 1. Minimal

**Purpose**: Test basic required fields and core processing logic.

- **Enabled sources**: prescriptions, cultures
- **Missing**: admissions, order specifications
- **Columns**: minimal; clean English labels
- **Time windows**: 48h before, 24h after

### 🔹 2. Alternative

**Purpose**: Test different raw column names and hospital-style labels.

- **Enabled sources**: prescriptions, cultures
- **Missing**: admissions, order specifications
- **Columns**: different naming conventions (e.g., `mrn`, `encounter_id`)
- **Same logic**, different schema

### 🔹 3. Extended

**Purpose**: Test the full capabilities of the pipeline.

- **Enabled sources**: prescriptions, cultures, admissions, order specifications
- **Columns**: all possible fields (e.g., subspecialty, dosage, ICU status)
- **Time windows**: custom per treatment type (default, intra-abdominal, emergency, ICU)
- **Includes multiple order questions per prescription**

---

## Running the Tests

Generate synthetic data (overwrites all scenarios):

```bash
python data/generate_test_data.py
```

Run a specific test scenario:

```bash
python src/main.py --config test_scenarios/minimal/config.yaml
python src/main.py --config test_scenarios/alternative/config.yaml
python src/main.py --config test_scenarios/extended/config.yaml
```

---

## Validation Summary

| Scenario    | Prescriptions | Cultures | Admissions | Orders | Custom Columns | Time Windows |
|-------------|---------------|----------|------------|--------|----------------|--------------|
| Minimal     | ✅             | ✅        | ❌          | ❌      | ❌              | Basic (48/24) |
| Alternative | ✅             | ✅        | ❌          | ❌      | ✅              | Default       |
| Extended    | ✅             | ✅        | ✅          | ✅      | ✅              | Multiple      |

---

## Usage

These scenarios are useful for:

- Testing configuration flexibility
- Validating internal mapping logic
- Demonstrating edge cases (missing files, alternative schema)
- Onboarding new users

Each scenario includes a corresponding `config.yaml` to match its input data.

---
