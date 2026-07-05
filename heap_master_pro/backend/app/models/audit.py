"""
Audit log model for tracking changes.
"""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class AuditLog(Base):
    """Audit log for tracking all changes in the system."""
    
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Action information
    action = Column(String(50), nullable=False)  # create, update, delete, login, export, etc.
    entity_type = Column(String(50), nullable=False)  # user, pad, project, etc.
    entity_id = Column(Integer, nullable=True)
    
    # User who performed the action
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    user = relationship("User", back_populates="audit_logs")
    
    # Project context (if applicable)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    project = relationship("Project", back_populates="audit_logs")
    
    # Change details
    old_values = Column(JSON, nullable=True)  # Previous values (for updates)
    new_values = Column(JSON, nullable=True)  # New values
    changes = Column(Text, nullable=True)  # Human-readable description
    
    # IP and user agent
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f"<AuditLog {self.action} on {self.entity_type} by user {self.user_id}>"
