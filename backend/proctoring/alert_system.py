import time
import threading
from enum import Enum

class AlertSeverity(Enum):
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"

class AlertSystem:
    def __init__(self):
        self.alert_history = []
        self.alert_rules = {
            'multiple_faces': {'severity': AlertSeverity.CRITICAL, 'points': 3, 'cooldown': 3.0},
            'no_face': {'severity': AlertSeverity.WARNING, 'points': 2, 'cooldown': 5.0},
            'head_movement': {'severity': AlertSeverity.WARNING, 'points': 1, 'cooldown': 2.0},
            'background_voice': {'severity': AlertSeverity.INFO, 'points': 1, 'cooldown': 6.0},
            'tab_switch': {'severity': AlertSeverity.WARNING, 'points': 2, 'cooldown': 10.0},
            'unauthorized_face': {'severity': AlertSeverity.CRITICAL, 'points': 5, 'cooldown': 2.0},
        }
        self.last_alert_time = {}
        self.escalation_count = {}
        self.escalation_threshold = 3  # Escalate after 3 alerts of same type
        
    def create_alert(self, alert_type, message, details=None):
        """Create a new alert with severity and rules"""
        current_time = time.time()
        
        # Check if alert type exists in rules
        if alert_type not in self.alert_rules:
            print(f"[ALERT] Unknown alert type: {alert_type}")
            return None
        
        rule = self.alert_rules[alert_type]
        
        # Check cooldown
        if alert_type in self.last_alert_time:
            if current_time - self.last_alert_time[alert_type] < rule['cooldown']:
                return None
        
        # Create alert object
        alert = {
            'type': alert_type,
            'message': message,
            'severity': rule['severity'].value,
            'points': rule['points'],
            'timestamp': current_time,
            'details': details or {}
        }
        
        # Update last alert time
        self.last_alert_time[alert_type] = current_time
        
        # Track escalation
        if alert_type not in self.escalation_count:
            self.escalation_count[alert_type] = 0
        self.escalation_count[alert_type] += 1
        
        # Add to history
        self.alert_history.append(alert)
        
        # Check for escalation
        if self.escalation_count[alert_type] >= self.escalation_threshold:
            alert['escalated'] = True
            alert['message'] = f"ESCALATED: {message}"
            print(f"[ESCALATION] Multiple violations of type: {alert_type}")
        
        print(f"[ALERT] {rule['severity'].upper()}: {message}")
        return alert
    
    def get_alert_color(self, severity):
        """Get color code for alert severity"""
        colors = {
            AlertSeverity.CRITICAL: "#DC2626",  # Red
            AlertSeverity.WARNING: "#F59E0B",   # Orange
            AlertSeverity.INFO: "#3B82F6"      # Blue
        }
        return colors.get(severity, "#6B7280")  # Gray default
    
    def get_recent_alerts(self, count=10):
        """Get recent alerts"""
        return sorted(self.alert_history, key=lambda x: x['timestamp'], reverse=True)[:count]
    
    def get_alerts_by_severity(self, severity):
        """Get alerts filtered by severity"""
        return [alert for alert in self.alert_history if alert['severity'] == severity.value]
    
    def get_alert_statistics(self):
        """Get statistics of alerts"""
        stats = {
            'total_alerts': len(self.alert_history),
            'by_type': {},
            'by_severity': {
                'critical': 0,
                'warning': 0,
                'info': 0
            }
        }
        
        for alert in self.alert_history:
            # Count by type
            if alert['type'] not in stats['by_type']:
                stats['by_type'][alert['type']] = 0
            stats['by_type'][alert['type']] += 1
            
            # Count by severity
            if alert['severity'] == AlertSeverity.CRITICAL.value:
                stats['by_severity']['critical'] += 1
            elif alert['severity'] == AlertSeverity.WARNING.value:
                stats['by_severity']['warning'] += 1
            else:
                stats['by_severity']['info'] += 1
        
        return stats
    
    def clear_old_alerts(self, max_age_hours=24):
        """Clear alerts older than specified hours"""
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        self.alert_history = [
            alert for alert in self.alert_history 
            if current_time - alert['timestamp'] < max_age_seconds
        ]
    
    def should_escalate(self, alert_type):
        """Check if alert should be escalated"""
        return self.escalation_count.get(alert_type, 0) >= self.escalation_threshold

# Global alert system
alert_system = AlertSystem()

def initialize_alert_system():
    """Initialize the enhanced alert system"""
    return alert_system

def create_severity_alert(alert_type, message, details=None):
    """Create alert with automatic severity assignment"""
    return alert_system.create_alert(alert_type, message, details)

def get_alert_statistics():
    """Get comprehensive alert statistics"""
    return alert_system.get_alert_statistics()

def check_escalation_status(alert_type):
    """Check if specific alert type should be escalated"""
    return alert_system.should_escalate(alert_type)
