"""
Engineering calculation service for heap leach pads.
Implements prismoidal volume calculations, irrigation design, and metallurgical estimates.
"""
import math
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime


@dataclass
class PadGeometry:
    """Pad geometry parameters."""
    length: float  # meters
    width: float   # meters
    height: float  # meters
    slope_degrees: float
    terrain_slope_x: float = 0.0  # %
    terrain_slope_y: float = 0.0  # %
    

@dataclass
class IrrigationParams:
    """Irrigation system parameters."""
    emitter_flow_rate: float  # mL/min
    lateral_spacing: float    # cm
    emitter_spacing: float    # cm
    

@dataclass
class MetallurgicalParams:
    """Metallurgical parameters."""
    copper_grade: float       # %
    recovery_rate: float      # %
    density: float            # t/m³
    acid_consumption: float = 15.0  # kg/ton


@dataclass
class CalculationResult:
    """Complete calculation results."""
    # Volume calculations
    volume: float                    # m³
    base_area: float                 # m²
    top_area: float                  # m²
    
    # Mass and metal
    tonnage: float                   # tons
    recoverable_copper: float        # tons
    
    # Acid and water
    acid_consumption: float          # tons
    total_flow_rate: float           # m³/hour
    
    # Irrigation design
    emitter_count: int
    collector_length: float          # meters
    lateral_length: float            # meters
    
    # Corner heights (considering terrain slope)
    corner_heights: Dict[str, float]
    
    # Hip lengths
    hip_lengths: Dict[str, float]
    
    # Timestamp
    calculated_at: datetime


class EngineeringCalculator:
    """
    Professional engineering calculator for heap leach pads.
    Implements industry-standard formulas and methods.
    """
    
    def __init__(self):
        self.gravity = 9.81  # m/s²
    
    def calculate_prismoidal_volume(
        self,
        geometry: PadGeometry
    ) -> Tuple[float, float, float]:
        """
        Calculate volume using the prismoidal formula.
        
        V = (H / 6) * (A_base + A_top + 4 * A_mid)
        
        Args:
            geometry: Pad geometry parameters
            
        Returns:
            Tuple of (volume, base_area, top_area)
        """
        L = geometry.length
        W = geometry.width
        H = geometry.height
        slope_rad = math.radians(geometry.slope_degrees)
        
        # Base area
        A_base = L * W
        
        # Calculate horizontal offset due to slope
        horizontal_offset = H / math.tan(slope_rad) if slope_rad > 0 else 0
        
        # Top dimensions (reduced by slope on each side)
        L_top = max(0, L - 2 * horizontal_offset)
        W_top = max(0, W - 2 * horizontal_offset)
        A_top = L_top * W_top
        
        # Mid-section area
        L_mid = (L + L_top) / 2
        W_mid = (W + W_top) / 2
        A_mid = L_mid * W_mid
        
        # Prismoidal volume
        volume = (H / 6) * (A_base + A_top + 4 * A_mid)
        
        return volume, A_base, A_top
    
    def calculate_corner_heights(
        self,
        geometry: PadGeometry,
        start_x: float = 0.0,
        start_z: float = 0.0
    ) -> Dict[str, float]:
        """
        Calculate heights at all four corners considering terrain slope.
        
        Args:
            geometry: Pad geometry parameters
            start_x: X coordinate of starting corner
            start_z: Z coordinate of starting corner
            
        Returns:
            Dictionary with heights at FL, FR, BL, BR corners
        """
        H = geometry.height
        sx = geometry.terrain_slope_x / 100  # Convert % to ratio
        sy = geometry.terrain_slope_y / 100
        
        # Terrain elevation changes across pad
        delta_elevation_x = sx * geometry.length
        delta_elevation_z = sy * geometry.width
        
        # Corner heights (relative to base height)
        # FL = Front-Left, FR = Front-Right, BL = Back-Left, BR = Back-Right
        corners = {
            "FL": H,  # Reference corner
            "FR": H - delta_elevation_x,  # Right side elevation change
            "BL": H - delta_elevation_z,  # Back side elevation change
            "BR": H - delta_elevation_x - delta_elevation_z  # Diagonal
        }
        
        return corners
    
    def calculate_hip_lengths(
        self,
        geometry: PadGeometry,
        corner_heights: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Calculate sloped edge (hip) lengths.
        
        Args:
            geometry: Pad geometry parameters
            corner_heights: Heights at corners
            
        Returns:
            Dictionary with hip lengths for each edge
        """
        slope_rad = math.radians(geometry.slope_degrees)
        
        # Horizontal run for each hip
        horizontal_run = geometry.height / math.tan(slope_rad) if slope_rad > 0 else 0
        
        # Hip lengths (hypotenuse of triangle)
        hips = {}
        for corner, height in corner_heights.items():
            # Simplified: assume similar slope for all edges
            hip_length = math.sqrt(height**2 + horizontal_run**2)
            hips[f"hip_{corner.lower()}"] = hip_length
        
        return hips
    
    def calculate_irrigation(
        self,
        geometry: PadGeometry,
        irrigation: IrrigationParams,
        base_area: float
    ) -> Dict:
        """
        Design irrigation system parameters.
        
        Args:
            geometry: Pad geometry parameters
            irrigation: Irrigation parameters
            base_area: Base area of pad
            
        Returns:
            Dictionary with irrigation design parameters
        """
        L = geometry.length
        W = geometry.width
        
        # Convert spacings to meters
        lat_spacing_m = irrigation.lateral_spacing / 100
        emit_spacing_m = irrigation.emitter_spacing / 100
        
        # Number of laterals
        num_laterals = int(W / lat_spacing_m) + 1
        
        # Emitters per lateral
        emitters_per_lateral = int(L / emit_spacing_m) + 1
        
        # Total emitters
        total_emitters = num_laterals * emitters_per_lateral
        
        # Total flow rate
        # Flow per emitter (mL/min) -> m³/hour
        flow_per_emitter_m3h = (irrigation.emitter_flow_rate / 1000) * 60 / 1000
        total_flow_rate = total_emitters * flow_per_emitter_m3h
        
        # Pipe lengths
        collector_length = L  # Main collector along length
        lateral_length = num_laterals * W  # Total lateral pipe length
        
        return {
            "emitter_count": total_emitters,
            "num_laterals": num_laterals,
            "emitters_per_lateral": emitters_per_lateral,
            "total_flow_rate": round(total_flow_rate, 2),  # m³/hour
            "collector_length": round(collector_length, 2),  # meters
            "lateral_length": round(lateral_length, 2),  # meters
        }
    
    def calculate_metallurgical(
        self,
        volume: float,
        metallurgy: MetallurgicalParams
    ) -> Dict:
        """
        Calculate metallurgical estimates.
        
        Args:
            volume: Pad volume in m³
            metallurgy: Metallurgical parameters
            
        Returns:
            Dictionary with metallurgical calculations
        """
        # Tonnage
        tonnage = volume * metallurgy.density
        
        # Recoverable copper
        # Grade (%) * Tonnage * Recovery (%)
        recoverable_cu = tonnage * (metallurgy.copper_grade / 100) * (metallurgy.recovery_rate / 100)
        
        # Acid consumption
        # Acid (kg/ton) * Tonnage / 1000 -> tons
        acid_tons = (metallurgy.acid_consumption * tonnage) / 1000
        
        return {
            "tonnage": round(tonnage, 2),
            "recoverable_copper": round(recoverable_cu, 2),
            "acid_consumption": round(acid_tons, 2),
        }
    
    def calculate_pad(
        self,
        geometry: PadGeometry,
        irrigation: IrrigationParams,
        metallurgy: MetallurgicalParams,
        start_x: float = 0.0,
        start_z: float = 0.0
    ) -> CalculationResult:
        """
        Perform complete pad calculation.
        
        Args:
            geometry: Pad geometry
            irrigation: Irrigation parameters
            metallurgy: Metallurgical parameters
            start_x: Starting X coordinate
            start_z: Starting Z coordinate
            
        Returns:
            Complete calculation results
        """
        # Volume calculations
        volume, base_area, top_area = self.calculate_prismoidal_volume(geometry)
        
        # Corner heights
        corner_heights = self.calculate_corner_heights(geometry, start_x, start_z)
        
        # Hip lengths
        hip_lengths = self.calculate_hip_lengths(geometry, corner_heights)
        
        # Irrigation design
        irrigation_results = self.calculate_irrigation(geometry, irrigation, base_area)
        
        # Metallurgical calculations
        metal_results = self.calculate_metallurgical(volume, metallurgy)
        
        return CalculationResult(
            volume=round(volume, 2),
            base_area=round(base_area, 2),
            top_area=round(top_area, 2),
            tonnage=metal_results["tonnage"],
            recoverable_copper=metal_results["recoverable_copper"],
            acid_consumption=metal_results["acid_consumption"],
            total_flow_rate=irrigation_results["total_flow_rate"],
            emitter_count=irrigation_results["emitter_count"],
            collector_length=irrigation_results["collector_length"],
            lateral_length=irrigation_results["lateral_length"],
            corner_heights={k: round(v, 2) for k, v in corner_heights.items()},
            hip_lengths={k: round(v, 2) for k, v in hip_lengths.items()},
            calculated_at=datetime.utcnow()
        )
    
    def calculate_multiple_pads(
        self,
        pads: List[Dict]
    ) -> List[CalculationResult]:
        """
        Calculate multiple pads efficiently.
        
        Args:
            pads: List of pad parameter dictionaries
            
        Returns:
            List of calculation results
        """
        results = []
        for pad_data in pads:
            geometry = PadGeometry(
                length=pad_data["length"],
                width=pad_data["width"],
                height=pad_data["height"],
                slope_degrees=pad_data.get("slope_degrees", 37.0),
                terrain_slope_x=pad_data.get("terrain_slope_x", 0.0),
                terrain_slope_y=pad_data.get("terrain_slope_y", 0.0),
            )
            
            irrigation = IrrigationParams(
                emitter_flow_rate=pad_data.get("emitter_flow_rate", 80.0),
                lateral_spacing=pad_data.get("lateral_spacing", 50.0),
                emitter_spacing=pad_data.get("emitter_spacing", 40.0),
            )
            
            metallurgy = MetallurgicalParams(
                copper_grade=pad_data.get("copper_grade", 0.7),
                recovery_rate=pad_data.get("recovery_rate", 80.0),
                density=pad_data.get("density", 1.7),
                acid_consumption=pad_data.get("acid_consumption", 15.0),
            )
            
            result = self.calculate_pad(
                geometry=geometry,
                irrigation=irrigation,
                metallurgy=metallurgy,
                start_x=pad_data.get("start_x", 0.0),
                start_z=pad_data.get("start_z", 0.0),
            )
            results.append(result)
        
        return results
