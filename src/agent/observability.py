"""Structured logging and CloudWatch EMF metric helpers.

Two functions, one file. Replace this file to plug in OpenTelemetry or any
other telemetry backend — nothing else in the codebase should care.
"""

from __future__ import annotations

import json
import sys
import time
from typing import Any


def log_turn(level: str = "info", **fields: Any) -> None:
    """Write one JSON line to stdout — CloudWatch ingests it as a structured log."""
    payload: dict[str, Any] = {
        "ts": time.time(),
        "level": level,
        **fields,
    }
    print(json.dumps(payload, default=str), file=sys.stdout, flush=True)


def emit_emf(
    namespace: str,
    metrics: dict[str, tuple[float, str]],
    dimensions: dict[str, str] | None = None,
) -> None:
    """Emit a CloudWatch EMF (Embedded Metric Format) line.

    Args:
        namespace: CloudWatch namespace, e.g. ``BedrockAgent``.
        metrics: Mapping of metric name → ``(value, unit)``. Common units:
            ``"Count"``, ``"Milliseconds"``, ``"None"``.
        dimensions: Optional dimension key/value pairs (e.g. ``{"model_id": ...}``).
    """
    dims = dimensions or {}
    metric_directives = [{"Name": k, "Unit": u} for k, (_, u) in metrics.items()]
    emf: dict[str, Any] = {
        "_aws": {
            "Timestamp": int(time.time() * 1000),
            "CloudWatchMetrics": [
                {
                    "Namespace": namespace,
                    "Dimensions": [list(dims.keys())] if dims else [[]],
                    "Metrics": metric_directives,
                }
            ],
        },
        **dims,
        **{k: v for k, (v, _) in metrics.items()},
    }
    print(json.dumps(emf, default=str), file=sys.stdout, flush=True)
