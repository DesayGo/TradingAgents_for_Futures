#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Lightweight JSONL trace logging for long-running analysis stages."""

import json
import os
import threading
from datetime import datetime
from pathlib import Path
from typing import Any

_LOCK = threading.Lock()


def trace_event(event: str, run_id: str = "", **fields: Any) -> None:
    """Append one trace event to logs/analysis_trace.log.

    This logger intentionally avoids the global logging configuration so traces
    remain available even when Streamlit or imported modules override logging.
    """
    try:
        payload = {
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
            "pid": os.getpid(),
            "thread": threading.current_thread().name,
            "run_id": run_id,
            "event": event,
            **fields,
        }
        log_path = Path(__file__).resolve().parent / "logs" / "analysis_trace.log"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        line = json.dumps(payload, ensure_ascii=False, default=str)
        with _LOCK:
            with log_path.open("a", encoding="utf-8") as fh:
                fh.write(line + "\n")
    except Exception:
        # Trace logging must never break analysis execution.
        pass
