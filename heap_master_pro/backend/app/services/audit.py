"""
Audit logging service for tracking system changes.
"""
from sqlalchemy.orm import Session
from typing import Optional, Any, Dict
import json


class AuditService:
    """Service for creating and managing audit logs."""
    
    @staticmethod
    def log_action(
        db: Session,
        action: str,
        entity_type: str,
        entity_id: Optional[int] = None,
        user_id: Optional[int] = None,
        project_id: Optional[int] = None,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        changes: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> None:
        """
        Log an action in the audit trail.
        
        Args:
            db: Database session
            action: Type of action (create, update, delete, login, etc.)
            entity_type: Type of entity affected (user, pad, project, etc.)
            entity_id: ID of the affected entity
            user_id: ID of the user who performed the action
            project_id: ID of related project (if applicable)
            old_values: Previous values (for updates)
            new_values: New values (for creates/updates)
            changes: Human-readable description of changes
            ip_address: IP address of the request
            user_agent: User agent string
        """
        from app.models.audit import AuditLog
        
        # Serialize complex objects to JSON strings
        old_values_json = None
        new_values_json = None
        
        if old_values:
            try:
                old_values_json = {
                    k: v.isoformat() if hasattr(v, 'isoformat') else v
                    for k, v in old_values.items()
                }
            except Exception:
                old_values_json = str(old_values)
        
        if new_values:
            try:
                new_values_json = {
                    k: v.isoformat() if hasattr(v, 'isoformat') else v
                    for k, v in new_values.items()
                }
            except Exception:
                new_values_json = str(new_values)
        
        audit_log = AuditLog(
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            user_id=user_id,
            project_id=project_id,
            old_values=old_values_json,
            new_values=new_values_json,
            changes=changes,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        
        db.add(audit_log)
        db.commit()
    
    @staticmethod
    def get_user_history(
        db: Session,
        user_id: int,
        limit: int = 100,
        offset: int = 0,
    ):
        """Get audit history for a specific user."""
        from app.models.audit import AuditLog
        
        return db.query(AuditLog).filter(
            AuditLog.user_id == user_id
        ).order_by(
            AuditLog.created_at.desc()
        ).offset(offset).limit(limit).all()
    
    @staticmethod
    def get_entity_history(
        db: Session,
        entity_type: str,
        entity_id: int,
        limit: int = 100,
    ):
        """Get audit history for a specific entity."""
        from app.models.audit import AuditLog
        
        return db.query(AuditLog).filter(
            AuditLog.entity_type == entity_type,
            AuditLog.entity_id == entity_id,
        ).order_by(
            AuditLog.created_at.desc()
        ).limit(limit).all()
