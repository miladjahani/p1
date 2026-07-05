"""
Heap Master Pro - API Routes for Metallurgical Calculations
RESTful API with comprehensive error handling and validation
"""

from fastapi import APIRouter, HTTPException, status, BackgroundTasks
from typing import Dict, Any, Optional
import logging

from app.schemas.calculations import (
    RecoveryInput,
    RecoveryOutput,
    OPEXInput,
    OPEXOutput,
    PLSInput,
    PLSOutput,
    ScheduleInput,
    ScheduleOutput,
    PadVolumeInput,
    PadVolumeOutput,
    AcidOptimizationInput,
    AcidOptimizationOutput,
    CalculationRequest,
    CalculationResponse,
    MonteCarloInput,
    MonteCarloOutput,
)
from app.services.metallurgy_engine import HeapLeachCalculator, OreType, CalculationResult

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/calculate", tags=["calculations"])

# Initialize calculator instance (singleton pattern)
calculator = HeapLeachCalculator()


def _handle_calculation_result(result: CalculationResult, operation: str):
    """Helper function to handle calculation results consistently"""
    if not result.success:
        logger.error(f"{operation} failed: {result.errors}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "operation": operation,
                "errors": result.errors,
                "warnings": result.warnings
            }
        )
    
    if result.warnings:
        logger.warning(f"{operation} completed with warnings: {result.warnings}")
    
    return result.data


@router.post("/recovery", response_model=RecoveryOutput, summary="Calculate Copper Recovery")
async def calculate_recovery(input_data: RecoveryInput) -> RecoveryOutput:
    """
    Calculate copper recovery percentage using advanced multivariate regression.
    
    This endpoint computes the expected copper recovery based on:
    - Irrigation flow rate
    - Acid concentration  
    - Leaching time
    - Ore grade
    - Particle size
    - Ore type (oxide/sulfide/mixed)
    - Temperature
    
    **Example:**
    ```json
    {
        "flow_rate": 80,
        "acid_conc": 15,
        "time_days": 90,
        "ore_grade": 0.7,
        "particle_size": 0.025,
        "ore_type": "oxide",
        "temperature": 25
    }
    ```
    """
    try:
        # Convert ore_type string to enum
        ore_type = OreType(input_data.ore_type) if hasattr(input_data, 'ore_type') else OreType.OXIDE
        
        result = calculator.calculate_recovery(
            flow_rate=input_data.flow_rate,
            acid_conc=input_data.acid_conc,
            time_days=input_data.time_days,
            ore_grade=input_data.ore_grade,
            particle_size=input_data.particle_size,
            ore_type=ore_type,
            temperature=getattr(input_data, 'temperature', 25.0)
        )
        
        data = _handle_calculation_result(result, "Recovery calculation")
        
        return RecoveryOutput(
            recovery_percent=data["recovery_percent"],
            calculation_method=data["calculation_method"],
            metadata=data.get("metadata", {}),
            warnings=result.warnings
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid input parameters: {str(e)}"
        )
    except Exception as e:
        logger.exception("Unexpected error in recovery calculation")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Calculation error: {str(e)}"
        )


@router.post("/opex", response_model=OPEXOutput, summary="Calculate Operational Expenses")
async def calculate_opex(input_data: OPEXInput) -> OPEXOutput:
    """
    Calculate operational expenses (OPEX) with detailed breakdown.
    
    Provides comprehensive cost analysis including:
    - Acid consumption and cost
    - Labor costs
    - Diesel/fuel costs
    - Electricity costs
    - Maintenance costs
    - Overhead expenses
    - Cost breakdown percentages
    """
    try:
        result = calculator.calculate_opex(
            tonnage=input_data.tonnage,
            days=input_data.days,
            acid_price=input_data.acid_price,
            labor_cost=input_data.labor_cost,
            diesel_price=input_data.diesel_price,
            electricity_price=getattr(input_data, 'electricity_price', 0.1),
            maintenance_factor=getattr(input_data, 'maintenance_factor', 0.05)
        )
        
        data = _handle_calculation_result(result, "OPEX calculation")
        
        return OPEXOutput(**data)
        
    except Exception as e:
        logger.exception("Error in OPEX calculation")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Calculation error: {str(e)}"
        )


@router.post("/pls", response_model=PLSOutput, summary="Calculate PLS Properties")
async def calculate_pls(input_data: PLSInput) -> PLSOutput:
    """
    Calculate Pregnant Leach Solution (PLS) properties.
    
    Determines:
    - Total flow rate
    - Copper dissolution rate
    - PLS copper concentration
    - Annual cathode production
    - Daily production rate
    """
    try:
        result = calculator.calculate_pls(
            flow_rate=input_data.flow_rate,
            area=input_data.area,
            recovery=input_data.recovery,
            ore_grade=input_data.ore_grade,
            tonnage=input_data.tonnage,
            solution_density=getattr(input_data, 'solution_density', 1.02)
        )
        
        data = _handle_calculation_result(result, "PLS calculation")
        
        return PLSOutput(**data)
        
    except Exception as e:
        logger.exception("Error in PLS calculation")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Calculation error: {str(e)}"
        )


@router.post("/schedule", response_model=ScheduleOutput, summary="Generate Production Schedule")
async def calculate_schedule(input_data: ScheduleInput) -> ScheduleOutput:
    """
    Generate production schedule to meet cathode targets.
    
    Creates a monthly production plan including:
    - Required ore tonnage
    - Daily feed rate
    - Monthly production breakdown
    - Ramp-up period consideration
    - Efficiency factors
    - Variance analysis
    """
    try:
        result = calculator.production_schedule(
            target_cathode=input_data.target_cathode,
            ore_grade=input_data.ore_grade,
            recovery=input_data.recovery,
            days=input_data.days,
            ramp_up_period=getattr(input_data, 'ramp_up_period', 30),
            efficiency_factor=getattr(input_data, 'efficiency_factor', 0.95)
        )
        
        data = _handle_calculation_result(result, "Production scheduling")
        
        return ScheduleOutput(**data)
        
    except Exception as e:
        logger.exception("Error in production scheduling")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Calculation error: {str(e)}"
        )


@router.post("/volume", response_model=PadVolumeOutput, summary="Calculate Pad Volume")
async def calculate_volume(input_data: PadVolumeInput) -> PadVolumeOutput:
    """
    Calculate pad volume and tonnage with terrain correction.
    
    Accounts for:
    - Wall slopes
    - Terrain gradients in X and Y directions
    - Liner thickness requirements
    - Freeboard specifications
    - Surface area calculations
    """
    try:
        result = calculator.pad_volume_calculation(
            L=input_data.L,
            W=input_data.W,
            H_top=input_data.H_top,
            H_bottom=input_data.H_bottom,
            slope_deg=input_data.slope_deg,
            terrain_slope_x=input_data.terrain_slope_x or 0,
            terrain_slope_y=input_data.terrain_slope_y or 0,
            liner_thickness=getattr(input_data, 'liner_thickness', 0.002),
            freeboard=getattr(input_data, 'freeboard', 0.5)
        )
        
        data = _handle_calculation_result(result, "Volume calculation")
        
        return PadVolumeOutput(**data)
        
    except Exception as e:
        logger.exception("Error in volume calculation")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Calculation error: {str(e)}"
        )


@router.post("/acid-optimize", response_model=AcidOptimizationOutput, summary="Optimize Acid Addition")
async def optimize_acid(input_data: AcidOptimizationInput) -> AcidOptimizationOutput:
    """
    Optimize acid addition for pH control.
    
    Provides recommendations for:
    - Acid dosing rate (kg/hour)
    - Daily acid requirement (tonnes/day)
    - pH adjustment direction
    - Urgency level
    - Next check time
    - Control strategy
    """
    try:
        result = calculator.optimize_acid_addition(
            pls_flow=input_data.pls_flow,
            cu_conc=input_data.cu_conc,
            target_ph=input_data.target_ph,
            current_ph=input_data.current_ph,
            acid_purity=getattr(input_data, 'acid_purity', 0.98),
            control_mode=getattr(input_data, 'control_mode', 'automatic')
        )
        
        data = _handle_calculation_result(result, "Acid optimization")
        
        return AcidOptimizationOutput(**data)
        
    except Exception as e:
        logger.exception("Error in acid optimization")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Calculation error: {str(e)}"
        )


@router.post("/monte-carlo", response_model=MonteCarloOutput, summary="Monte Carlo Simulation")
async def run_monte_carlo(input_data: MonteCarloInput) -> MonteCarloOutput:
    """
    Perform Monte Carlo simulation for uncertainty analysis.
    
    Analyzes the impact of parameter uncertainty on recovery predictions
    by running multiple simulations with randomly varied inputs.
    
    Returns:
    - Mean recovery
    - Standard deviation
    - Confidence intervals (P5, P50, P95)
    - Statistical summary
    """
    try:
        result = calculator.monte_carlo_analysis(
            base_parameters=input_data.base_parameters,
            n_simulations=input_data.n_simulations or 1000,
            confidence_level=input_data.confidence_level or 0.95
        )
        
        data = _handle_calculation_result(result, "Monte Carlo simulation")
        
        return MonteCarloOutput(**data)
        
    except Exception as e:
        logger.exception("Error in Monte Carlo simulation")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Calculation error: {str(e)}"
        )


@router.post("", response_model=CalculationResponse, summary="Multiple Calculations")
async def calculate_multiple(request: CalculationRequest) -> CalculationResponse:
    """
    Execute multiple calculations in a single request.
    
    Accepts any combination of:
    - recovery
    - opex
    - pls
    - schedule
    - volume
    - acid_optimization
    
    Returns all requested results in one response with unified format.
    """
    try:
        results: Dict[str, Any] = {}
        all_warnings = []
        all_errors = []
        
        if request.recovery:
            try:
                ore_type = OreType(getattr(request.recovery, 'ore_type', 'oxide'))
                result = calculator.calculate_recovery(
                    flow_rate=request.recovery.flow_rate,
                    acid_conc=request.recovery.acid_conc,
                    time_days=request.recovery.time_days,
                    ore_grade=request.recovery.ore_grade,
                    particle_size=request.recovery.particle_size,
                    ore_type=ore_type
                )
                if result.success:
                    results['recovery'] = result.data
                    all_warnings.extend(result.warnings)
                else:
                    all_errors.extend(result.errors)
            except Exception as e:
                all_errors.append(f"Recovery: {str(e)}")
        
        if request.opex:
            try:
                result = calculator.calculate_opex(
                    tonnage=request.opex.tonnage,
                    days=request.opex.days,
                    acid_price=request.opex.acid_price,
                    labor_cost=request.opex.labor_cost,
                    diesel_price=request.opex.diesel_price
                )
                if result.success:
                    results['opex'] = result.data
                    all_warnings.extend(result.warnings)
                else:
                    all_errors.extend(result.errors)
            except Exception as e:
                all_errors.append(f"OPEX: {str(e)}")
        
        if request.pls:
            try:
                result = calculator.calculate_pls(
                    flow_rate=request.pls.flow_rate,
                    area=request.pls.area,
                    recovery=request.pls.recovery,
                    ore_grade=request.pls.ore_grade,
                    tonnage=request.pls.tonnage
                )
                if result.success:
                    results['pls'] = result.data
                    all_warnings.extend(result.warnings)
                else:
                    all_errors.extend(result.errors)
            except Exception as e:
                all_errors.append(f"PLS: {str(e)}")
        
        if request.schedule:
            try:
                result = calculator.production_schedule(
                    target_cathode=request.schedule.target_cathode,
                    ore_grade=request.schedule.ore_grade,
                    recovery=request.schedule.recovery,
                    days=request.schedule.days
                )
                if result.success:
                    results['schedule'] = result.data
                    all_warnings.extend(result.warnings)
                else:
                    all_errors.extend(result.errors)
            except Exception as e:
                all_errors.append(f"Schedule: {str(e)}")
        
        if request.volume:
            try:
                result = calculator.pad_volume_calculation(
                    L=request.volume.L,
                    W=request.volume.W,
                    H_top=request.volume.H_top,
                    H_bottom=request.volume.H_bottom,
                    slope_deg=request.volume.slope_deg,
                    terrain_slope_x=request.volume.terrain_slope_x or 0,
                    terrain_slope_y=request.volume.terrain_slope_y or 0
                )
                if result.success:
                    results['volume'] = result.data
                    all_warnings.extend(result.warnings)
                else:
                    all_errors.extend(result.errors)
            except Exception as e:
                all_errors.append(f"Volume: {str(e)}")
        
        if request.acid_optimization:
            try:
                result = calculator.optimize_acid_addition(
                    pls_flow=request.acid_optimization.pls_flow,
                    cu_conc=request.acid_optimization.cu_conc,
                    target_ph=request.acid_optimization.target_ph,
                    current_ph=request.acid_optimization.current_ph
                )
                if result.success:
                    results['acid_optimization'] = result.data
                    all_warnings.extend(result.warnings)
                else:
                    all_errors.extend(result.errors)
            except Exception as e:
                all_errors.append(f"Acid Optimization: {str(e)}")
        
        success = len(results) > 0 and len(all_errors) == 0
        
        return CalculationResponse(
            success=success,
            results=results,
            error="; ".join(all_errors) if all_errors else None,
            warnings=all_warnings if all_warnings else None
        )
        
    except Exception as e:
        logger.exception("Error in multiple calculations")
        return CalculationResponse(
            success=False,
            results={},
            error=str(e)
        )
