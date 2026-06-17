"""
CyberShield AI — Central Configuration
All constants, paths, and settings live here.
Supports: CIC-IDS2017 + CSE-CIC-IDS2018 (combined or individual)
"""

from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────
BASE_DIR    = Path(__file__).parent
DATA_DIR    = BASE_DIR / "datasets"
MODEL_DIR   = BASE_DIR / "saved_models"
DB_PATH     = BASE_DIR / "ids_alerts.db"

DATA_DIR.mkdir(exist_ok=True)
MODEL_DIR.mkdir(exist_ok=True)

# ── Reproducibility ────────────────────────────────────────────────────────
RANDOM_STATE = 42

# ── ML Pipeline ───────────────────────────────────────────────────────────
TEST_SIZE       = 0.25
CV_FOLDS        = 5
MAX_SAMPLE_SIZE = 150_000   # rows to load per CSV (None = all)

MODEL_NAMES = [
    "Random Forest",
    "XGBoost",
    "LightGBM",
]

# ── Label configuration ────────────────────────────────────────────────────
BENIGN_LABEL = "BENIGN"

# ── Combined label map: CIC-IDS2017 + CSE-CIC-IDS2018 ─────────────────────
# Keys are lowercase stripped strings → friendly unified label
ATTACK_LABEL_MAP = {

    # ── CIC-IDS2017 labels ────────────────────────────────────────────────
    "ddos"                             : "DDoS",
    "portscan"                         : "PortScan",
    "bot"                              : "Botnet",
    "infiltration"                     : "Infiltration",
    "web attack \x96 brute force"      : "Web-BruteForce",
    "web attack \u2013 brute force"    : "Web-BruteForce",
    "web attack - brute force"         : "Web-BruteForce",
    "web attack \x96 xss"             : "Web-XSS",
    "web attack \u2013 xss"           : "Web-XSS",
    "web attack - xss"                 : "Web-XSS",
    "web attack \x96 sql injection"    : "Web-SQLi",
    "web attack \u2013 sql injection"  : "Web-SQLi",
    "web attack - sql injection"       : "Web-SQLi",
    "ftp-patator"                      : "FTP-BruteForce",
    "ssh-patator"                      : "SSH-BruteForce",
    "dos slowloris"                    : "DoS-Slowloris",
    "dos slowhttptest"                 : "DoS-SlowHTTP",
    "dos hulk"                         : "DoS-Hulk",
    "dos goldeneye"                    : "DoS-GoldenEye",
    "heartbleed"                       : "Heartbleed",

    # ── CSE-CIC-IDS2018 labels ────────────────────────────────────────────
    # Note: 2018 uses lowercase "benign" — normalised here
    "benign"                           : "BENIGN",

    # DDoS variants (2018 has 3 DDoS tools)
    "ddos attack-hoic"                 : "DDoS",
    "ddos attack-loic-udp"             : "DDoS",
    "ddos attack-loic-http"            : "DDoS",

    # DoS variants (2018 renames them)
    "dos attacks-hulk"                 : "DoS-Hulk",
    "dos attacks-slowhttptest"         : "DoS-SlowHTTP",
    "dos attacks-slowloris"            : "DoS-Slowloris",
    "dos attacks-goldeneye"            : "DoS-GoldenEye",

    # Brute force (2018 format)
    "ssh-bruteforce"                   : "SSH-BruteForce",
    "ftp-bruteforce"                   : "FTP-BruteForce",
    "brute force -web"                 : "Web-BruteForce",
    "brute force -xss"                 : "Web-XSS",
    "sql injection"                    : "Web-SQLi",

    # 2018 has a typo in the label ("infilteration" with extra 'e')
    "infilteration"                    : "Infiltration",

    # Ransomware & new 2018 types
    "ransomware"                       : "Ransomware",
}

# ── Live Monitor ───────────────────────────────────────────────────────────
MONITOR_REFRESH_SEC  = 2      # dashboard auto-refresh interval
FLOW_BATCH_SIZE      = 5      # flows generated per tick per simulator
MAX_ALERTS_DISPLAY   = 200    # rows shown in SOC triage

# Confidence threshold to trigger a block (per attack family)
BLOCK_THRESHOLDS = {
    "DDoS"          : 0.01,
    "PortScan"      : 0.01,
    "SSH-BruteForce": 0.01,
    "FTP-BruteForce": 0.01,
    "DoS-Slowloris" : 0.01,
    "DoS-SlowHTTP"  : 0.01,
    "DoS-Hulk"      : 0.01,
    "DoS-GoldenEye" : 0.01,
    "Botnet"        : 0.01,
    "Ransomware"    : 0.01,
    "default"       : 0.01,
}

# Auto-unblock after N seconds (0 = permanent until manual)
BLOCK_DURATIONS = {
    "DDoS"          : 3600,
    "PortScan"      : 600,
    "SSH-BruteForce": 1800,
    "FTP-BruteForce": 1800,
    "DoS-Slowloris" : 900,
    "default"       : 300,
}

# ── Recommended SOC actions per attack type ────────────────────────────────
SOC_ACTIONS = {
    "DDoS"          : "Block source IP, rate-limit destination, alert NOC",
    "PortScan"      : "Block source IP for 10 min, log for investigation",
    "SSH-BruteForce": "Block source IP, enforce MFA on SSH, alert admin",
    "FTP-BruteForce": "Block source IP, disable FTP if unused",
    "DoS-Slowloris" : "Apply connection rate limit, block source IP",
    "DoS-SlowHTTP"  : "Apply connection timeout rules, block source IP",
    "DoS-Hulk"      : "Block source IP, scale load balancer",
    "DoS-GoldenEye" : "Block source IP, enable CDN protection",
    "Botnet"        : "Isolate host, run forensic scan, alert security team",
    "Ransomware"    : "Immediately isolate infected host, block C2 IPs, restore from backup",
    "Web-BruteForce": "Block IP, enforce CAPTCHA, alert web team",
    "Web-XSS"       : "Block IP, patch vulnerable endpoint, alert dev team",
    "Web-SQLi"      : "Block IP, patch vulnerable query, alert dev team",
    "Heartbleed"    : "Patch OpenSSL immediately, rotate all certificates",
    "Infiltration"  : "Isolate network segment, full forensic investigation",
    "BENIGN"        : "No action required",
    "default"       : "Investigate and escalate to security analyst",
}

# ── Simulated attacker IP pools (Option B) ────────────────────────────────
ATTACKER_IP_POOLS = {
    "DDoS"          : ("10.0.0.", 254),
    "PortScan"      : ("172.16.0.", 254),
    "SSH-BruteForce": ("192.168.100.", 254),
    "FTP-BruteForce": ("192.168.101.", 254),
    "DoS-Slowloris" : ("10.10.10.", 254),
    "DoS-SlowHTTP"  : ("10.10.11.", 254),
    "DoS-Hulk"      : ("10.20.0.", 254),
    "DoS-GoldenEye" : ("10.20.1.", 254),
    "Botnet"        : ("185.220.101.", 254),
    "Web-BruteForce": ("45.33.32.", 254),
    "Web-XSS"       : ("45.33.33.", 254),
    "Web-SQLi"      : ("45.33.34.", 254),
}

# ── Top 25 extractable live features (matches CIC-IDS2017 columns) ─────────
LIVE_FEATURES = [
    "Destination Port",
    "Flow Duration",
    "Total Fwd Packets",
    "Total Backward Packets",
    "Total Length of Fwd Packets",
    "Total Length of Bwd Packets",
    "Fwd Packet Length Max",
    "Fwd Packet Length Min",
    "Fwd Packet Length Mean",
    "Bwd Packet Length Max",
    "Bwd Packet Length Min",
    "Bwd Packet Length Mean",
    "Flow Bytes/s",
    "Flow Packets/s",
    "Flow IAT Mean",
    "Flow IAT Std",
    "Flow IAT Max",
    "Fwd IAT Mean",
    "Bwd IAT Mean",
    "Fwd PSH Flags",
    "SYN Flag Count",
    "RST Flag Count",
    "ACK Flag Count",
    "Avg Fwd Segment Size",
    "Avg Bwd Segment Size",
]

# ── UI Theme ───────────────────────────────────────────────────────────────
THEME = {
    "primary"   : "#00ff87",
    "secondary" : "#60efff",
    "danger"    : "#ff4757",
    "warning"   : "#feca57",
    "info"      : "#70a1ff",
    "bg"        : "#0a0a0a",
    "card_bg"   : "rgba(255,255,255,0.03)",
    "border"    : "rgba(255,255,255,0.07)",
}
