# Prescription and Culture Data Processing Pipeline

This pipeline processes antimicrobial prescription and microbiology culture data, combining them into structured per-patient JSON outputs. It supports dynamic configuration, linking prescriptions to relevant cultures based on configurable time windows.

## Project Structure

```
dynamic_atmt/
├── data/
│   ├── raw/                # Raw input data (by scenario)
│   ├── processed/          # Output JSON files
│   └── generate_test_data.py  # Script to create synthetic test cases
├── docs/
│   └── README.md           # (Optional) Extended documentation
├── src/
│   ├── core/               # Core logic: config + processing
│   │   ├── config_loader.py
│   │   └── data_processor.py
│   ├── config.yaml         # Default config
│   └── main.py             # Entry point
├── test_scenarios/         # Configs for test data variants
│   ├── minimal/
│   ├── alternative/
│   ├── extended/
│   └── test_scenarios.md   # Describes each scenario
└── requirements.txt        # Python dependencies
```

## Quick Start

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the default pipeline:
   ```bash
   python src/main.py --config src/config.yaml
   ```

3. Run a specific test scenario:
   ```bash
   python src/main.py --config test_scenarios/minimal/config.yaml
   ```

4. Generate fresh synthetic test data:
   ```bash
   python data/generate_test_data.py
   ```

## Configuration

Each config file maps raw input columns to internal names. The structure supports:
- Required vs. optional fields
- Custom input file locations
- Scenario-specific culture time windows

## Documentation

- [Full Documentation](docs/README.md)
- [Test Scenarios Overview](test_scenarios/test_scenarios.md)

## Requirements

- Python 3.9+
- pandas >= 1.5.0
- pyyaml >= 6.0.0
- numpy < 2.0.0

## License

This project is licensed under the MIT License – see the LICENSE file for details.
