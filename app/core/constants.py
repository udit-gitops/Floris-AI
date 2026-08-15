"""
Business rule constants for Floris AI.
Centralizes thresholds, escalation rules, statuses, stall types, and
communication channels used across the application.
"""

# Stall detection thresholds (hours since last activity)
KYC_STALL_HOURS = 48
PAYMENT_STALL_HOURS = 72
SILENT_STALL_HOURS = 120  # 5 days

# Escalation
MAX_AUTO_ATTEMPTS = 2

RED_FLAG_KEYWORDS = [
    "stop calling",
    "not interested",
    "harassment",
    "complain",
    "can't pay",
    "cannot afford",
    "confused",
    "talk to someone",
]

# Do-not-disturb window (24-hour clock, local time)
DND_START_HOUR = 20  # 8 PM
DND_END_HOUR = 9  # 9 AM

# Status values used across applications and conversation_state
STATUS_DETECTED = "DETECTED"
STATUS_CONTACTED = "CONTACTED"
STATUS_RECOVERED = "RECOVERED"
STATUS_ESCALATED = "ESCALATED"
STATUS_ABANDONED = "ABANDONED"

# Stall types
STALL_TYPE_KYC = "KYC_PENDING"
STALL_TYPE_PAYMENT = "PAYMENT_PENDING"
STALL_TYPE_SILENT = "GONE_SILENT"

# Communication channels
CHANNEL_VOICE = "voice"
CHANNEL_CHAT = "chat"
