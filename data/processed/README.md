# Processed Data Directory

This directory stores the output of the prescription and culture data processing pipeline. Outputs are structured JSON files that contain per-patient treatment episodes linked to relevant microbiological cultures.

## Output Format

- Each processed file is a `.json` file with the structure:

```json
{
  "PSEUDO_1": {
    "admissions": [
      {
        "patient_contact_id": "...",
        "admission_start": "...",
        "treatments": [
          {
            "treatment_start": "...",
            "prescriptions": [...],
            "treatment_cultures": [...]
          }
        ]
      }
    ]
  },
  ...
}
```

- One file is created per scenario, using the output path defined in its `config.yaml`.

## Scenario-based Outputs

Each test scenario writes its result to:

```
data/processed/
├── minimal/       # ← from test_scenarios/minimal/config.yaml
│   └── output.json
├── alternative/
│   └── output.json
├── extended/
│   └── output.json
└── default/       # ← from src/config.yaml
    └── grouped_treatments_and_cultures.json
```

## How to Regenerate

Run the pipeline with the desired config:

```bash
python src/main.py --config test_scenarios/minimal/config.yaml
```

The file will be automatically written to the matching folder under `data/processed/`.

## Notes

- All outputs are fully deterministic based on the input config and data.
- No manual editing is required.
