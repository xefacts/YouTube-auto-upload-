"""Artistic / cinematic QC, kept strictly separate from town3d/qc.py's
technical pixel-statistics QC (brightness/contrast/sharpness). Per the
user's explicit instruction: "Do not give a high artistic score based only
on brightness and sharpness" and "Technical success must never be reported
as artistic success."

Two tiers here, clearly labelled:

1. OBJECTIVELY MEASURABLE temporal checks (still computed from pixels, but
   they measure something an artistic eye actually cares about -- sudden
   frame-to-frame jumps -- not just "is this pixel bright"):
     - temporal_flicker: large whole-frame color change between consecutive
       frames with no corresponding camera/pose motion (symptom of z-fighting
       or render nondeterminism).
     - motion_discontinuity: frame-to-frame camera eye/target jump larger
       than the shot's own average step (symptom of a bad keyframe/easing bug).

2. GENUINELY SUBJECTIVE checks that CANNOT be reduced to a pixel formula --
   geometry defects, character deformation, camera clipping, shadow
   artifacts, character consistency, visual composition, narration
   relevance. These are filled in by a human (or an LLM actually looking at
   the rendered frames), not computed. This module only provides the
   structure to record that review honestly; it does not fake a score.
"""
from dataclasses import dataclass, field
from typing import Optional

import numpy as np


@dataclass
class TemporalCheck:
    frame_index: int
    whole_frame_delta: float
    camera_step: float
    flagged: bool
    reason: str = ""


def check_temporal(frames_rgb: list, camera_positions: list, shot_boundaries: list = None) -> dict:
    """frames_rgb: list of HxWx3 uint8 arrays. camera_positions: list of
    (eye_xyz, target_xyz) per frame, same length. shot_boundaries: optional
    list of frame indices where an INTENTIONAL hard cut to a new shot occurs
    (e.g. [38, 81, 119, ...] for a sequence of fixed-length shots) -- these
    are expected large jumps, not defects, and are excluded from both checks.
    Also normalizes against each frame's own shot (not one global average),
    because different shots legitimately move the camera at very different
    speeds (a wide establishing pan covers far more distance per frame than
    a close-up), and an eased camera move is naturally fastest in its middle
    -- comparing every frame to a single whole-video average otherwise flags
    both real cuts and the fast middle of normal ease curves as false
    positives (observed and corrected during this project's own QC pass).
    Returns objective temporal-consistency findings -- NOT an artistic score."""
    assert len(frames_rgb) == len(camera_positions)
    shot_boundaries = set(shot_boundaries or [])
    deltas = []
    cam_steps = []
    for i in range(1, len(frames_rgb)):
        a = frames_rgb[i - 1].astype(np.float64)
        b = frames_rgb[i].astype(np.float64)
        deltas.append(float(np.abs(a - b).mean()))
        (eye0, tgt0), (eye1, tgt1) = camera_positions[i - 1], camera_positions[i]
        cam_steps.append(float(np.linalg.norm(np.array(eye1) - np.array(eye0)) +
                                np.linalg.norm(np.array(tgt1) - np.array(tgt0))))

    if not deltas:
        return {"frames_checked": 0, "flicker_events": [], "discontinuity_events": [], "pass": True}

    # Per-frame local expectation: median of a +/-12 frame window (robust to
    # one shot's overall speed being very different from another's), instead
    # of a single global average across the whole clip.
    W = 12
    n = len(deltas)
    flicker_events, discontinuity_events = [], []
    for idx in range(n):
        frame_i = idx + 1  # deltas[idx] is the jump arriving at frame_i
        if frame_i in shot_boundaries:
            continue  # an intentional cut is SUPPOSED to jump -- not a defect
        lo, hi = max(0, idx - W), min(n, idx + W + 1)
        window_d = [deltas[j] for j in range(lo, hi) if (j + 1) not in shot_boundaries]
        window_s = [cam_steps[j] for j in range(lo, hi) if (j + 1) not in shot_boundaries]
        local_mean_d = float(np.median(window_d)) if window_d else deltas[idx]
        local_std_d = float(np.std(window_d)) + 1e-6
        local_mean_s = float(np.median(window_s)) + 1e-6 if window_s else cam_steps[idx] + 1e-6

        d, s = deltas[idx], cam_steps[idx]
        expected_from_motion = (s / local_mean_s) * local_mean_d
        if d > local_mean_d + 4 * local_std_d and d > 1.6 * max(expected_from_motion, 1e-6):
            flicker_events.append({"frame": frame_i, "delta": round(d, 2), "local_expected": round(expected_from_motion, 2)})
        if s > 5 * local_mean_s and local_mean_s > 1e-3:
            discontinuity_events.append({"frame": frame_i, "camera_step": round(s, 4), "local_avg_step": round(local_mean_s, 4)})

    return {
        "frames_checked": len(frames_rgb),
        "shot_boundaries_excluded": sorted(shot_boundaries),
        "mean_frame_delta": round(float(np.mean(deltas)), 3),
        "flicker_events": flicker_events,
        "discontinuity_events": discontinuity_events,
        "pass": len(flicker_events) == 0 and len(discontinuity_events) == 0,
    }


@dataclass
class SubjectiveReview:
    """Filled in manually after actually looking at rendered frames.
    `status` must be one of pass/warning/fail; `evidence` should name which
    frame(s) were inspected. Leaving a field as None means "not reviewed",
    which is reported as such -- never silently treated as a pass."""
    geometry_defects: Optional[dict] = None
    character_deformation: Optional[dict] = None
    camera_clipping: Optional[dict] = None
    shadow_artifacts: Optional[dict] = None
    character_consistency: Optional[dict] = None
    visual_composition: Optional[dict] = None
    narration_relevance: Optional[dict] = None

    def as_report(self):
        fields = ["geometry_defects", "character_deformation", "camera_clipping",
                  "shadow_artifacts", "character_consistency", "visual_composition",
                  "narration_relevance"]
        out = {}
        reviewed = 0
        passed = 0
        for f in fields:
            v = getattr(self, f)
            if v is None:
                out[f] = {"status": "NOT_REVIEWED"}
            else:
                out[f] = v
                reviewed += 1
                if v.get("status") == "pass":
                    passed += 1
        out["_summary"] = {
            "criteria_total": len(fields),
            "criteria_reviewed": reviewed,
            "criteria_passed": passed,
            "fully_reviewed": reviewed == len(fields),
        }
        return out
