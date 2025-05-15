# Prescription and Culture Data Processing Pipeline

This pipeline processes prescription and culture data from various healthcare data sources, combining them into a structured JSON output that links prescriptions with relevant cultures based on configurable time windows. The pipeline is designed to be flexible, allowing users to adapt it to different data sources and column names through configuration.

## Table of Contents
1. [Overview](#overview)
2. [Project Structure](#project-structure)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Data Sources](#data-sources)
6. [Core Functionality](#core-functionality)
7. [Running the Pipeline](#running-the-pipeline)
8. [Test Scenarios](#test-scenarios)
9. [Output Format](#output-format)
10. [Customization](#customization)

## Overview

The pipeline takes several input data sources:
- Prescription data (required)
- Culture data (required)
- Admission data (optional)
- Order specifications (optional)

It processes these inputs to:
1. Group prescriptions into treatments based on temporal proximity
2. Match relevant cultures to prescriptions based on configurable time windows
3. Link treatments to hospital admissions when available
4. Generate a structured JSON output

## Project Structure

```
project/
├── config.yaml              # Main configuration file
├── main.py                 # Entry point script
├── config_loader.py        # Configuration loading and validation
├── data_processor.py       # Core data processing logic
├── test_scenarios/         # Test data and configurations
│   ├── minimal/           # Minimal scenario (prescriptions + cultures only)
│   ├── alternative/       # Alternative column names scenario
│   └── extended/         # Extended scenario with additional fields
└── README.md              # This documentation
```

## Installation

1. Requirements:
   ```
   pandas>=1.5.0
   pyyaml>=6.0.0
   numpy>=1.24.0
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

The pipeline uses YAML configuration files to define:
- Data source locations and column mappings
- Analysis options
- Output settings

Example configuration:
```yaml
data_sources:
  prescriptions:
    enabled: true
    file_path: "data/prescriptions.csv"
    columns:
      patient_id: "mrn"
      start_datetime: "medication_start"
      # ... other column mappings

analysis_options:
  culture_time_windows:
    default:
      hours_before: 72
      hours_after: 24
    # ... other time windows

output:
  format: "json"
  file_path: "output.json"
```

### Column Mapping

The configuration allows mapping between your data's column names and the pipeline's internal names. Required mappings for each data source:

#### Prescriptions (Required)
- patient_id: Patient identifier
- patient_contact_id: Admission/encounter identifier
- start_datetime: When the prescription starts
- stop_datetime: When the prescription ends
- prescription_datetime: When the prescription was ordered
- medication_name: Name of the medication
- administration_route: How the medication is administered
- specialty: Prescribing specialty

#### Cultures (Required)
- patient_id: Patient identifier
- sample_datetime: When the culture was collected
- material_category: Type of culture specimen
- culture_result: Result of the culture

#### Admissions (Optional)
- patient_id: Patient identifier
- patient_contact_id: Admission/encounter identifier
- admission_start: Start of admission
- admission_end: End of admission

## Core Functionality

### 1. Data Loading (`data_processor.py`)
- Loads CSV files based on configuration
- Applies column mappings
- Converts datetime fields
- Handles missing or disabled data sources

### 2. Treatment Grouping
The pipeline groups prescriptions into treatments based on:
- Same patient and admission
- Temporal proximity (within 24 hours)
- Overlapping durations

Example:
```python
# Two prescriptions within 24 hours are grouped together
Prescription 1: 2024-01-01 10:00 to 2024-01-07 10:00
Prescription 2: 2024-01-02 09:00 to 2024-01-08 09:00
→ Treatment Group 0
```

### 3. Culture Matching
Cultures are matched to prescriptions based on configurable time windows:
- Default: 72 hours before to 24 hours after prescription start
- Intra-abdominal: 72 hours before to 48 hours after
- Custom windows can be defined in configuration

### 4. Data Processing Flow
1. Load and validate configuration
2. Load data sources
3. Process each patient:
   - Group prescriptions by admission
   - Create treatment groups
   - Match relevant cultures
   - Build output structure
4. Save JSON output

## Running the Pipeline

Basic usage:
```bash
python main.py --config config.yaml
```

The pipeline will:
1. Load the specified configuration
2. Process all enabled data sources
3. Generate the output JSON file

## Test Scenarios

The project includes three test scenarios to demonstrate different use cases:

### 1. Minimal Scenario
- Only prescriptions and cultures
- Basic column names
- No admission data
- Simple time windows

### 2. Alternative Scenario
- All data sources
- Different column naming convention
- Full admission information
- Standard time windows

### 3. Extended Scenario
- All data sources with additional columns
- Complex data relationships
- Multiple time window configurations
- Additional metadata fields

To generate test data:
```bash
python test_scenarios/generate_test_data.py
```

## Output Format

The pipeline generates a JSON file with the following structure:
```json
{
  "patient_id": {
    "admissions": [
      {
        "patient_contact_id": "...",
        "admission_start": "...",
        "admission_end": "...",
        "treatments": [
          {
            "treatment_id": 0,
            "treatment_start": "...",
            "treatment_end": "...",
            "prescriptions": [
              {
                "start_datetime": "...",
                "medication_name": "...",
                "cultures": [
                  {
                    "sample_datetime": "...",
                    "material_category": "...",
                    "culture_result": "..."
                  }
                ]
              }
            ]
          }
        ]
      }
    ]
  }
}
```

## Customization

### Adding New Data Sources
1. Add source configuration to `config.yaml`
2. Define column mappings
3. Update `data_processor.py` if new processing logic is needed

### Modifying Time Windows
Update the `culture_time_windows` section in configuration:
```yaml
analysis_options:
  culture_time_windows:
    custom_case:
      hours_before: 48
      hours_after: 24
```

### Adding Custom Logic
The `DataProcessor` class in `data_processor.py` can be extended with new methods for custom processing requirements.

## Error Handling

The pipeline includes robust error handling:
- Configuration validation
- Data source validation
- DateTime parsing with error handling
- Missing data handling
- Optional data source handling

## Best Practices

1. Always validate your configuration before running
2. Test with a small dataset first
3. Back up your data before processing
4. Monitor memory usage with large datasets
5. Use appropriate time windows for your use case

## Limitations

1. All dates must be in "YYYY-MM-DD HH:MM:SS" format
2. CSV files must use comma as delimiter
3. Memory usage scales with dataset size
4. Treatment grouping uses fixed 24-hour window 