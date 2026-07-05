"""
Heap Master Pro - Pad Manager Service
Handles CRUD operations for heap leaching pads with automatic calculations
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from app.schemas.calculations import PadCreate, PadUpdate, PadResponse
from app.services.metallurgy_engine import HeapLeachCalculator

logger = logging.getLogger(__name__)


class PadManager:
    """
    Manages heap leaching pad operations.
    
    Features:
    - In-memory storage (can be replaced with database)
    - Automatic volume and tonnage calculations
    - Recoverable copper estimation
    - Search and pagination support
    """
    
    def __init__(self):
        self._pads: Dict[int, Dict[str, Any]] = {}
        self._next_id = 1
        self._calculator = HeapLeachCalculator()
    
    def _calculate_pad_metrics(self, pad_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate volume, tonnage, and recoverable copper"""
        # Use the calculator's volume calculation
        volume_result = self._calculator.pad_volume_calculation(
            L=pad_data["L"],
            W=pad_data["W"],
            H_top=pad_data["H"],
            H_bottom=0,
            slope_deg=pad_data["slope_deg"]
        )
        
        if not volume_result.success:
            raise ValueError(f"Volume calculation failed: {volume_result.errors}")
        
        volume_m3 = volume_result.data["volume_m3"]
        tonnage = volume_result.data["tonnage"]
        
        # Calculate recoverable copper
        ore_grade = pad_data.get("ore_grade", 0.7)
        recovery = pad_data.get("recovery", 85.0)
        recoverable_copper = tonnage * (ore_grade / 100) * (recovery / 100)
        
        return {
            "volume_m3": round(volume_m3, 2),
            "tonnage": round(tonnage, 2),
            "recoverable_copper_tonnes": round(recoverable_copper, 2)
        }
    
    def create_pad(self, pad_data: PadCreate) -> PadResponse:
        """Create a new pad with automatic metric calculations"""
        try:
            # Convert to dict and calculate metrics
            data = pad_data.model_dump()
            metrics = self._calculate_pad_metrics(data)
            
            # Create pad record
            pad_record = {
                **data,
                "id": self._next_id,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                **metrics
            }
            
            self._pads[self._next_id] = pad_record
            self._next_id += 1
            
            return PadResponse(**pad_record)
            
        except Exception as e:
            logger.exception(f"Error creating pad: {e}")
            raise
    
    def get_pad(self, pad_id: int) -> Optional[PadResponse]:
        """Retrieve a pad by ID"""
        pad_record = self._pads.get(pad_id)
        if pad_record:
            return PadResponse(**pad_record)
        return None
    
    def get_all_pads(
        self, 
        skip: int = 0, 
        limit: int = 100, 
        search: Optional[str] = None
    ) -> List[PadResponse]:
        """Retrieve all pads with pagination and search"""
        pads = list(self._pads.values())
        
        # Apply search filter
        if search:
            pads = [
                p for p in pads 
                if p.get("name") and search.lower() in p["name"].lower()
            ]
        
        # Apply pagination
        paginated = pads[skip:skip + limit]
        
        return [PadResponse(**p) for p in paginated]
    
    def get_total_count(self, search: Optional[str] = None) -> int:
        """Get total count of pads"""
        if not search:
            return len(self._pads)
        
        return len([
            p for p in self._pads.values()
            if p.get("name") and search.lower() in p["name"].lower()
        ])
    
    def update_pad(self, pad_id: int, pad_data: PadUpdate) -> Optional[PadResponse]:
        """Update an existing pad"""
        pad_record = self._pads.get(pad_id)
        if not pad_record:
            return None
        
        # Get only non-None fields
        updates = {k: v for k, v in pad_data.model_dump().items() if v is not None}
        
        if not updates:
            return PadResponse(**pad_record)
        
        # Update record
        pad_record.update(updates)
        pad_record["updated_at"] = datetime.utcnow()
        
        # Recalculate metrics if dimensions changed
        dimension_fields = {"L", "W", "H", "slope_deg", "ore_grade", "recovery", "density"}
        if any(field in updates for field in dimension_fields):
            try:
                metrics = self._calculate_pad_metrics(pad_record)
                pad_record.update(metrics)
            except ValueError as e:
                logger.warning(f"Could not recalculate metrics: {e}")
        
        self._pads[pad_id] = pad_record
        return PadResponse(**pad_record)
    
    def delete_pad(self, pad_id: int) -> bool:
        """Delete a pad"""
        if pad_id in self._pads:
            del self._pads[pad_id]
            return True
        return False
    
    def clear_all(self):
        """Clear all pads (useful for testing)"""
        self._pads.clear()
        self._next_id = 1
