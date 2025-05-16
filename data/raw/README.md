# Raw Data Directory

This directory contains synthetic raw input data files for each test scenario. These inputs simulate real-world hospital data and are used for testing the prescription and culture data processing pipeline.

## Scenarios

The raw data is organized by test case:

```
data/raw/
├── minimal/         # Basic test case with only prescriptions + cultures
├── alternative/     # Uses hospital-style column names
└── extended/        # Full data: prescriptions, cultures, orders, admissions
```

Each folder contains CSV files named:

- `mmi_MedicatieVoorschrift.csv`
- `kweken.csv`
- `OrderSpecificatievraagAntwoord.csv` *(only for extended)*
- `mmi_OpnameDeeltraject.csv` *(only for extended)*

## File Format

All files are UTF-8 encoded `.csv` files. The columns vary per scenario and are mapped dynamically using the corresponding `config.yaml` in `/test_scenarios/`.

## How to Regenerate

To rebuild all synthetic data folders:

```bash
python data/generate_test_data.py
```

This will overwrite existing CSVs in `data/raw/{scenario}/`.

## Notes

- Data is fully synthetic and does **not** contain any real patient information.
- This structure allows testing a flexible and configurable processing pipeline.