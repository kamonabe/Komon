"""
Network check state manager.

Manages network check state (NG only) with retention-based auto-cleanup.
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)


class NetworkStateManager:
    """
    Network check state manager.
    
    Stores only NG (failed) states with retention-based auto-cleanup.
    OK states are not stored.
    
    State format:
    {
        "net.ping:192.168.1.1": {
            "first_detected_at": "2025-12-08T12:00:00Z"
        },
        "net.http:https://api.example.com": {
            "first_detected_at": "2025-12-08T12:05:00Z"
        }
    }
    """
    
    def __init__(self, state_file, retention_hours=24):
        """
        Initialize state manager.
        
        Args:
            state_file (str): Path to state file
            retention_hours (int): Retention period in hours (default: 24)
        """
        self.state_file = Path(state_file)
        self.retention_hours = retention_hours
        self.state = self._load()
    
    def _load(self):
        """Load state from file."""
        try:
            if not self.state_file.exists():
                logger.debug("State file not found, using empty state: %s", self.state_file)
                return {}
            
            with open(self.state_file, 'r', encoding='utf-8') as f:
                state = json.load(f)
            
            logger.debug("Loaded state: %d entries", len(state))
            return state
            
        except json.JSONDecodeError as e:
            logger.warning("State file corrupted, using empty state: %s", e)
            return {}
            
        except Exception as e:
            logger.error("Failed to load state: %s", e, exc_info=True)
            return {}
    
    def _save(self):
        """Save state to file."""
        try:
            # Create parent directory if not exists
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, indent=2, ensure_ascii=False)
            
            logger.debug("Saved state: %d entries", len(self.state))
            
        except Exception as e:
            logger.error("Failed to save state: %s", e, exc_info=True)
    
    def _cleanup_expired(self):
        """Remove expired NG states based on retention period."""
        now = datetime.now()
        retention_delta = timedelta(hours=self.retention_hours)
        
        expired_keys = []
        for key, value in self.state.items():
            try:
                first_detected = datetime.fromisoformat(value['first_detected_at'].replace('Z', '+00:00'))
                if now - first_detected.replace(tzinfo=None) > retention_delta:
                    expired_keys.append(key)
            except Exception as e:
                logger.warning("Invalid timestamp in state, removing: key=%s, error=%s", key, e)
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.state[key]
            logger.debug("Removed expired state: %s", key)
        
        if expired_keys:
            logger.info("Cleaned up %d expired NG states", len(expired_keys))
    
    def check_state_change(self, check_type, target, is_ok):
        """
        Check if state has changed and update state.
        
        Args:
            check_type (str): Check type ('ping' or 'http')
            target (str): Target (host or URL)
            is_ok (bool): Current check result
        
        Returns:
            str or None: State change type ('ok_to_ng', 'ng_to_ok', None)
        """
        key = f"net.{check_type}:{target}"
        was_ng = key in self.state
        
        # Cleanup expired states before checking
        self._cleanup_expired()
        
        if is_ok:
            # Current: OK
            if was_ng:
                # NG → OK (recovery)
                del self.state[key]
                self._save()
                logger.info("State change detected: NG → OK, %s", key)
                return 'ng_to_ok'
            else:
                # OK → OK (no change)
                return None
        else:
            # Current: NG
            if was_ng:
                # NG → NG (no change)
                return None
            else:
                # OK → NG (new failure)
                self.state[key] = {
                    'first_detected_at': datetime.now().isoformat() + 'Z'
                }
                self._save()
                logger.info("State change detected: OK → NG, %s", key)
                return 'ok_to_ng'
    
    def get_ng_count(self):
        """Get current NG count."""
        return len(self.state)
    
    def get_ng_targets(self):
        """Get list of current NG targets."""
        return list(self.state.keys())
    
    def format_notification_message(self, check_type, target, state_change, description=None):
        """
        Format notification message for state change.
        
        Args:
            check_type (str): Check type ('ping' or 'http')
            target (str): Target (host or URL)
            state_change (str): State change type ('ok_to_ng' or 'ng_to_ok')
            description (str, optional): Target description
        
        Returns:
            str: Formatted notification message
        """
        # Format display name
        if description:
            display_name = f"{description} ({target})"
        else:
            display_name = target
        
        if state_change == 'ok_to_ng':
            if check_type == 'ping':
                return f"❌ Ping失敗: {display_name}"
            else:  # http
                return f"❌ HTTP失敗: {display_name}"
        elif state_change == 'ng_to_ok':
            if check_type == 'ping':
                return f"✅ Ping復旧: {display_name}"
            else:  # http
                return f"✅ HTTP復旧: {display_name}"
        else:
            return ""
