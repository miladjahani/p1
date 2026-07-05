"""
Heap Master Pro - Pydantic Schemas for API Request/Response Validation
Based on the original metallurgy_engine.py calculations
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any
from datetime import datetime


# ============= Recovery Calculation Schemas =============

class RecoveryInput(BaseModel):
    """Input schema for copper recovery calculation"""
    flow_rate: float = Field(80.0, ge=0, description="Irrigation flow rate (L/m²/h)")
    acid_conc: float = Field(15.0, ge=0, description="Sulfuric acid concentration (g/L)")
    time_days: int = Field(90, ge=1, description="Leaching time (days)")
    ore_grade: float = Field(0.7, ge=0, le=100, description="Copper ore grade (%)")
    particle_size: float = Field(0.025, ge=0, description="Particle size (m)")


class RecoveryOutput(BaseModel):
    """Output schema for copper recovery calculation"""
    recovery_percent: float = Field(..., ge=0, le=100, description="Recovery percentage")
    calculation_method: str = "multivariate_regression"
    

# ============= OPEX Calculation Schemas =============

class OPEXInput(BaseModel):
    """Input schema for operational expense calculation"""
    tonnage: float = Field(1000000, ge=0, description="Total tonnage (tons)")
    days: int = Field(365, ge=1, description="Operation days")
    acid_price: float = Field(300, ge=0, description="Sulfuric acid price ($/ton)")
    labor_cost: float = Field(5000, ge=0, description="Monthly labor cost ($)")
    diesel_price: float = Field(1.5, ge=0, description="Diesel price ($/L)")


class OPEXOutput(BaseModel):
    """Output schema for OPEX calculation"""
    acid_consumption_kg: float
    acid_cost_usd: float
    labor_cost_usd: float
    diesel_cost_usd: float
    overhead_usd: float
    total_opex_usd: float
    opex_per_ton_usd: float


# ============= PLS Calculation Schemas =============

class PLSInput(BaseModel):
    """Input schema for Pregnant Leach Solution calculation"""
    flow_rate: float = Field(80.0, ge=0, description="Irrigation flow rate (L/m²/h)")
    area: float = Field(20000, ge=0, description="Pad surface area (m²)")
    recovery: float = Field(85.0, ge=0, le=100, description="Recovery percentage")
    ore_grade: float = Field(0.7, ge=0, description="Copper ore grade (%)")
    tonnage: float = Field(1700000, ge=0, description="Total tonnage (tons)")


class PLSOutput(BaseModel):
    """Output schema for PLS calculation"""
    total_flow_m3_day: float
    copper_dissolved_kg_year: float
    cu_concentration_g_L: float
    target_ph: float = 1.8
    annual_cathode_tonnes: float


# ============= Production Schedule Schemas =============

class ScheduleInput(BaseModel):
    """Input schema for production scheduling"""
    target_cathode: float = Field(50000, ge=0, description="Target cathode production (tons/year)")
    ore_grade: float = Field(0.7, ge=0, description="Copper ore grade (%)")
    recovery: float = Field(85.0, ge=0, le=100, description="Recovery percentage")
    days: int = Field(365, ge=1, description="Operation days")


class MonthlySchedule(BaseModel):
    """Monthly production schedule item"""
    month: int
    cathode_tonnes: float
    ore_processed_tonnes: float


class ScheduleOutput(BaseModel):
    """Output schema for production schedule"""
    required_ore_tonnes: float
    daily_feed_tonnes: float
    monthly_schedule: List[MonthlySchedule]
    target_achieved: bool


# ============= Pad Volume Calculation Schemas =============

class PadVolumeInput(BaseModel):
    """Input schema for pad volume calculation"""
    L: float = Field(200, ge=0, description="Pad length (m)")
    W: float = Field(100, ge=0, description="Pad width (m)")
    H_top: float = Field(15, ge=0, description="Top height (m)")
    H_bottom: float = Field(0, ge=0, description="Bottom height (m)")
    slope_deg: float = Field(37, ge=0, le=90, description="Wall slope (degrees)")
    terrain_slope_x: float = Field(0, description="Terrain slope X (%)")
    terrain_slope_y: float = Field(0, description="Terrain slope Y (%)")


class PadVolumeOutput(BaseModel):
    """Output schema for pad volume calculation"""
    volume_m3: float
    tonnage: float
    density_t_m3: float = 1.7
    surface_area_m2: float
    avg_height_m: float


# ============= Acid Optimization Schemas =============

class AcidOptimizationInput(BaseModel):
    """Input schema for acid optimization"""
    pls_flow: float = Field(ge=0, description="PLS flow rate (m³/h)")
    cu_conc: float = Field(ge=0, description="Copper concentration (g/L)")
    target_ph: float = Field(1.8, ge=0, le=14, description="Target pH")
    current_ph: float = Field(ge=0, le=14, description="Current pH")


class AcidOptimizationOutput(BaseModel):
    """Output schema for acid optimization"""
    acid_kg_per_hour: float
    acid_tonnes_per_day: float
    ph_adjustment: float
    recommendation: str


# ============= Combined Calculation Request/Response =============

class CalculationRequest(BaseModel):
    """Unified calculation request"""
    recovery: Optional[RecoveryInput] = None
    opex: Optional[OPEXInput] = None
    pls: Optional[PLSInput] = None
    schedule: Optional[ScheduleInput] = None
    volume: Optional[PadVolumeInput] = None
    acid_optimization: Optional[AcidOptimizationInput] = None


class CalculationResponse(BaseModel):
    """Unified calculation response"""
    success: bool
    results: Dict[str, Any]
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ============= Pad Management Schemas =============

class PadBase(BaseModel):
    """Base schema for heap leaching pad"""
    name: Optional[str] = None
    L: float = Field(ge=0, description="Length (m)")
    W: float = Field(ge=0, description="Width (m)")
    H: float = Field(ge=0, description="Height (m)")
    x: float = Field(0, description="X position")
    z: float = Field(0, description="Z position")
    slope_deg: float = Field(37, ge=0, le=90, description="Wall slope (degrees)")
    
    # Boundary conditions
    bounds: Optional[Dict[str, str]] = None
    
    # Irrigation
    lateral_spacing: float = Field(1.0, ge=0, description="Lateral spacing (m)")
    emitter_spacing: float = Field(0.5, ge=0, description="Emitter spacing (m)")
    emitter_flow_rate: float = Field(4.0, ge=0, description="Emitter flow rate (mL/min)")
    
    # Metallurgical parameters
    ore_grade: float = Field(0.7, ge=0, description="Copper grade (%)")
    recovery: float = Field(85.0, ge=0, le=100, description="Recovery (%)")
    density: float = Field(1.7, ge=0, description="Density (t/m³)")


class PadCreate(PadBase):
    """Schema for creating a new pad"""
    pass


class PadUpdate(BaseModel):
    """Schema for updating an existing pad"""
    name: Optional[str] = None
    L: Optional[float] = None
    W: Optional[float] = None
    H: Optional[float] = None
    x: Optional[float] = None
    z: Optional[float] = None
    slope_deg: Optional[float] = None
    bounds: Optional[Dict[str, str]] = None
    lateral_spacing: Optional[float] = None
    emitter_spacing: Optional[float] = None
    emitter_flow_rate: Optional[float] = None
    ore_grade: Optional[float] = None
    recovery: Optional[float] = None
    density: Optional[float] = None


class PadResponse(PadBase):
    """Schema for pad response with calculated values"""
    id: int
    volume_m3: float
    tonnage: float
    recoverable_copper_tonnes: float
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
