import argparse
from core.config_loader import load_config
from core.data_processor import DataProcessor

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Process prescription and culture data.')
    parser.add_argument('--config', type=str, default='src/config.yaml',
                      help='Path to configuration file (default: src/config.yaml)')
    args = parser.parse_args()

    # Load configuration
    config = load_config(args.config)
    
    # Initialize data processor
    processor = DataProcessor(config)
    
    # Process data
    result = processor.process_data()
    
    # Save output
    processor.save_output(result)

if __name__ == "__main__":
    main() 