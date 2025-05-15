# Prescription and Culture Data Processing Pipeline

This pipeline processes prescription and culture data, combining them into a structured JSON output that links prescriptions with relevant cultures based on configurable time windows.

## Project Structure

```
project/
├── data/
│   ├── raw/              # Raw input data files
│   └── processed/        # Generated output files
├── docs/
│   ├── README.md         # Detailed documentation
├── src/
│   ├── core/            # Core processing logic
│   │   ├── config_loader.py
│   │   └── data_processor.py
│   ├── utils/           # Utility functions
│   ├── config.yaml      # Main configuration file
│   └── main.py         # Entry point script
├── test_scenarios/      # Test scenario configurations and data
│   ├── minimal/
│   ├── alternative/
│   └── extended/
└── requirements.txt     # Python dependencies
```

## Quick Start

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the pipeline:
   ```bash
   python src/main.py --config src/config.yaml
   ```

## Documentation

- [Full Documentation](docs/README.md)
- [Test Scenarios](test_scenarios/test_scenarios.md)

## Requirements

- Python 3.9+
- pandas>=1.5.0
- pyyaml>=6.0.0
- numpy<2.0.0

## License

This project is licensed under the MIT License - see the LICENSE file for details. 