import pandas as pd
from typing import Dict, Any, Optional
from datetime import timedelta
import json
from .config_loader import get_column_mapping

class DataProcessor:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.data_sources = {}
        self.load_data_sources()

    def load_data_sources(self) -> None:
        """Load all enabled data sources."""
        for source_name, source_config in self.config['data_sources'].items():
            if source_config['enabled']:
                try:
                    df = pd.read_csv(source_config['file_path'], encoding='utf-8')
                except UnicodeDecodeError:
                    # Try different encoding if utf-8 fails
                    df = pd.read_csv(source_config['file_path'], encoding='latin1')
                
                # Rename columns according to mapping
                column_mapping = get_column_mapping(self.config, source_name)
                df = df.rename(columns={v: k for k, v in column_mapping.items()})
                
                # Convert datetime columns after renaming
                datetime_cols = ['start_datetime', 'stop_datetime', 'prescription_datetime', 
                               'admission_start', 'admission_end', 'sample_datetime']
                for col in datetime_cols:
                    if col in df.columns:
                        df[col] = pd.to_datetime(df[col], errors='coerce')
                
                self.data_sources[source_name] = df

    def _get_order_specifications(self, patient_id: str, patient_contact_id: str, order_id: str) -> list:
        """Get order specifications for a prescription."""
        if 'order_specifications' not in self.data_sources or not self.config['data_sources']['order_specifications']['enabled']:
            return []
        
        specs_df = self.data_sources['order_specifications']
        matching_specs = specs_df[
            (specs_df['patient_id'] == patient_id) &
            (specs_df['patient_contact_id'] == patient_contact_id) &
            (specs_df['order_id'] == order_id)
        ]
        
        if len(matching_specs) == 0:
            return []
        
        return [{
            'question_id': row['question_id'],
            'answer': row['answer']
        } for _, row in matching_specs.iterrows()]

    def process_data(self) -> Dict:
        """Process the data according to configuration and return the final structure."""
        prescriptions_df = self.data_sources['prescriptions']

        result = {}
        
        for patient_id, patient_data in prescriptions_df.groupby('patient_id'):
            admissions_list = []
            
            # Group prescriptions by admission
            for adm_id, adm_data in patient_data.groupby('patient_contact_id'):
                # Create treatment groups within this admission
                adm_data = self._create_treatment_groups(adm_data)
                admission_dict = self._process_admission(adm_id, adm_data)
                admissions_list.append(admission_dict)
            
            result[str(patient_id)] = {
                "admissions": admissions_list
            }
        
        return result

    def _create_treatment_groups(self, prescriptions: pd.DataFrame) -> pd.DataFrame:
        """Create treatment groups based on overlapping prescription times."""
        if len(prescriptions) == 0:
            return prescriptions
        
        # Sort by start time
        prescriptions = prescriptions.sort_values('start_datetime')
        
        # Initialize groups
        current_group = 0
        groups = []
        current_end = prescriptions.iloc[0]['stop_datetime']
        
        for _, row in prescriptions.iterrows():
            # If this prescription starts after the current group ends
            # (with a 24-hour buffer), start a new group
            if pd.notnull(row['start_datetime']) and pd.notnull(current_end):
                if row['start_datetime'] > current_end + pd.Timedelta(hours=24):
                    current_group += 1
                current_end = max(current_end, row['stop_datetime'])
            groups.append(current_group)
        
        prescriptions['group'] = groups
        return prescriptions

    def _process_admission(self, adm_id: str, adm_data: pd.DataFrame) -> Dict:
        """Process a single admission's data."""
        admission_info = self._get_admission_info(adm_id)
        treatments_list = []
        
        for group_id, treatment_data in adm_data.groupby('group'):
            treatment_dict = self._process_treatment(group_id, treatment_data)
            treatments_list.append(treatment_dict)
        
        return {
            "patient_contact_id": adm_id,
            "admission_start": self._format_datetime(admission_info.get('admission_start')),
            "admission_end": self._format_datetime(admission_info.get('admission_end')),
            "treatments": treatments_list
        }

    def _get_admission_info(self, adm_id: str) -> Dict:
        """Get admission information from admissions data source."""
        if 'admissions' not in self.data_sources:
            return {}
        
        admission_data = self.data_sources['admissions']
        matching_admissions = admission_data[admission_data['patient_contact_id'] == adm_id]
        if len(matching_admissions) == 0:
            return {}
        
        admission = matching_admissions.iloc[0]
        return {
            "admission_start": admission['admission_start'],
            "admission_end": admission['admission_end']
        }

    def _process_treatment(self, group_id: str, treatment_data: pd.DataFrame) -> Dict:
        """Process a single treatment's data."""
        treatment_start = treatment_data['start_datetime'].min()
        treatment_end = treatment_data['stop_datetime'].max()
        
        prescriptions_list = []
        for _, presc in treatment_data.iterrows():
            prescription_dict = self._process_prescription(presc)
            prescriptions_list.append(prescription_dict)
        
        return {
            "treatment_id": int(group_id),
            "treatment_start": self._format_datetime(treatment_start),
            "treatment_end": self._format_datetime(treatment_end),
            "prescriptions": prescriptions_list
        }

    def _process_prescription(self, prescription: pd.Series) -> Dict:
        """Process a single prescription's data."""
        # Get time window configuration
        time_windows = self.config['analysis_options']['culture_time_windows']
        window = (time_windows['intra_abdominal'] 
                 if self._is_intra_abdominal(prescription)
                 else time_windows['default'])
        
        # Find relevant cultures
        relevant_cultures = self._find_relevant_cultures(
            prescription['patient_id'],
            prescription['start_datetime'],
            window['hours_before'],
            window['hours_after']
        )
        
        # Get order specifications
        order_specs = self._get_order_specifications(
            prescription['patient_id'],
            prescription['patient_contact_id'],
            prescription.get('order_id', None)
        )
        
        result = {
            "start_datetime": self._format_datetime(prescription['start_datetime']),
            "stop_datetime": self._format_datetime(prescription['stop_datetime']),
            "prescription_datetime": self._format_datetime(prescription['prescription_datetime']),
            "medication_name": prescription['medication_name'],
            "administration_route": prescription['administration_route'],
            "specialty": prescription['specialty'],
            "cultures": relevant_cultures
        }
        
        # Add ATC code if available
        if 'atc_code' in prescription and pd.notna(prescription['atc_code']):
            result["atc_code"] = prescription['atc_code']
        
        # Only add order specifications if they exist
        if order_specs:
            result["order_specifications"] = order_specs
        
        return result

    def _is_intra_abdominal(self, prescription: pd.Series) -> bool:
        """Check if prescription is for intra-abdominal infection."""
        # Check order specifications for intra-abdominal infection
        if 'order_specifications' in self.data_sources and self.config['data_sources']['order_specifications']['enabled']:
            specs = self._get_order_specifications(
                prescription['patient_id'],
                prescription['patient_contact_id'],
                prescription.get('order_id', None)
            )
            
            for spec in specs:
                if spec['answer'] and 'intra-abdominale infectie' in str(spec['answer']).lower():
                    return True
        
        return False

    def _find_relevant_cultures(
        self, 
        patient_id: str, 
        start_time: pd.Timestamp,
        hours_before: int,
        hours_after: int
    ) -> list:
        """Find cultures within the specified time window."""
        if 'cultures' not in self.data_sources or pd.isna(start_time):
            return []
        
        cultures_df = self.data_sources['cultures']
        start_before = start_time - timedelta(hours=hours_before)
        start_after = start_time + timedelta(hours=hours_after)
        
        relevant_cultures = cultures_df[
            (cultures_df['patient_id'] == patient_id) &
            (cultures_df['sample_datetime'] >= start_before) &
            (cultures_df['sample_datetime'] <= start_after)
        ].sort_values('sample_datetime')
        
        return [{
            'sample_datetime': self._format_datetime(row['sample_datetime']),
            'material_category': row['material_category'],
            'culture_result': row['culture_result']
        } for _, row in relevant_cultures.iterrows()]

    def _format_datetime(self, dt) -> Optional[str]:
        """Format datetime to string or return None if input is None."""
        if pd.isna(dt):
            return None
        return dt.strftime("%Y-%m-%d %H:%M:%S")

    def save_output(self, result: Dict) -> None:
        """Save the processed data to the specified output file."""
        output_path = self.config['output']['file_path']
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=4, ensure_ascii=False) 