"""
Heap Master Pro - API Routes for Metallurgical Calculations
"""

from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any

from app.schemas import (
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
)
from app.services.metallurgy_engine import HeapLeachCalculator

router = APIRouter(prefix="/calculate", tags=["calculations"])

# Initialize calculator instance
calculator = HeapLeachCalculator()


@router.post("/recovery", response_model=RecoveryOutput)
async def calculate_recovery(input_data: RecoveryInput) -> RecoveryOutput:
    """
    Calculate copper recovery percentage using multivariate regression.
    
    This endpoint computes the expected copper recovery based on:
    - Irrigation flow rate
    - Acid concentration
    - Leaching time
    - Ore grade
    - Particle size
    """
    try:
        recovery = calculator.calculate_recovery(
            flow_rate=input_data.flow_rate,
            acid_conc=input_data.acid_conc,
            time_days=input_data.time_days,
            ore_grade=input_data.ore_grade,
            particle_size=input_data.particle_size
        )
        
        return RecoveryOutput(
            recovery_percent=recovery,
            calculation_method="multivariate_regression"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Calculation error: {str(e)}"
        )


@router.post("/opex", response_model=OPEXOutput)
async def calculate_opex(input_data: OPEXInput) -> OPEXOutput:
    """
    Calculate operational expenses (OPEX) breakdown.
    
    Provides detailed cost analysis including:
    - Acid consumption and cost
    - Labor costs
    - Diesel/fuel costs
    - Overhead expenses
    """
    try:
        result = calculator.calculate_opex(
            tonnage=input_data.tonnage,
            days=input_data.days,
            acid_price=input_data.acid_price,
            labor_cost=input_data.labor_cost,
            diesel_price=input_data.diesel_price
        )
        
        return OPEXOutput(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Calculation error: {str(e)}"
        )


@router.post("/pls", response_model=PLSOutput)
async def calculate_pls(input_data: PLSInput) -> PLSOutput:
    """
    Calculate Pregnant Leach Solution (PLS) properties.
    
    Determines:
    - Total flow rate
    - Copper dissolution rate
    - PLS copper concentration
    - Annual cathode production
    """
    try:
        result = calculator.calculate_pls(
            flow_rate=input_data.flow_rate,
            area=input_data.area,
            recovery=input_data.recovery,
            ore_grade=input_data.ore_grade,
            tonnage=input_data.tonnage
        )
        
        return PLSOutput(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Calculation error: {str(e)}"
        )


@router.post("/schedule", response_model=ScheduleOutput)
async def calculate_schedule(input_data: ScheduleInput) -> ScheduleOutput:
    """
    Generate production schedule to meet cathode targets.
    
    Creates a monthly production plan including:
    - Required ore tonnage
    - Daily feed rate
    - Monthly production breakdown
    """
    try:
        result = calculator.production_schedule(
            target_cathode=input_data.target_cathode,
            ore_grade=input_data.ore_grade,
            recovery=input_data.recovery,
            days=input_data.days
        )
        
        return ScheduleOutput(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Calculation error: {str(e)}"
        )


@router.post("/volume", response_model=PadVolumeOutput)
async def calculate_volume(input_data: PadVolumeInput) -> PadVolumeOutput:
    """
    Calculate pad volume and tonnage with terrain correction.
    
    Accounts for:
    - Wall slopes
    - Terrain gradients
    - Material density
    """
    try:
        result = calculator.pad_volume_calculation(
            L=input_data.L,
            W=input_data.W,
            H_top=input_data.H_top,
            H_bottom=input_data.H_bottom,
            slope_deg=input_data.slope_deg,
            terrain_slope_x=input_data.terrain_slope_x,
            terrain_slope_y=input_data.terrain_slope_y
        )
        
        return PadVolumeOutput(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Calculation error: {str(e)}"
        )


@router.post("/acid-optimize", response_model=AcidOptimizationOutput)
async def optimize_acid(input_data: AcidOptimizationInput) -> AcidOptimizationOutput:
    """
    Optimize acid addition for pH control.
    
    Provides recommendations for:
    - Acid dosing rate
    - Daily acid requirement
    - pH adjustment direction
    """
    try:
        result = calculator.optimize_acid_addition(
            pls_flow=input_data.pls_flow,
            cu_conc=input_data.cu_conc,
            target_ph=input_data.target_ph,
            current_ph=input_data.current_ph
        )
        
        return AcidOptimizationOutput(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Calculation error: {str(e)}"
        )


@router.post("", response_model=CalculationResponse)
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
    
    Returns all requested results in one response.
    """
    try:
        results: Dict[str, Any] = {}
        
        if request.recovery:
            recovery = calculator.calculate_recovery(
                flow_rate=request.recovery.flow_rate,
                acid_conc=request.recovery.acid_conc,
                time_days=request.recovery.time_days,
                ore_grade=request.recovery.ore_grade,
                particle_size=request.recovery.particle_size
            )
            results['recovery'] = {'recovery_percent': recovery}
        
        if request.opex:
            results['opex'] = calculator.calculate_opex(
                tonnage=request.opex.tonnage,
                days=request.opex.days,
                acid_price=request.opex.acid_price,
                labor_cost=request.opex.labor_cost,
                diesel_price=request.opex.diesel_price
            )
        
        if request.pls:
            results['pls'] = calculator.calculate_pls(
                flow_rate=request.pls.flow_rate,
                area=request.pls.area,
                recovery=request.pls.recovery,
                ore_grade=request.pls.ore_grade,
                tonnage=request.pls.tonnage
            )
        
        if request.schedule:
            results['schedule'] = calculator.production_schedule(
                target_cathode=request.schedule.target_cathode,
                ore_grade=request.schedule.ore_grade,
                recovery=request.schedule.recovery,
                days=request.schedule.days
            )
        
        if request.volume:
            results['volume'] = calculator.pad_volume_calculation(
                L=request.volume.L,
                W=request.volume.W,
                H_top=request.volume.H_top,
                H_bottom=request.volume.H_bottom,
                slope_deg=request.volume.slope_deg,
                terrain_slope_x=request.volume.terrain_slope_x,
                terrain_slope_y=request.volume.terrain_slope_y
            )
        
        if request.acid_optimization:
            results['acid_optimization'] = calculator.optimize_acid_addition(
                pls_flow=request.acid_optimization.pls_flow,
                cu_conc=request.acid_optimization.cu_conc,
                target_ph=request.acid_optimization.target_ph,
                current_ph=request.acid_optimization.current_ph
            )
        
        return CalculationResponse(
            success=True,
            results=results
        )
        
    except Exception as e:
        return CalculationResponse(
            success=False,
            results={},
            error=str(e)
        )
