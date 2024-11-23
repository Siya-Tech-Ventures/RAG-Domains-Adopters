import os
import pandas as pd
from typing import List, Dict, Any
from datetime import datetime
import json
from pathlib import Path

class MaintenanceDataIngestion:
    def __init__(self, base_dir: str):
        """
        Initialize the data ingestion system.
        
        Args:
            base_dir: Base directory for storing processed data
        """
        self.base_dir = base_dir
        self.docs_dir = os.path.join(base_dir, "processed_docs")
        self.performance_dir = os.path.join(base_dir, "performance_data")
        
        # Create necessary directories
        os.makedirs(self.docs_dir, exist_ok=True)
        os.makedirs(self.performance_dir, exist_ok=True)
        
    def process_sample_data(self, sample_data_dir: str) -> Dict[str, List[str]]:
        """
        Process all sample data files and organize them by category.
        
        Args:
            sample_data_dir: Directory containing sample data files
            
        Returns:
            Dictionary mapping categories to lists of processed file paths
        """
        processed_files = {
            "equipment_health": [],
            "maintenance_schedule": [],
            "technical_documentation": [],
            "data_ingestion": []
        }
        
        # Process each file type
        file_mappings = {
            "equipment_health_report.txt": "equipment_health",
            "maintenance_schedule.txt": "maintenance_schedule",
            "technical_documentation.txt": "technical_documentation",
            "data_ingestion_log.txt": "data_ingestion"
        }
        
        for filename, category in file_mappings.items():
            source_path = os.path.join(sample_data_dir, filename)
            if os.path.exists(source_path):
                output_path = self._process_document(source_path, category)
                processed_files[category].append(output_path)
        
        return processed_files
    
    def _process_document(self, source_path: str, category: str) -> str:
        """
        Process a single document and store it with metadata.
        
        Args:
            source_path: Path to the source document
            category: Document category
            
        Returns:
            Path to the processed document
        """
        # Create category-specific directory
        category_dir = os.path.join(self.docs_dir, category)
        os.makedirs(category_dir, exist_ok=True)
        
        # Generate output path
        filename = os.path.basename(source_path)
        output_path = os.path.join(category_dir, f"processed_{filename}")
        
        with open(source_path, 'r') as source, open(output_path, 'w') as target:
            # Add metadata header
            metadata = {
                "category": category,
                "processing_date": datetime.now().isoformat(),
                "source_file": filename
            }
            target.write(f"METADATA: {json.dumps(metadata)}\n\n")
            
            # Copy content
            content = source.read()
            target.write(content)
        
        return output_path
    
    def get_processed_files(self) -> Dict[str, List[str]]:
        """
        Get all processed files organized by category.
        
        Returns:
            Dictionary mapping categories to lists of processed file paths
        """
        processed_files = {
            "equipment_health": [],
            "maintenance_schedule": [],
            "technical_documentation": [],
            "data_ingestion": []
        }
        
        for category in processed_files.keys():
            category_dir = os.path.join(self.docs_dir, category)
            if os.path.exists(category_dir):
                for file in os.listdir(category_dir):
                    if file.endswith('.txt'):
                        processed_files[category].append(
                            os.path.join(category_dir, file)
                        )
        
        return processed_files
    
    def ingest_performance_data(self, 
                              data_path: str, 
                              equipment_id: str,
                              data_format: str = "csv") -> str:
        """
        Ingest and process equipment performance data.
        
        Args:
            data_path: Path to the performance data file
            equipment_id: Unique identifier for the equipment
            data_format: Format of the input data (csv, json, etc.)
            
        Returns:
            Path to the processed performance data
        """
        # Create equipment-specific directory
        equipment_dir = os.path.join(self.performance_dir, equipment_id)
        os.makedirs(equipment_dir, exist_ok=True)
        
        # Load and process data
        if data_format.lower() == "csv":
            df = pd.read_csv(data_path)
        elif data_format.lower() == "json":
            df = pd.read_json(data_path)
        else:
            raise ValueError(f"Unsupported data format: {data_format}")
            
        # Add metadata columns
        df['processing_date'] = datetime.now().isoformat()
        df['equipment_id'] = equipment_id
        
        # Perform basic data validation
        required_columns = ['timestamp', 'measurement_type', 'value']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
            
        # Save processed data
        output_path = os.path.join(
            equipment_dir,
            f"performance_data_{datetime.now().strftime('%Y%m%d')}.csv"
        )
        df.to_csv(output_path, index=False)
        
        return output_path
        
    def create_performance_summary(self, equipment_id: str) -> Dict[str, Any]:
        """
        Create a summary of equipment performance data.
        
        Args:
            equipment_id: Unique identifier for the equipment
            
        Returns:
            Dictionary containing performance summary
        """
        equipment_dir = os.path.join(self.performance_dir, equipment_id)
        if not os.path.exists(equipment_dir):
            return {"error": f"No data found for equipment {equipment_id}"}
            
        # Load all performance data for the equipment
        data_files = list(Path(equipment_dir).glob("performance_data_*.csv"))
        if not data_files:
            return {"error": "No performance data files found"}
            
        # Combine all data files
        dfs = []
        for file in data_files:
            df = pd.read_csv(file)
            dfs.append(df)
            
        combined_df = pd.concat(dfs, ignore_index=True)
        
        # Calculate summary statistics
        summary = {
            "equipment_id": equipment_id,
            "data_period": {
                "start": combined_df['timestamp'].min(),
                "end": combined_df['timestamp'].max()
            },
            "total_measurements": len(combined_df),
            "measurement_types": combined_df['measurement_type'].unique().tolist(),
            "statistics": {}
        }
        
        # Calculate statistics for each measurement type
        for mtype in summary["measurement_types"]:
            mtype_data = combined_df[combined_df['measurement_type'] == mtype]['value']
            summary["statistics"][mtype] = {
                "mean": mtype_data.mean(),
                "std": mtype_data.std(),
                "min": mtype_data.min(),
                "max": mtype_data.max()
            }
            
        return summary
