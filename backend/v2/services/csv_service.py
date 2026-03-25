"""
CSV Upload Service for CarbonSense v2
Handle CSV data import, validation, and batch processing
"""

from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
from sqlalchemy.orm import Session
import csv
import io
from datetime import datetime, timedelta
import re


@dataclass
class CSVValidationResult:
    """Result of CSV validation"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    data_points: int
    date_range: Optional[Tuple[str, str]]
    numeric_columns: List[str]
    parsed_data: Optional[List[Dict[str, Any]]]


@dataclass
class CSVImportResult:
    """Result of CSV import"""
    success: bool
    imported_rows: int
    skipped_rows: int
    emissions_series: List[float]
    dates: List[str]
    metadata: Dict[str, Any]
    message: str


class CSVUploadService:
    """Handle CSV file uploads for emissions data"""
    
    def __init__(self):
        """Initialize CSV service"""
        self.supported_formats = ['csv', 'txt']
        self.max_file_size_mb = 10
        self.max_rows = 10000
    
    def validate_csv_content(
        self,
        csv_content: str,
        delimiter: str = ",",
        expected_columns: Optional[List[str]] = None
    ) -> CSVValidationResult:
        """
        Validate CSV content structure and data
        
        Args:
            csv_content: Raw CSV content as string
            delimiter: CSV delimiter (default: comma)
            expected_columns: List of required columns
        
        Returns:
            CSVValidationResult with validation details
        """
        errors = []
        warnings = []
        data_points = 0
        numeric_columns = []
        parsed_data = []
        date_range = None
        
        if not csv_content or len(csv_content.strip()) == 0:
            return CSVValidationResult(
                is_valid=False,
                errors=["CSV content is empty"],
                warnings=[],
                data_points=0,
                date_range=None,
                numeric_columns=[],
                parsed_data=None
            )
        
        # Parse CSV
        try:
            csv_reader = csv.DictReader(
                io.StringIO(csv_content),
                delimiter=delimiter
            )
            
            if not csv_reader.fieldnames:
                errors.append("CSV has no header row")
                return CSVValidationResult(
                    is_valid=False,
                    errors=errors,
                    warnings=warnings,
                    data_points=0,
                    date_range=None,
                    numeric_columns=[],
                    parsed_data=None
                )
            
            # Check expected columns
            if expected_columns:
                missing_cols = set(expected_columns) - set(csv_reader.fieldnames)
                if missing_cols:
                    errors.append(
                        f"Missing columns: {', '.join(missing_cols)}"
                    )
            
            # Parse rows
            dates = []
            emissions = []
            
            for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 (skip header)
                if row_num - 1 > self.max_rows:
                    errors.append(f"CSV exceeds maximum {self.max_rows} rows")
                    break
                
                # Skip empty rows
                if all(v == '' for v in row.values()):
                    continue
                
                parsed_row = {}
                has_date = False
                has_emissions = False
                
                for col, value in row.items():
                    col_lower = col.lower().strip()
                    
                    # Try to parse date
                    if any(x in col_lower for x in ['date', 'time', 'month', 'year']):
                        date_str = self._parse_date(value)
                        if date_str:
                            parsed_row['date'] = date_str
                            dates.append(date_str)
                            has_date = True
                        else:
                            warnings.append(f"Row {row_num}: Could not parse date '{value}'")
                    
                    # Try to parse emissions
                    elif any(x in col_lower for x in ['co2', 'emissions', 'carbon', 'kg', 'value', 'data']):
                        try:
                            em_value = float(value)
                            if em_value < 0:
                                warnings.append(f"Row {row_num}: Negative emissions value {em_value}")
                            parsed_row['emissions'] = em_value
                            emissions.append(em_value)
                            has_emissions = True
                            
                            if col_lower not in numeric_columns:
                                numeric_columns.append(col_lower)
                        except (ValueError, TypeError):
                            warnings.append(f"Row {row_num}: Could not parse emissions '{value}'")
                
                if has_emissions:
                    parsed_row['row_number'] = row_num
                    parsed_data.append(parsed_row)
                    data_points += 1
            
            # Validate data points
            if data_points == 0:
                errors.append("No valid emissions data found in CSV")
            elif data_points < 3:
                errors.append(f"Need at least 3 data points, found {data_points}")
            
            # Calculate date range
            if dates:
                date_range = (min(dates), max(dates))
            
        except Exception as e:
            errors.append(f"CSV parsing error: {str(e)}")
            return CSVValidationResult(
                is_valid=False,
                errors=errors,
                warnings=warnings,
                data_points=0,
                date_range=None,
                numeric_columns=[],
                parsed_data=None
            )
        
        is_valid = len(errors) == 0
        
        return CSVValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            data_points=data_points,
            date_range=date_range,
            numeric_columns=numeric_columns,
            parsed_data=parsed_data if is_valid else None
        )
    
    def import_csv_data(
        self,
        csv_content: str,
        delimiter: str = ",",
        source_name: str = "Uploaded CSV",
        db: Session = None
    ) -> CSVImportResult:
        """
        Import CSV data and extract emissions series
        
        Args:
            csv_content: Raw CSV content
            delimiter: CSV delimiter
            source_name: Name/description of data source
        
        Returns:
            CSVImportResult with extracted emissions data
        """
        # Validate first
        validation = self.validate_csv_content(csv_content, delimiter)
        
        if not validation.is_valid:
            return CSVImportResult(
                success=False,
                imported_rows=0,
                skipped_rows=0,
                emissions_series=[],
                dates=[],
                metadata={"errors": validation.errors},
                message=f"Validation failed: {'; '.join(validation.errors)}"
            )
        
        # Extract emissions series
        emissions_series = []
        dates = []
        imported_rows = 0
        
        for row in validation.parsed_data:
            if 'emissions' in row:
                emissions_series.append(row['emissions'])
                if 'date' in row:
                    dates.append(row['date'])
                imported_rows += 1
        
        # Calculate metadata
        metadata = {
            "source": source_name,
            "import_timestamp": datetime.now().isoformat(),
            "total_points": len(emissions_series),
            "date_range": validation.date_range,
            "statistics": {
                "min": round(min(emissions_series), 2) if emissions_series else None,
                "max": round(max(emissions_series), 2) if emissions_series else None,
                "avg": round(sum(emissions_series) / len(emissions_series), 2) if emissions_series else None,
            },
            "warnings": validation.warnings
        }
        
        result = CSVImportResult(
            success=True,
            imported_rows=imported_rows,
            skipped_rows=validation.data_points - imported_rows if hasattr(validation, 'data_points') else 0,
            emissions_series=emissions_series,
            dates=dates,
            metadata=metadata,
            message=f"Successfully imported {imported_rows} emissions data points from CSV"
        )
        
        # Store in database if session provided
        if db:
            self._store_csv_import(db, result, source_name)
        
        return result
    
    def validate_batch_csv(
        self,
        csv_contents: List[str],
        source_names: List[str]
    ) -> Dict[str, Any]:
        """
        Validate multiple CSV files for batch processing
        
        Args:
            csv_contents: List of CSV content strings
            source_names: List of source names for each CSV
        
        Returns:
            Batch validation results
        """
        results = {
            "total_files": len(csv_contents),
            "valid_files": 0,
            "invalid_files": 0,
            "errors": [],
            "files": []
        }
        
        for content, source in zip(csv_contents, source_names):
            validation = self.validate_csv_content(content)
            
            file_result = {
                "source": source,
                "is_valid": validation.is_valid,
                "data_points": validation.data_points,
                "date_range": validation.date_range,
                "errors": validation.errors,
                "warnings": validation.warnings
            }
            
            results["files"].append(file_result)
            
            if validation.is_valid:
                results["valid_files"] += 1
            else:
                results["invalid_files"] += 1
                results["errors"].extend([
                    f"{source}: {err}" for err in validation.errors
                ])
        
        return results
    
    def _parse_date(self, date_str: str) -> Optional[str]:
        """
        Parse various date formats
        
        Supported formats:
        - YYYY-MM-DD
        - MM/DD/YYYY
        - DD/MM/YYYY
        - YYYY-MM
        - Month names
        """
        if not date_str or not isinstance(date_str, str):
            return None
        
        date_str = date_str.strip()
        
        # Try common formats
        formats = [
            "%Y-%m-%d",      # 2024-01-15
            "%m/%d/%Y",      # 01/15/2024
            "%d/%m/%Y",      # 15/01/2024
            "%Y-%m",         # 2024-01
            "%B %Y",         # January 2024
            "%b %Y",         # Jan 2024
            "%Y/%m/%d",      # 2024/01/15
        ]
        
        for fmt in formats:
            try:
                parsed = datetime.strptime(date_str, fmt)
                return parsed.strftime("%Y-%m-%d")
            except ValueError:
                continue
        
        return None
    
    def generate_import_summary(
        self,
        import_result: CSVImportResult
    ) -> Dict[str, Any]:
        """Generate human-readable import summary"""
        
        return {
            "status": "success" if import_result.success else "failed",
            "imported_rows": import_result.imported_rows,
            "skipped_rows": import_result.skipped_rows,
            "total_data_points": len(import_result.emissions_series),
            "date_range": {
                "start": import_result.dates[0] if import_result.dates else None,
                "end": import_result.dates[-1] if import_result.dates else None,
            },
            "emissions_statistics": {
                "min_kg": import_result.metadata.get("statistics", {}).get("min"),
                "max_kg": import_result.metadata.get("statistics", {}).get("max"),
                "average_kg": import_result.metadata.get("statistics", {}).get("avg"),
                "total_kg": round(sum(import_result.emissions_series), 2) if import_result.emissions_series else 0
            },
            "next_steps": [
                "Use emissions_series for LSTM forecasting",
                "Run anomaly detection on imported data",
                "Generate Monte Carlo simulations",
                "Compare with ESG benchmarks"
            ]
        }
    
    def _store_csv_import(self, db: Session, result: CSVImportResult, source_name: str) -> None:
        """Store CSV import log in database"""
        try:
            from services.database_service import DatabaseService
            
            # Log the CSV import event
            DatabaseService.log_csv_import(
                db=db,
                filename=source_name,
                rows_imported=result.imported_rows,
                import_status="success" if result.success else "failed",
                import_metadata={
                    "skipped_rows": result.skipped_rows,
                    "date_range": result.metadata.get("date_range"),
                    "statistics": result.metadata.get("statistics"),
                    "warnings": result.metadata.get("warnings", [])
                }
            )
            
            # Also store the imported emissions as historical data if successful
            if result.success and result.emissions_series:
                for idx, value in enumerate(result.emissions_series):
                    DatabaseService.store_historical_data(
                        db=db,
                        emissions_value=value,
                        data_source=source_name,
                        is_training_data=True,
                        import_batch_id=f"csv_{result.metadata.get('import_timestamp')}"
                    )
        except Exception as e:
            print(f"Database storage error in CSV import: {str(e)}")
