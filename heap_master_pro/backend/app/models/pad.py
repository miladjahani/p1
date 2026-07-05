"""
Pad model for heap leach pad data and calculations.
"""
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, JSON, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Pad(Base):
    """Heap leach pad model with geometry and configuration."""
    
    __tablename__ = "pads"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    
    # Geometry
    length = Column(Float, nullable=False)  # Length (L) in meters
    width = Column(Float, nullable=False)   # Width (W) in meters
    height = Column(Float, nullable=False)  # Height (H) in meters
    start_x = Column(Float, default=0.0)    # X coordinate
    start_z = Column(Float, default=0.0)    # Z coordinate
    
    # Lift/Layer information
    lift_number = Column(Integer, default=1)
    parent_pad_id = Column(Integer, ForeignKey("pads.id"), nullable=True)
    
    # Slope and boundaries
    slope_degrees = Column(Float, default=37.0)
    terrain_slope_x = Column(Float, default=-2.0)  # Terrain slope X%
    terrain_slope_y = Column(Float, default=1.0)   # Terrain slope Y%
    
    # Boundary types (free, wall, attach)
    boundary_left = Column(String(20), default="free")
    boundary_right = Column(String(20), default="free")
    boundary_front = Column(String(20), default="free")
    boundary_back = Column(String(20), default="free")
    
    # Irrigation system
    emitter_flow_rate = Column(Float, default=80.0)  # mL/min
    lateral_spacing = Column(Float, default=50.0)    # cm
    emitter_spacing = Column(Float, default=40.0)    # cm
    
    # Metallurgical parameters
    copper_grade = Column(Float, default=0.7)  # %
    recovery_rate = Column(Float, default=80.0)  # %
    density = Column(Float, default=1.7)  # t/m³
    
    # Project association
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    project = relationship("Project", back_populates="pads")
    
    # Calculations cache
    calculated_volume = Column(Float, nullable=True)
    calculated_tonnage = Column(Float, nullable=True)
    calculated_copper = Column(Float, nullable=True)
    calculated_acid = Column(Float, nullable=True)
    last_calculation = Column(DateTime, nullable=True)
    
    # Metadata
    color = Column(String(20), default="#b45309")  # 3D visualization color
    is_active = Column(Boolean, default=True)
    notes = Column(String(1000), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    calculations = relationship("PadCalculation", back_populates="pad", cascade="all, delete-orphan")
    creator = relationship("User")
    parent_pad = relationship("Pad", remote_side=[id], backref="child_pads")
    
    def __repr__(self):
        return f"<Pad {self.name} (Lift {self.lift_number})>"
    
    @property
    def base_area(self) -> float:
        """Calculate base area in square meters."""
        return self.length * self.width
    
    @property
    def top_area(self) -> float:
        """Calculate top area considering slopes."""
        # Simplified calculation - actual implementation would consider slopes
        slope_factor = 1 - (2 * self.height / (self.length + self.width)) * (1 / self.slope_degrees)
        return max(0, self.base_area * slope_factor)


class PadCalculation(Base):
    """Historical calculation records for pads."""
    
    __tablename__ = "pad_calculations"
    
    id = Column(Integer, primary_key=True, index=True)
    pad_id = Column(Integer, ForeignKey("pads.id"), nullable=False)
    pad = relationship("Pad", back_populates="calculations")
    
    # Calculation results
    volume = Column(Float, nullable=False)  # m³
    tonnage = Column(Float, nullable=False)  # tons
    recoverable_copper = Column(Float, nullable=False)  # tons
    acid_consumption = Column(Float, nullable=False)  # tons
    total_flow_rate = Column(Float, nullable=False)  # m³/hour
    emitter_count = Column(Integer, nullable=False)
    collector_length = Column(Float, nullable=False)  # meters
    lateral_length = Column(Float, nullable=False)  # meters
    
    # Corner heights
    corner_fl = Column(Float)  # Front-Left
    corner_fr = Column(Float)  # Front-Right
    corner_bl = Column(Float)  # Back-Left
    corner_br = Column(Float)  # Back-Right
    
    # Hip lengths
    hip_fl = Column(Float)
    hip_fr = Column(Float)
    hip_bl = Column(Float)
    hip_br = Column(Float)
    
    # Parameters used
    parameters = Column(JSON, nullable=True)  # Store input parameters as JSON
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    def __repr__(self):
        return f"<PadCalculation {self.id} for Pad {self.pad_id}>"
