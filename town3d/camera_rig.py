"""Reusable camera-move presets for engine2.Camera2, with real easing
(cubic ease-in-out, not just linear lerp) -- used by the Phase 5 cinematic
sample. Every function returns a `pose(t)` callable, t in [0, 1], giving
(eye, target) for that fraction of the shot, so shots can be composed and
re-timed without duplicating interpolation math per scene.
"""
import math


def ease_in_out_cubic(t):
    if t < 0.5:
        return 4 * t * t * t
    p = -2 * t + 2
    return 1 - (p ** 3) / 2


def ease_out_quad(t):
    return 1 - (1 - t) ** 2


def _lerp3(a, b, t):
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))


def push_in(eye_far, eye_near, target, ease=ease_in_out_cubic):
    def pose(t):
        return _lerp3(eye_far, eye_near, ease(t)), target
    return pose


def pull_out(eye_near, eye_far, target, ease=ease_in_out_cubic):
    return push_in(eye_near, eye_far, target, ease)


def orbit(center, radius, height, start_deg, end_deg, target, ease=ease_in_out_cubic):
    def pose(t):
        ang = math.radians(start_deg + (end_deg - start_deg) * ease(t))
        eye = (center[0] + radius * math.cos(ang), height, center[2] + radius * math.sin(ang))
        return eye, target
    return pose


def tracking_shot(eye0, eye1, target0, target1, ease=ease_in_out_cubic):
    def pose(t):
        e = ease(t)
        return _lerp3(eye0, eye1, e), _lerp3(target0, target1, e)
    return pose


def low_angle(target, distance, height=0.35, azimuth_deg=0.0):
    ang = math.radians(azimuth_deg)
    eye = (target[0] + distance * math.sin(ang), height, target[2] + distance * math.cos(ang))
    return eye, target


def high_angle(target, distance, height, azimuth_deg=0.0):
    ang = math.radians(azimuth_deg)
    eye = (target[0] + distance * math.sin(ang), height, target[2] + distance * math.cos(ang))
    return eye, target


def aerial_descend(start_xyz, end_xyz, target_start, target_end, ease=ease_in_out_cubic):
    return tracking_shot(start_xyz, end_xyz, target_start, target_end, ease)


def compose_shots(shots):
    """shots: list of (duration_frames, pose_fn). Returns a single
    pose_at(frame_index, total_frames) function with per-shot timing."""
    total = sum(d for d, _ in shots)

    def pose_at(frame_idx):
        f = frame_idx
        for dur, pose_fn in shots:
            if f < dur:
                t = f / max(1, dur - 1)
                return pose_fn(min(1.0, t))
            f -= dur
        dur, pose_fn = shots[-1]
        return pose_fn(1.0)

    return pose_at, total
