"""
Database Models for CarbonSense
Defines table structures for storing data
"""

from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, Text, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from config.db_config import SQLALCHEMY_DATABASE_URL, POOL_CONFIG

Base = declarative_base()

# Create engine with connection pooling
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=POOL_CONFIG['pool_size'],
    max_overflow=POOL_CONFIG['max_overflow'],
    pool_timeout=POOL_CONFIG['pool_timeout'],
    pool_recycle=POOL_CONFIG['pool_recycle'],
    pool_pre_ping=POOL_CONFIG['pool_pre_ping'],
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class UserInputData(Base):
    """Store user-entered emissions data"""
    __tablename__ = "user_input_data"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    sector = Column(String(100), index=True)  # energy, transport, manufacturing, etc.
    emissions_value = Column(Float)  # kg CO2
    unit = Column(String(50), default="kg CO2")
    description = Column(Text, nullable=True)
    source = Column(String(100), nullable=True)  # web form, csv upload, api, etc.
    meta = Column(JSON, nullable=True)  # Additional fields as JSON

    # Relationships
    predictions = relationship("PredictionData", back_populates="input_data")

    def __repr__(self):
        return f"<UserInputData(id={self.id}, sector={self.sector}, value={self.emissions_value})>"


class HistoricalData(Base):
    """Store historical/training data used for predictions"""
    __tablename__ = "historical_data"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, index=True)
    sector = Column(String(100), index=True)
    emissions_value = Column(Float)  # kg CO2
    unit = Column(String(50), default="kg CO2")
    data_source = Column(String(100), nullable=True)  # csv, manual, previous prediction, etc.
    is_training_data = Column(Integer, default=1)  # 1 = used for training, 0 = validation
    created_at = Column(DateTime, default=datetime.utcnow)
    meta = Column(JSON, nullable=True)

    def __repr__(self):
        return f"<HistoricalData(id={self.id}, timestamp={self.timestamp}, value={self.emissions_value})>"


class PredictionData(Base):
    """Store predictions from ML models"""
    __tablename__ = "prediction_data"

    id = Column(Integer, primary_key=True, index=True)
    input_id = Column(Integer, ForeignKey("user_input_data.id"), nullable=True)
    prediction_type = Column(String(50), index=True)  # lstm, anomaly, simulation, etc.
    predicted_value = Column(Float)
    confidence_score = Column(Float, nullable=True)  # 0-1 or 0-100
    confidence_interval_low = Column(Float, nullable=True)
    confidence_interval_high = Column(Float, nullable=True)
    model_version = Column(String(50), nullable=True)  # e.g., "v1.0", "lstm-20260325"
    input_features = Column(JSON)  # Store the features used for prediction
    prediction_result = Column(JSON)  # Complete prediction result as JSON
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    meta = Column(JSON, nullable=True)

    # Relationships
    input_data = relationship("UserInputData", back_populates="predictions")

    def __repr__(self):
        return f"<PredictionData(id={self.id}, type={self.prediction_type}, value={self.predicted_value})>"


class AnomalyData(Base):
    """Store anomaly detection results"""
    __tablename__ = "anomaly_data"

    id = Column(Integer, primary_key=True, index=True)
    input_id = Column(Integer, ForeignKey("user_input_data.id"), nullable=True)
    is_anomaly = Column(Integer)  # 1 = anomaly, 0 = normal
    anomaly_score = Column(Float)  # -1 to 1
    severity = Column(String(20))  # LOW, MEDIUM, HIGH, CRITICAL
    deviation_percent = Column(Float)
    detection_method = Column(String(50))  # isolation_forest, statistical, etc.
    baseline_value = Column(Float, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    meta = Column(JSON, nullable=True)

    def __repr__(self):
        return f"<AnomalyData(id={self.id}, is_anomaly={self.is_anomaly}, severity={self.severity})>"


class AlertData(Base):
    """Store generated alerts"""
    __tablename__ = "alert_data"

    id = Column(Integer, primary_key=True, index=True)
    alert_type = Column(String(50), index=True)  # threshold_exceeded, anomaly_detected, trend_change, forecast_warning
    severity = Column(String(20))  # LOW, MEDIUM, HIGH, CRITICAL
    current_value = Column(Float)
    threshold_value = Column(Float, nullable=True)
    message = Column(Text)
    is_active = Column(Integer, default=1)  # 1 = active, 0 = acknowledged
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    acknowledged_at = Column(DateTime, nullable=True)
    meta = Column(JSON, nullable=True)

    def __repr__(self):
        return f"<AlertData(id={self.id}, type={self.alert_type}, severity={self.severity})>"


class ReportData(Base):
    """Store generated reports"""
    __tablename__ = "report_data"

    id = Column(Integer, primary_key=True, index=True)
    report_type = Column(String(50), index=True)  # executive, detailed, comparative, forecast, full
    report_content = Column(JSON)  # Complete report as JSON
    summary = Column(Text, nullable=True)
    data_period_start = Column(DateTime)
    data_period_end = Column(DateTime)
    total_emissions = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    meta = Column(JSON, nullable=True)

    def __repr__(self):
        return f"<ReportData(id={self.id}, type={self.report_type})>"


class CSVImportLog(Base):
    """Log CSV imports for audit trail"""
    __tablename__ = "csv_import_log"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255))
    rows_imported = Column(Integer)
    rows_failed = Column(Integer)
    import_status = Column(String(50))  # success, partial, failed
    error_message = Column(Text, nullable=True)
    imported_at = Column(DateTime, default=datetime.utcnow, index=True)
    meta = Column(JSON, nullable=True)

    def __repr__(self):
        return f"<CSVImportLog(id={self.id}, filename={self.filename}, rows={self.rows_imported})>"


# Create all tables
def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)
    print("✓ All database tables created successfully!")


def get_db():
    """Dependency for getting DB session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
