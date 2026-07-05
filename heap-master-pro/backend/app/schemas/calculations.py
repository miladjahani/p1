"""
Heap Master Pro - Pydantic Schemas for API Request/Response Validation
Comprehensive schemas with validation rules and documentation
"""

from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


# ============= Enums =============

class OreType(str, Enum):
    """Types of copper ore"""
    OXIDE = "oxide"
    SULFIDE = "sulfide"
    MIXED = "mixed"


class UrgencyLevel(str, Enum):
    """Urgency levels for recommendations"""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ControlMode(str, Enum):
    """Control modes for acid dosing"""
    AUTOMATIC = "automatic"
    SEMI_AUTOMATIC = "semi-automatic"
    MANUAL = "manual"


# ============= Recovery Calculation Schemas =============

class RecoveryInput(BaseModel):
    """Input schema for copper recovery calculation"""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "flow_rate": 80.0,
            "acid_conc": 15.0,
            "time_days": 90,
            "ore_grade": 0.7,
            "particle_size": 0.025,
            "ore_type": "oxide",
            "temperature": 25.0
        }
    })
    
    flow_rate: float = Field(80.0, gt=0, description="Irrigation flow rate (L/m²/h)")
    acid_conc: float = Field(15.0, gt=0, description="Sulfuric acid concentration (g/L)")
    time_days: int = Field(90, ge=1, description="Leaching time (days)")
    ore_grade: float = Field(0.7, gt=0, le=100, description="Copper ore grade (%)")
    particle_size: float = Field(0.025, gt=0, description="Particle size (m)")
    ore_type: str = Field("oxide", description="Type of ore (oxide/sulfide/mixed)")
    temperature: float = Field(25.0, ge=-10, le=60, description="Ambient temperature (°C)")


class RecoveryOutput(BaseModel):
    """Output schema for copper recovery calculation"""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "recovery_percent": 87.45,
            "calculation_method": "multivariate_regression_v3",
            "metadata": {
                "model_version": "3.0.0",
                "calibration_date": "2025-01-01",
                "confidence_level": 0.92
            },
            "warnings": []
        }
    })
    
    recovery_percent: float = Field(..., ge=0, le=100, description="Recovery percentage")
    calculation_method: str = "multivariate_regression_v3"
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    warnings: List[str] = Field(default_factory=list, description="Calculation warnings")


# ============= OPEX Calculation Schemas =============

class OPEXInput(BaseModel):
    """Input schema for operational expense calculation"""
    tonnage: float = Field(1000000, gt=0, description="Total tonnage (tons)")
    days: int = Field(365, ge=1, description="Operation days")
    acid_price: float = Field(300, ge=0, description="Sulfuric acid price ($/ton)")
    labor_cost: float = Field(5000, ge=0, description="Monthly labor cost ($)")
    diesel_price: float = Field(1.5, ge=0, description="Diesel price ($/L)")
    electricity_price: float = Field(0.1, ge=0, description="Electricity price ($/kWh)")
    maintenance_factor: float = Field(0.05, ge=0, le=1, description="Maintenance as fraction of direct costs")


class OPEXOutput(BaseModel):
    """Output schema for OPEX calculation"""
    acid_consumption_kg: float
    acid_cost_usd: float
    labor_cost_usd: float
    diesel_cost_usd: float
    electricity_cost_usd: float
    maintenance_cost_usd: float
    overhead_usd: float
    total_opex_usd: float
    opex_per_ton_usd: float
    cost_breakdown_percent: Dict[str, float]


# ============= PLS Calculation Schemas =============

class PLSInput(BaseModel):
    """Input schema for Pregnant Leach Solution calculation"""
    flow_rate: float = Field(80.0, gt=0, description="Irrigation flow rate (L/m²/h)")
    area: float = Field(20000, gt=0, description="Pad surface area (m²)")
    recovery: float = Field(85.0, ge=0, le=100, description="Recovery percentage")
    ore_grade: float = Field(0.7, gt=0, description="Copper ore grade (%)")
    tonnage: float = Field(1700000, gt=0, description="Total tonnage (tons)")
    solution_density: float = Field(1.02, gt=0, description="PLS density (t/m³)")


class PLSOutput(BaseModel):
    """Output schema for PLS calculation"""
    total_flow_m3_day: float
    copper_dissolved_kg_year: float
    cu_concentration_g_L: float
    target_ph: float = 1.8
    annual_cathode_tonnes: float
    solution_density_t_m3: float
    daily_cathode_production_kg: float


# ============= Production Schedule Schemas =============

class ScheduleInput(BaseModel):
    """Input schema for production scheduling"""
    target_cathode: float = Field(50000, gt=0, description="Target cathode production (tons/year)")
    ore_grade: float = Field(0.7, gt=0, description="Copper ore grade (%)")
    recovery: float = Field(85.0, ge=0, le=100, description="Recovery percentage")
    days: int = Field(365, ge=1, description="Operation days")
    ramp_up_period: int = Field(30, ge=0, description="Days to reach full production")
    efficiency_factor: float = Field(0.95, gt=0, le=1, description="Overall equipment efficiency")


class MonthlySchedule(BaseModel):
    """Monthly production schedule item"""
    month: int
    month_name: str
    cathode_tonnes: float
    ore_processed_tonnes: float
    efficiency_applied: float


class ScheduleOutput(BaseModel):
    """Output schema for production schedule"""
    required_ore_tonnes: float
    daily_feed_tonnes: float
    monthly_schedule: List[MonthlySchedule]
    target_achieved: bool
    total_produced_tonnes: float
    target_cathode_tonnes: float
    variance_percent: float


# ============= Pad Volume Calculation Schemas =============

class PadVolumeInput(BaseModel):
    """Input schema for pad volume calculation"""
    L: float = Field(200, gt=0, description="Pad length (m)")
    W: float = Field(100, gt=0, description="Pad width (m)")
    H_top: float = Field(15, ge=0, description="Top height (m)")
    H_bottom: float = Field(0, ge=0, description="Bottom height (m)")
    slope_deg: float = Field(37, ge=0, le=90, description="Wall slope (degrees)")
    terrain_slope_x: Optional[float] = Field(0, description="Terrain slope X (%)")
    terrain_slope_y: Optional[float] = Field(0, description="Terrain slope Y (%)")
    liner_thickness: float = Field(0.002, ge=0, description="Liner thickness (m)")
    freeboard: float = Field(0.5, ge=0, description="Freeboard height (m)")


class PadVolumeOutput(BaseModel):
    """Output schema for pad volume calculation"""
    volume_m3: float
    tonnage: float
    density_t_m3: float = 1.7
    surface_area_m2: float
    total_surface_area_with_slopes_m2: float
    avg_height_m: float
    effective_height_with_freeboard_m: float
    liner_area_m2: float
    terrain_correction_factor: float


# ============= Acid Optimization Schemas =============

class AcidOptimizationInput(BaseModel):
    """Input schema for acid optimization"""
    pls_flow: float = Field(..., gt=0, description="PLS flow rate (m³/h)")
    cu_conc: float = Field(..., ge=0, description="Copper concentration (g/L)")
    target_ph: float = Field(1.8, ge=0, le=14, description="Target pH")
    current_ph: float = Field(..., ge=0, le=14, description="Current pH")
    acid_purity: float = Field(0.98, gt=0, le=1, description="Sulfuric acid purity")
    control_mode: str = Field("automatic", description="Control strategy")


class AcidOptimizationOutput(BaseModel):
    """Output schema for acid optimization"""
    acid_kg_per_hour: float
    acid_tonnes_per_day: float
    ph_adjustment: float
    recommendation: str
    urgency: str
    current_ph: float
    target_ph: float
    in_optimal_range: bool
    control_mode: str
    next_check_hours: int


# ============= Monte Carlo Simulation Schemas =============

class MonteCarloInput(BaseModel):
    """Input schema for Monte Carlo simulation"""
    base_parameters: Dict[str, float] = Field(
        ..., 
        description="Base parameter values for simulation",
        example={"flow_rate": 80, "acid_conc": 15, "time_days": 90, "ore_grade": 0.7}
    )
    n_simulations: Optional[int] = Field(1000, ge=100, le=10000, description="Number of simulations")
    confidence_level: Optional[float] = Field(0.95, ge=0.5, le=0.99, description="Confidence level")


class MonteCarloOutput(BaseModel):
    """Output schema for Monte Carlo simulation"""
    mean_recovery: float
    std_recovery: float
    p5_recovery: float
    p50_recovery: float
    p95_recovery: float
    confidence_interval: List[float]
    n_successful_simulations: int
    n_total_simulations: int


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
    warnings: Optional[List[str]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ============= Pad Management Schemas =============

class PadBase(BaseModel):
    """Base schema for heap leaching pad"""
    name: Optional[str] = Field(None, max_length=100, description="Pad name")
    L: float = Field(..., gt=0, description="Length (m)")
    W: float = Field(..., gt=0, description="Width (m)")
    H: float = Field(..., gt=0, description="Height (m)")
    x: float = Field(0, description="X position")
    z: float = Field(0, description="Z position")
    slope_deg: float = Field(37, ge=0, le=90, description="Wall slope (degrees)")
    
    # Boundary conditions
    bounds: Optional[Dict[str, str]] = None
    
    # Irrigation
    lateral_spacing: float = Field(1.0, gt=0, description="Lateral spacing (m)")
    emitter_spacing: float = Field(0.5, gt=0, description="Emitter spacing (m)")
    emitter_flow_rate: float = Field(4.0, gt=0, description="Emitter flow rate (mL/min)")
    
    # Metallurgical parameters
    ore_grade: float = Field(0.7, gt=0, description="Copper grade (%)")
    recovery: float = Field(85.0, ge=0, le=100, description="Recovery (%)")
    density: float = Field(1.7, gt=0, description="Density (t/m³)")


class PadCreate(PadBase):
    """Schema for creating a new pad"""
    pass


class PadUpdate(BaseModel):
    """Schema for updating an existing pad"""
    name: Optional[str] = Field(None, max_length=100)
    L: Optional[float] = Field(None, gt=0)
    W: Optional[float] = Field(None, gt=0)
    H: Optional[float] = Field(None, gt=0)
    x: Optional[float] = None
    z: Optional[float] = None
    slope_deg: Optional[float] = Field(None, ge=0, le=90)
    bounds: Optional[Dict[str, str]] = None
    lateral_spacing: Optional[float] = Field(None, gt=0)
    emitter_spacing: Optional[float] = Field(None, gt=0)
    emitter_flow_rate: Optional[float] = Field(None, gt=0)
    ore_grade: Optional[float] = Field(None, gt=0)
    recovery: Optional[float] = Field(None, ge=0, le=100)
    density: Optional[float] = Field(None, gt=0)


class PadResponse(PadBase):
    """Schema for pad response with calculated values"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    volume_m3: float
    tonnage: float
    recoverable_copper_tonnes: float
    created_at: datetime
    updated_at: datetime


class PadListResponse(BaseModel):
    """Schema for paginated pad list response"""
    success: bool
    data: List[PadResponse]
    total: int
    skip: int
    limit: int
