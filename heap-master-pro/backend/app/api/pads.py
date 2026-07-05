"""
Heap Master Pro - API Routes for Pad Management
RESTful API for CRUD operations on heap leaching pads
"""

from fastapi import APIRouter, HTTPException, status
from typing import List, Optional
import logging
from datetime import datetime

from app.schemas.pads import (
    PadCreate,
    PadUpdate,
    PadResponse,
    PadListResponse,
)
from app.services.pad_manager import PadManager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/pads", tags=["pads"])

# Initialize pad manager (in-memory storage for now)
pad_manager = PadManager()


@router.get("", response_model=PadListResponse, summary="List All Pads")
async def list_pads(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None
):
    """
    Retrieve a list of all heap leaching pads.
    
    Supports pagination and search by pad name.
    """
    try:
        pads = pad_manager.get_all_pads(skip=skip, limit=limit, search=search)
        total = pad_manager.get_total_count(search=search)
        
        return PadListResponse(
            success=True,
            data=pads,
            total=total,
            skip=skip,
            limit=limit
        )
    except Exception as e:
        logger.exception("Error listing pads")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve pads: {str(e)}"
        )


@router.get("/{pad_id}", response_model=PadResponse, summary="Get Pad by ID")
async def get_pad(pad_id: int):
    """
    Retrieve detailed information about a specific pad.
    """
    try:
        pad = pad_manager.get_pad(pad_id)
        
        if not pad:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pad with ID {pad_id} not found"
            )
        
        return pad
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error retrieving pad {pad_id}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve pad: {str(e)}"
        )


@router.post("", response_model=PadResponse, status_code=status.HTTP_201_CREATED, summary="Create New Pad")
async def create_pad(pad_data: PadCreate):
    """
    Create a new heap leaching pad.
    
    Automatically calculates:
    - Volume based on dimensions and slope
    - Tonnage based on volume and density
    - Recoverable copper based on grade and recovery
    """
    try:
        pad = pad_manager.create_pad(pad_data)
        
        logger.info(f"Created new pad: {pad.name or f'ID {pad.id}'}")
        
        return pad
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.exception("Error creating pad")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create pad: {str(e)}"
        )


@router.put("/{pad_id}", response_model=PadResponse, summary="Update Pad")
async def update_pad(pad_id: int, pad_data: PadUpdate):
    """
    Update an existing pad's properties.
    
    Only provided fields will be updated.
    Recalculates volume and tonnage if dimensions change.
    """
    try:
        pad = pad_manager.update_pad(pad_id, pad_data)
        
        if not pad:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pad with ID {pad_id} not found"
            )
        
        logger.info(f"Updated pad: {pad_id}")
        
        return pad
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.exception(f"Error updating pad {pad_id}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update pad: {str(e)}"
        )


@router.delete("/{pad_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete Pad")
async def delete_pad(pad_id: int):
    """
    Delete a pad from the system.
    """
    try:
        success = pad_manager.delete_pad(pad_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pad with ID {pad_id} not found"
            )
        
        logger.info(f"Deleted pad: {pad_id}")
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error deleting pad {pad_id}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete pad: {str(e)}"
        )


@router.post("/batch", response_model=PadListResponse, status_code=status.HTTP_201_CREATED, summary="Create Multiple Pads")
async def create_pads_batch(pads_data: List[PadCreate]):
    """
    Create multiple pads in a single request.
    
    Useful for importing pad configurations or creating pad arrays.
    """
    try:
        created_pads = []
        
        for pad_data in pads_data:
            pad = pad_manager.create_pad(pad_data)
            created_pads.append(pad)
        
        logger.info(f"Created {len(created_pads)} pads in batch")
        
        return PadListResponse(
            success=True,
            data=created_pads,
            total=len(created_pads),
            skip=0,
            limit=len(created_pads)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.exception("Error creating pads in batch")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create pads: {str(e)}"
        )
