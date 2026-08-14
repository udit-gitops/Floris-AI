"""
Business rule constants for Floris AI.
Keeping these here (instead of scattered magic numbers in logic files)
means when a judge asks "why 2 attempts, why 48 hours", you can point
to ONE file and explain every number.
"""

# --- Stall detection thresholds (hours since last activity) ---
KYC_STALL_HOURS = 48
PAYMENT_STALL_HOURS = 72
SILENT_STALL_HOURS = 120  # 5 days

# --- Escalation ---
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

# --- Do-not-disturb window (24h clock, local time) ---
DND_START_HOUR = 20  # 8 PM
DND_END_HOUR = 9  # 9 AM

# --- Status values used across applications / conversation_state ---
STATUS_DETECTED = "DETECTED"
STATUS_CONTACTED = "CONTACTED"
STATUS_RECOVERED = "RECOVERED"
STATUS_ESCALATED = "ESCALATED"
STATUS_ABANDONED = "ABANDONED"

# --- Stall types ---
STALL_TYPE_KYC = "KYC_PENDING"
STALL_TYPE_PAYMENT = "PAYMENT_PENDING"
STALL_TYPE_SILENT = "GONE_SILENT"

# --- Channels ---
CHANNEL_VOICE = "voice"
CHANNEL_CHAT = "chat"
