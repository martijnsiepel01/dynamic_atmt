# Test Scenarios Documentation

This directory contains three test scenarios designed to demonstrate different aspects of the prescription and culture data processing pipeline. Each scenario has its own configuration file that references data from the central data directory.

## Overview

```
test_scenarios/
├── minimal/              # Minimal scenario
│   └── config.yaml      # Configuration with basic settings
├── alternative/         # Alternative naming scenario
│   └── config.yaml     # Configuration with different column names
└── extended/           # Extended scenario
    └── config.yaml     # Configuration with additional fields

data/
├── raw/                # Input data files
│   ├── prescriptions.csv
│   ├── cultures.csv
│   ├── microbiology.csv
│   ├── encounters.csv
│   ├── orders.csv
│   └── admissions.csv
└── processed/          # Output data files
    ├── minimal/        # Minimal scenario outputs
    ├── alternative/    # Alternative scenario outputs
    └── extended/       # Extended scenario outputs
```

## Scenario Details

### 1. Minimal Scenario

Demonstrates the core functionality with minimal required data:

#### Data Sources:
- **Prescriptions** (from data/raw/prescriptions.csv):
  - Basic fields: patient number, visit ID, dates, drug info
  - Simple column names in English
- **Cultures** (from data/raw/cultures.csv):
  - Basic fields: patient number, collection time, specimen type, result
  - Simple matching based on time windows

#### Features:
- No admission data (null values in output)
- Basic time window configuration (48h before, 24h after)
- Simple treatment grouping

#### Example Data:
```csv
# data/raw/prescriptions.csv
patient_number,visit_id,start_date,end_date,drug_name,route
P001,V101,2024-01-01 08:00:00,2024-01-07 08:00:00,Amoxicillin,oral
```

### 2. Alternative Scenario

Demonstrates flexibility with different naming conventions:

#### Data Sources:
- **Prescriptions** (from data/raw/prescriptions.csv):
  - Hospital-style column names (mrn, encounter_id, etc.)
  - Additional medication details
- **Cultures** (from data/raw/microbiology.csv):
  - Lab-style column names
  - Extended specimen information
- **Admissions** (from data/raw/encounters.csv):
  - Hospital encounter data
- **Orders** (from data/raw/orders.csv):
  - Order specifications and indications

#### Features:
- Full admission information
- Standard time windows
- Complete data linkage

#### Example Data:
```csv
# data/raw/prescriptions.csv
mrn,encounter_id,medication_start,medication_stop,generic_name,admin_route
MRN001,ENC001,2024-02-01 10:00:00,2024-02-07 10:00:00,Piperacillin-Tazobactam,intravenous
```

### 3. Extended Scenario

Demonstrates full capabilities with additional fields:

#### Data Sources:
- **Prescriptions** (from data/raw/prescriptions.csv):
  - All standard fields
  - Additional fields:
    - Subspecialty
    - Department
    - Dosage information
    - Frequency
    - Order status
- **Cultures** (from data/raw/cultures.csv):
  - Extended information:
    - Material codes
    - Detailed descriptions
    - Culture purpose
    - Department
    - Location
- **Admissions** (from data/raw/admissions.csv):
  - Additional fields:
    - Emergency status
    - ICU status
    - Specialty details
    - Duration calculations
- **Orders** (from data/raw/orders.csv):
  - Detailed specifications
  - Multiple questions per order
  - Location information
  - Order status flags

#### Features:
- Multiple time window configurations
- Complex data relationships
- Additional metadata in output
- Dutch column names (matching original system)

#### Example Data:
```csv
# data/raw/prescriptions.csv
Pseudo_id,PatientContactId,StartDatumTijd,StopDatumTijd,MedicatieStofnaam,ToedieningsRoute
PSEUDO_1,CONTACT_1234,2024-01-01 08:00:00,2024-01-07 08:00:00,AMOXICILLINE,oraal
```

## Running the Tests

1. Generate test data:
   ```bash
   python generate_test_data.py
   ```

2. Run individual scenarios:
   ```bash
   python ../main.py --config minimal/config.yaml
   python ../main.py --config alternative/config.yaml
   python ../main.py --config extended/config.yaml
   ```

## Data Generation

The `generate_test_data.py` script creates realistic test data in the data/raw directory:
- Uses consistent patient and visit IDs across files
- Generates temporally coherent dates
- Creates meaningful relationships between prescriptions and cultures
- Adds realistic medical terminology and values

## Validation

Each scenario tests different aspects:
1. **Minimal**: Core functionality and required fields
2. **Alternative**: Column name mapping and data source flexibility
3. **Extended**: Additional fields and complex relationships

## Expected Outputs

Each scenario generates a JSON file in its respective output directory:
- Minimal: data/processed/minimal/output.json
- Alternative: data/processed/alternative/output.json
- Extended: data/processed/extended/output.json

## Using as Examples

These scenarios serve as templates for:
1. Setting up new data sources
2. Mapping different column names
3. Adding custom fields
4. Configuring time windows
5. Testing data relationships 