import yaml
from typing import Dict, Any
import os

class ConfigurationError(Exception):
    pass

def load_config(config_path: str) -> Dict[str, Any]:
    """Load and validate the configuration file."""
    if not os.path.exists(config_path):
        raise ConfigurationError(f"Configuration file not found: {config_path}")
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    validate_config(config)
    return config

def validate_config(config: Dict[str, Any]) -> None:
    """Validate the configuration structure and required fields."""
    required_sources = ['prescriptions', 'cultures', 'admissions']
    
    if 'data_sources' not in config:
        raise ConfigurationError("Missing 'data_sources' section in config")
    
    # Validate required data sources
    for source in required_sources:
        if source not in config['data_sources']:
            raise ConfigurationError(f"Missing required data source: {source}")
        
        source_config = config['data_sources'][source]
        if 'enabled' not in source_config:
            raise ConfigurationError(f"Missing 'enabled' field for {source}")
        if source_config['enabled']:
            if 'file_path' not in source_config:
                raise ConfigurationError(f"Missing 'file_path' for enabled source: {source}")
            if 'columns' not in source_config:
                raise ConfigurationError(f"Missing 'columns' mapping for enabled source: {source}")
    
    # Validate analysis options
    if 'analysis_options' not in config:
        raise ConfigurationError("Missing 'analysis_options' section in config")
    
    analysis_options = config['analysis_options']
    if 'culture_time_windows' not in analysis_options:
        raise ConfigurationError("Missing 'culture_time_windows' in analysis_options")
    
    # Validate output configuration
    if 'output' not in config:
        raise ConfigurationError("Missing 'output' section in config")
    if 'file_path' not in config['output']:
        raise ConfigurationError("Missing 'file_path' in output configuration")

def get_column_mapping(config: Dict[str, Any], source: str) -> Dict[str, str]:
    """Get the column mapping for a specific data source."""
    if not config['data_sources'][source]['enabled']:
        return {}
    return config['data_sources'][source]['columns'] 