"""
Database models for the application.
"""
from app import db
from time_provider import default_time_provider

class BaseModel(db.Model):
    """Base model with common fields."""
    __abstract__ = True
    
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.Float, default=lambda: default_time_provider.current_time())
    updated_at = db.Column(
        db.Float, 
        default=lambda: default_time_provider.current_time(),
        onupdate=lambda: default_time_provider.current_time()
    )

class HealthCheck(BaseModel):
    """Model for storing health check logs."""
    __tablename__ = 'health_checks'
    
    status = db.Column(db.String(50), nullable=False, default='healthy')
    response_time = db.Column(db.Float)
    
    def __repr__(self):
        return f'<HealthCheck {self.status} at {self.created_at}>'
