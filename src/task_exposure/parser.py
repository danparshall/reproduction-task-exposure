"""Response parser for CDRF classification output.

Parses pipe-delimited model responses in both merged and per-axis reasoning formats.
"""

from __future__ import annotations


def parse_response(
    raw: str,
    reasoning_format: str = "merged",
    axes: list[str] | None = None,
) -> dict[str, dict[str, str]]:
    """Parse a pipe-delimited CDRF/CDR response into structured results.

    Args:
        raw: Raw model response text.
        reasoning_format: "merged" (7/6 columns), "per_axis" (10/8 columns),
            or "axis_dispute" (5 columns: task_id, axis, reasoning, rating, confidence).
        axes: Which axes were classified. Default ["C","D","R","F"].
            Pass ["C","D","R"] for CDR-only mode.

    Returns:
        Dict mapping task_id → {C, D, R, [F], conf, reasoning fields}.
        For axis_dispute format, only disputed axes are populated.
    """
    if axes is None:
        axes = ["C", "D", "R", "F"]
    if reasoning_format == "merged":
        return _parse_merged(raw, axes=axes)
    elif reasoning_format == "per_axis":
        return _parse_per_axis(raw, axes=axes)
    elif reasoning_format == "axis_dispute":
        return _parse_axis_dispute(raw)
    else:
        raise ValueError(
            f"reasoning_format must be 'merged', 'per_axis', or 'axis_dispute', "
            f"got '{reasoning_format}'"
        )


def _split_line(line: str) -> list[str]:
    """Split a response line by || delimiter, falling back to | if needed.

    Returns stripped parts. If || yields fewer than expected columns,
    tries single | as a fallback (handles known Opus delimiter issue).
    """
    if "||" in line:
        parts = [p.strip() for p in line.split("||")]
        return parts
    elif "|" in line:
        parts = [p.strip() for p in line.split("|")]
        return parts
    return []



def _is_header(parts: list[str]) -> bool:
    """Check if parts look like a header row."""
    return parts[0].lower().replace("_", "").startswith("taskid")


def _parse_merged(
    raw: str, axes: list[str] | None = None
) -> dict[str, dict[str, str]]:
    """Parse merged-reasoning format.

    CDRF (4 axes): task_id||reasoning||C||D||R||F||confidence  (7 columns)
    CDR  (3 axes): task_id||reasoning||C||D||R||confidence     (6 columns)
    """
    if axes is None:
        axes = ["C", "D", "R", "F"]
    n_axes = len(axes)
    min_cols = 2 + n_axes + 1  # task_id + reasoning + axes + confidence

    results = {}
    for line in raw.strip().splitlines():
        parts = _split_line(line)
        if len(parts) < min_cols:
            continue
        if _is_header(parts):
            continue
        task_id = parts[0]
        result = {"reasoning": parts[1]}
        for i, axis in enumerate(axes):
            result[axis] = parts[2 + i]
        result["conf"] = parts[2 + n_axes] if len(parts) > 2 + n_axes else "?"
        results[task_id] = result
    return results


def _parse_per_axis(
    raw: str, axes: list[str] | None = None
) -> dict[str, dict[str, str]]:
    """Parse per-axis reasoning format.

    CDRF (4 axes): task_id||c_r||d_r||r_r||f_r||C||D||R||F||conf  (10 columns)
    CDR  (3 axes): task_id||c_r||d_r||r_r||C||D||R||conf          (8 columns)
    """
    if axes is None:
        axes = ["C", "D", "R", "F"]
    n_axes = len(axes)
    min_cols = 1 + n_axes + n_axes + 1  # task_id + reasonings + ratings + confidence

    results = {}
    for line in raw.strip().splitlines():
        parts = _split_line(line)
        if len(parts) < min_cols:
            continue
        if _is_header(parts):
            continue
        task_id = parts[0]
        result = {}
        for i, axis in enumerate(axes):
            result[f"{axis.lower()}_reasoning"] = parts[1 + i]
        for i, axis in enumerate(axes):
            result[axis] = parts[1 + n_axes + i]
        result["conf"] = parts[1 + 2 * n_axes] if len(parts) > 1 + 2 * n_axes else "?"
        results[task_id] = result
    return results


_VALID_AXES = {"C", "D", "R", "F"}


def _parse_axis_dispute(raw: str) -> dict[str, dict[str, str]]:
    """Parse axis-dispute format (5 columns, one row per task×axis).

    Expected: task_id||axis||reasoning||rating||confidence

    Multiple rows for the same task_id are merged into a single dict.
    Only the disputed axes appear; unanimous axes are absent.

    Returns:
        Dict mapping task_id → {axis: rating, axis_reasoning: text, conf: text}.
        E.g. {"1839": {"F": "F2", "f_reasoning": "...", "conf": "HIGH"}}
    """
    results: dict[str, dict[str, str]] = {}
    for line in raw.strip().splitlines():
        parts = _split_line(line)
        if len(parts) < 5:
            continue
        if _is_header(parts):
            continue
        task_id = parts[0]
        axis = parts[1].upper().strip()
        if axis not in _VALID_AXES:
            continue
        reasoning = parts[2]
        rating = parts[3]
        confidence = parts[4] if len(parts) > 4 else "?"

        if task_id not in results:
            results[task_id] = {}
        results[task_id][axis] = rating
        results[task_id][f"{axis.lower()}_reasoning"] = reasoning
        # Use highest confidence across axes (last one wins for simplicity)
        results[task_id]["conf"] = confidence
    return results
