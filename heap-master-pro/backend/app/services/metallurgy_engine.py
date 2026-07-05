"""
Heap Master Pro - Professional Metallurgical Engine
Refactored from original metallurgy_engine.py with modern Python patterns
"""

import numpy as np
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class MetallurgicalConstants:
    """Constant parameters for metallurgical calculations"""
    BASE_RECOVERY: float = 0.85
    ACID_CONSUMPTION_BASE: float = 5.0  # kg/ton
    EVAPORATION_RATE: float = 0.003  # m/day
    ORE_DENSITY: float = 1.7  # ton/m³
    BUFFER_CAPACITY: float = 0.5  # mol/L per pH unit


class HeapLeachCalculator:
    """
    Advanced heap leaching simulation engine.
    
    Provides calculations for:
    - Copper recovery using multivariate regression
    - Operational expenses (OPEX)
    - Pregnant Leach Solution (PLS) properties
    - Production scheduling
    - Pad volume with terrain correction
    - Acid optimization for pH control
    
    All methods are based on empirical models calibrated for 
    oxide copper ore leaching operations.
    """
    
    def __init__(self, constants: Optional[MetallurgicalConstants] = None):
        """Initialize calculator with optional custom constants"""
        self.constants = constants or MetallurgicalConstants()
    
    def calculate_recovery(
        self,
        flow_rate: float,
        acid_conc: float,
        time_days: int,
        ore_grade: float,
        particle_size: float = 0.025
    ) -> float:
        """
        Calculate copper recovery using multivariate regression.
        
        This empirical model is calibrated for oxide copper ores and considers:
        - Irrigation flow rate (logarithmic effect)
        - Acid concentration (logarithmic effect)
        - Leaching time (square root with diminishing returns)
        - Ore grade (higher grade = slightly lower recovery due to locking)
        - Particle size (finer = better recovery but risk of agglomeration)
        
        Args:
            flow_rate: Irrigation flow rate (L/m²/h)
            acid_conc: Sulfuric acid concentration (g/L)
            time_days: Leaching time (days)
            ore_grade: Copper ore grade (%)
            particle_size: Particle size (m), default 25mm
            
        Returns:
            Recovery percentage (clamped between 70-95%)
        """
        # Normalize inputs using appropriate transformations
        flow_norm = np.log(flow_rate / 50 + 1)
        acid_norm = np.log(acid_conc / 10 + 1)
        time_norm = np.sqrt(time_days / 30)
        
        # Grade factor: higher grade slightly reduces recovery
        grade_factor = 1.0 - 0.02 * (ore_grade - 0.7)
        
        # Size factor: finer particles improve recovery
        size_factor = 1.0 - 2.0 * (particle_size - 0.025)
        
        # Multivariate regression model
        recovery = (
            self.constants.BASE_RECOVERY * 100 +
            8.5 * flow_norm +
            6.2 * acid_norm +
            12.0 * time_norm -
            0.15 * time_norm**2 +  # Diminishing returns after optimal time
            3.0 * grade_factor +
            2.5 * size_factor
        )
        
        return float(np.clip(recovery, 70, 95))
    
    def calculate_opex(
        self,
        tonnage: float,
        days: int,
        acid_price: float = 300,
        labor_cost: float = 5000,
        diesel_price: float = 1.5
    ) -> Dict[str, float]:
        """
        Calculate operational expenses (OPEX) breakdown.
        
        Args:
            tonnage: Total ore tonnage (tons)
            days: Operation duration (days)
            acid_price: Sulfuric acid price ($/ton)
            labor_cost: Monthly labor cost ($)
            diesel_price: Diesel price ($/L)
            
        Returns:
            Dictionary with detailed cost breakdown
        """
        # Acid consumption and cost
        acid_consumption_kg = tonnage * self.constants.ACID_CONSUMPTION_BASE
        acid_cost_usd = (acid_consumption_kg / 1000) * acid_price
        
        # Labor cost
        labor_months = days / 30
        labor_total_usd = labor_cost * labor_months
        
        # Diesel consumption (equipment and pumps)
        diesel_consumption_l = tonnage * 0.3
        diesel_cost_usd = diesel_consumption_l * diesel_price
        
        # Overhead (15% of direct costs)
        direct_costs = acid_cost_usd + labor_total_usd + diesel_cost_usd
        overhead_usd = direct_costs * 0.15
        
        total_opex_usd = direct_costs + overhead_usd
        
        return {
            'acid_consumption_kg': round(acid_consumption_kg, 2),
            'acid_cost_usd': round(acid_cost_usd, 2),
            'labor_cost_usd': round(labor_total_usd, 2),
            'diesel_cost_usd': round(diesel_cost_usd, 2),
            'overhead_usd': round(overhead_usd, 2),
            'total_opex_usd': round(total_opex_usd, 2),
            'opex_per_ton_usd': round(total_opex_usd / max(tonnage, 1), 2)
        }
    
    def calculate_pls(
        self,
        flow_rate: float,
        area: float,
        recovery: float,
        ore_grade: float,
        tonnage: float
    ) -> Dict[str, float]:
        """
        Calculate Pregnant Leach Solution (PLS) properties.
        
        Args:
            flow_rate: Irrigation flow rate (L/m²/h)
            area: Pad surface area (m²)
            recovery: Copper recovery (%)
            ore_grade: Copper ore grade (%)
            tonnage: Total ore tonnage (tons)
            
        Returns:
            Dictionary with PLS characteristics
        """
        # Total flow rate (m³/day)
        total_flow_m3_day = flow_rate * area * 24 / 1000
        
        # Dissolved copper (kg/year, assuming uniform distribution)
        copper_dissolved_kg_year = tonnage * (ore_grade / 100) * (recovery / 100)
        
        # Copper concentration in PLS (g/L)
        daily_flow = total_flow_m3_day * 365  # Annual flow
        cu_concentration_g_L = (copper_dissolved_kg_year * 1000) / (daily_flow * 1000)
        
        # Target pH for copper heap leaching (typically 1.5-2.0)
        target_ph = 1.8
        
        return {
            'total_flow_m3_day': round(total_flow_m3_day, 2),
            'copper_dissolved_kg_year': round(copper_dissolved_kg_year, 2),
            'cu_concentration_g_L': round(cu_concentration_g_L, 3),
            'target_ph': target_ph,
            'annual_cathode_tonnes': round(copper_dissolved_kg_year / 1000, 2)
        }
    
    def production_schedule(
        self,
        target_cathode: float,
        ore_grade: float,
        recovery: float,
        days: int = 365
    ) -> Dict[str, Any]:
        """
        Generate production schedule to meet cathode target.
        
        Args:
            target_cathode: Target cathode production (tons/year)
            ore_grade: Copper ore grade (%)
            recovery: Expected recovery (%)
            days: Operation days
            
        Returns:
            Production schedule with monthly breakdown
        """
        # Required ore tonnage
        required_ore_kg = (target_cathode * 1000) / ((ore_grade / 100) * (recovery / 100))
        required_ore_tonnes = required_ore_kg / 1000
        
        # Daily feed rate
        daily_feed_tonnes = required_ore_tonnes / days
        
        # Monthly production schedule
        monthly_schedule = []
        total_produced = 0
        
        for month in range(1, 13):
            month_days = 30
            ore_processed = daily_feed_tonnes * month_days
            cathode_produced = (
                ore_processed * 
                (ore_grade / 100) * 
                (recovery / 100)
            )
            
            monthly_schedule.append({
                'month': month,
                'cathode_tonnes': round(cathode_produced, 2),
                'ore_processed_tonnes': round(ore_processed, 2)
            })
            total_produced += cathode_produced
        
        return {
            'required_ore_tonnes': round(required_ore_tonnes, 2),
            'daily_feed_tonnes': round(daily_feed_tonnes, 2),
            'monthly_schedule': monthly_schedule,
            'target_achieved': total_produced >= target_cathode
        }
    
    def pad_volume_calculation(
        self,
        L: float,
        W: float,
        H_top: float,
        H_bottom: float,
        slope_deg: float,
        terrain_slope_x: float = 0,
        terrain_slope_y: float = 0
    ) -> Dict[str, float]:
        """
        Calculate pad volume and tonnage with terrain correction.
        
        Uses trapezoidal method with corrections for:
        - Wall slopes
        - Terrain gradients in X and Y directions
        
        Args:
            L: Pad length (m)
            W: Pad width (m)
            H_top: Height at top (m)
            H_bottom: Height at bottom (m)
            slope_deg: Wall slope angle (degrees)
            terrain_slope_x: Terrain slope in X direction (%)
            terrain_slope_y: Terrain slope in Y direction (%)
            
        Returns:
            Volume and tonnage calculations
        """
        slope_rad = np.radians(slope_deg)
        terrain_x_rad = np.arctan(terrain_slope_x / 100)
        terrain_y_rad = np.arctan(terrain_slope_y / 100)
        
        avg_height = (H_top + H_bottom) / 2
        
        # Terrain correction factor
        terrain_correction = 1.0 + (abs(terrain_slope_x) + abs(terrain_slope_y)) / 200
        
        # Base volume (rectangular prism)
        base_volume = L * W * avg_height
        
        # Volume reduction due to wall slopes
        slope_reduction = (L + W) * (avg_height ** 2) / (2 * np.tan(slope_rad))
        
        # Net volume
        net_volume = (base_volume - slope_reduction) * terrain_correction
        
        # Tonnage calculation
        tonnage = net_volume * self.constants.ORE_DENSITY
        
        return {
            'volume_m3': round(net_volume, 2),
            'tonnage': round(tonnage, 2),
            'density_t_m3': self.constants.ORE_DENSITY,
            'surface_area_m2': round(L * W, 2),
            'avg_height_m': round(avg_height, 2)
        }
    
    def optimize_acid_addition(
        self,
        pls_flow: float,
        cu_conc: float,
        target_ph: float,
        current_ph: float
    ) -> Dict[str, Any]:
        """
        Optimize acid addition for pH control.
        
        Args:
            pls_flow: PLS flow rate (m³/h)
            cu_conc: Copper concentration (g/L)
            target_ph: Target pH value
            current_ph: Current pH value
            
        Returns:
            Acid dosing recommendations
        """
        ph_diff = target_ph - current_ph
        
        # Acid requirement calculation
        acid_mol_h = abs(ph_diff) * self.constants.BUFFER_CAPACITY * pls_flow * 1000
        
        # Convert to kg of 98% sulfuric acid
        acid_kg_h = acid_mol_h * 98.08 / 1000 / 0.98
        
        # Recommendation
        if ph_diff < 0:
            recommendation = "افزایش اسید (Increase acid)"
        elif ph_diff > 0:
            recommendation = "کاهش اسید (Decrease acid)"
        else:
            recommendation = "pH بهینه است (pH is optimal)"
        
        return {
            'acid_kg_per_hour': round(acid_kg_h, 2),
            'acid_tonnes_per_day': round(acid_kg_h * 24 / 1000, 2),
            'ph_adjustment': round(ph_diff, 2),
            'recommendation': recommendation
        }
