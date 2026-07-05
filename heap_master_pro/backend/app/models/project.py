"""
Project model for organizing pads into groups.
"""
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Project(Base):
    """Project model for grouping related heap leach pads."""
    
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Location information
    location_name = Column(String(255), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    # Company association (multi-tenant)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)
    company = relationship("Company", back_populates="projects")
    
    # Owner
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="projects")
    
    # Status
    status = Column(String(50), default="active")  # active, archived, completed
    is_active = Column(Boolean, default=True)
    
    # Settings
    default_slope = Column(Float, default=37.0)
    default_acid_consumption = Column(Float, default=15.0)
    measurement_system = Column(String(20), default="metric")  # metric, imperial
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    pads = relationship("Pad", back_populates="project", cascade="all, delete-orphan")
    members = relationship("ProjectMember", back_populates="project", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="project")
    
    def __repr__(self):
        return f"<Project {self.name}>"
    
    @property
    def total_volume(self) -> float:
        """Calculate total volume of all pads in project."""
        return sum(pad.calculated_volume or 0 for pad in self.pads)
    
    @property
    def total_copper(self) -> float:
        """Calculate total recoverable copper in project."""
        return sum(pad.calculated_copper or 0 for pad in self.pads)


class ProjectMember(Base):
    """Project membership for team collaboration."""
    
    __tablename__ = "project_members"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    project = relationship("Project", back_populates="members")
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="project_memberships")
    
    # Role in project
    role = Column(String(50), default="viewer")  # viewer, editor, admin
    can_edit = Column(Boolean, default=False)
    can_delete = Column(Boolean, default=False)
    can_export = Column(Boolean, default=True)
    
    # Timestamps
    joined_at = Column(DateTime, default=datetime.utcnow)
    added_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    def __repr__(self):
        return f"<ProjectMember User {self.user_id} in Project {self.project_id}>"
