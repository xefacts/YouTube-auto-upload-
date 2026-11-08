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


def check_temporal(frames_rgb: list, camera_positions: list) -> dict:
    """frames_rgb: list of HxWx3 uint8 arrays. camera_positions: list of
    (eye_xyz, target_xyz) per frame, same length. Returns objective
    temporal-consistency findings -- NOT an artistic score."""
    assert len(frames_rgb) == len(camera_positions)
    results = []
    deltas = []
    cam_steps = []
    for i in range(1, len(frames_rgb)):
        a = frames_rgb[i - 1].astype(np.float64)
        b = frames_rgb[i].astype(np.float64)
        delta = float(np.abs(a - b).mean())
        deltas.append(delta)
        (eye0, tgt0), (eye1, tgt1) = camera_positions[i - 1], camera_positions[i]
        step = float(np.linalg.norm(np.array(eye1) - np.array(eye0)) +
                     np.linalg.norm(np.array(tgt1) - np.array(tgt0)))
        cam_steps.append(step)

    if not deltas:
        return {"frames_checked": 0, "flicker_events": [], "discontinuity_events": []}

    mean_delta = float(np.mean(deltas))
    std_delta = float(np.std(deltas)) + 1e-6
    mean_step = float(np.mean(cam_steps)) + 1e-6

    flicker_events = []
    discontinuity_events = []
    for i, (d, s) in enumerate(zip(deltas, cam_steps), start=1):
        # Flicker: a big visual jump NOT explained by camera motion.
        expected_from_motion = s / mean_step * mean_delta
        if d > mean_delta + 3 * std_delta and d > 1.5 * max(expected_from_motion, 1e-6):
            flicker_events.append({"frame": i, "delta": round(d, 2), "expected": round(expected_from_motion, 2)})
        # Motion discontinuity: camera itself jumped much more than its own average step.
        if s > 4 * mean_step and mean_step > 1e-3:
            discontinuity_events.append({"frame": i, "camera_step": round(s, 4), "avg_step": round(mean_step, 4)})

    return {
        "frames_checked": len(frames_rgb),
        "mean_frame_delta": round(mean_delta, 3),
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
