"""
CyberShield AI — SQLite Database Layer
Handles alerts, blocked IPs, and run history.
"""

import sqlite3
import time
from datetime import datetime
from pathlib import Path
from contextlib import contextmanager
import sys, os
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import DB_PATH


# ── Connection helper ──────────────────────────────────────────────────────
@contextmanager
def get_conn():
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


# ── Schema ─────────────────────────────────────────────────────────────────
def init_db() -> None:
    """Create tables if they do not exist."""
    with get_conn() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS alerts (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp     TEXT    NOT NULL,
            source_ip     TEXT    NOT NULL,
            dest_port     INTEGER,
            attack_type   TEXT    NOT NULL,
            confidence    REAL    NOT NULL,
            risk_level    TEXT    NOT NULL,
            action        TEXT    NOT NULL,
            model_used    TEXT,
            flow_duration REAL,
            packet_count  INTEGER,
            bytes_rate    REAL
        );

        CREATE TABLE IF NOT EXISTS blocked_ips (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            ip          TEXT    NOT NULL UNIQUE,
            reason      TEXT,
            blocked_at  TEXT    NOT NULL,
            unblock_at  TEXT,
            active      INTEGER NOT NULL DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS model_runs (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            run_at         TEXT NOT NULL,
            dataset_path   TEXT,
            model_name     TEXT,
            accuracy       REAL,
            f1_score       REAL,
            precision      REAL,
            recall         REAL,
            auc_roc        REAL,
            mcc            REAL,
            training_time  REAL
        );
        """)


# ── Alert operations ───────────────────────────────────────────────────────
def insert_alert(
    source_ip: str,
    dest_port: int,
    attack_type: str,
    confidence: float,
    risk_level: str,
    action: str,
    model_used: str = "",
    flow_duration: float = 0.0,
    packet_count: int = 0,
    bytes_rate: float = 0.0,
) -> None:
    with get_conn() as conn:
        conn.execute(
            """INSERT INTO alerts
               (timestamp, source_ip, dest_port, attack_type, confidence,
                risk_level, action, model_used, flow_duration, packet_count, bytes_rate)
               VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
            (
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                source_ip, dest_port, attack_type,
                round(confidence, 4), risk_level, action,
                model_used, flow_duration, packet_count, bytes_rate,
            ),
        )


def get_alerts(limit: int = 200, attack_filter: str = "All") -> list[dict]:
    with get_conn() as conn:
        if attack_filter == "All":
            rows = conn.execute(
                "SELECT * FROM alerts ORDER BY id DESC LIMIT ?", (limit,)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM alerts WHERE attack_type=? ORDER BY id DESC LIMIT ?",
                (attack_filter, limit),
            ).fetchall()
    return [dict(r) for r in rows]


def get_alert_stats() -> dict:
    with get_conn() as conn:
        total   = conn.execute("SELECT COUNT(*) FROM alerts").fetchone()[0]
        attacks = conn.execute(
            "SELECT COUNT(*) FROM alerts WHERE attack_type != 'BENIGN'"
        ).fetchone()[0]
        blocked = conn.execute(
            "SELECT COUNT(*) FROM alerts WHERE action LIKE '%Block%'"
        ).fetchone()[0]
        by_type = conn.execute(
            "SELECT attack_type, COUNT(*) as cnt FROM alerts GROUP BY attack_type ORDER BY cnt DESC"
        ).fetchall()
    return {
        "total"  : total,
        "attacks": attacks,
        "benign" : total - attacks,
        "blocked": blocked,
        "by_type": [dict(r) for r in by_type],
    }


def clear_alerts() -> None:
    with get_conn() as conn:
        conn.execute("DELETE FROM alerts")


# ── Blocked IP operations ──────────────────────────────────────────────────
def block_ip(ip: str, reason: str, duration_sec: int = 3600) -> None:
    unblock_at = datetime.fromtimestamp(time.time() + duration_sec).strftime(
        "%Y-%m-%d %H:%M:%S"
    )
    with get_conn() as conn:
        conn.execute(
            """INSERT INTO blocked_ips (ip, reason, blocked_at, unblock_at, active)
               VALUES (?,?,?,?,1)
               ON CONFLICT(ip) DO UPDATE SET
                   reason=excluded.reason,
                   blocked_at=excluded.blocked_at,
                   unblock_at=excluded.unblock_at,
                   active=1""",
            (ip, reason, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), unblock_at),
        )


def unblock_ip(ip: str) -> None:
    with get_conn() as conn:
        conn.execute("UPDATE blocked_ips SET active=0 WHERE ip=?", (ip,))


def get_blocked_ips() -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM blocked_ips WHERE active=1 ORDER BY blocked_at DESC"
        ).fetchall()
    return [dict(r) for r in rows]


def expire_blocks() -> None:
    """Mark expired blocks as inactive."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with get_conn() as conn:
        conn.execute(
            "UPDATE blocked_ips SET active=0 WHERE unblock_at <= ? AND active=1", (now,)
        )


# ── Model run history ──────────────────────────────────────────────────────
def save_model_run(
    dataset_path: str,
    model_name: str,
    metrics: dict,
    training_time: float,
) -> None:
    with get_conn() as conn:
        conn.execute(
            """INSERT INTO model_runs
               (run_at, dataset_path, model_name, accuracy, f1_score,
                precision, recall, auc_roc, mcc, training_time)
               VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                dataset_path, model_name,
                metrics.get("accuracy"),
                metrics.get("f1"),
                metrics.get("precision"),
                metrics.get("recall"),
                metrics.get("roc_auc"),
                metrics.get("mcc"),
                training_time,
            ),
        )


def get_run_history() -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM model_runs ORDER BY id DESC LIMIT 50"
        ).fetchall()
    return [dict(r) for r in rows]


# Initialise on import
init_db()
