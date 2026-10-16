"""Hazard-zone geometry and dwell tracking. Pure Python: runs and is unit-tested on any machine."""
from dataclasses import dataclass, field

def point_in_polygon(x, y, poly):
    inside = False
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]; x2, y2 = poly[(i + 1) % n]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            inside = not inside
    return inside

def foot_point(bbox):
    """bbox = (left, top, width, height) -> bottom-centre of the box."""
    l, t, w, h = bbox
    return l + w / 2.0, t + h

@dataclass
class DwellTracker:
    polygon: list
    zone_name: str
    dwell_s: float = 2.0
    cooldown_s: float = 10.0
    _enter: dict = field(default_factory=dict)
    _last_alert: dict = field(default_factory=dict)

    def update(self, track_id, bbox, now):
        """Returns dwell seconds when an alert should fire for this track, else None."""
        x, y = foot_point(bbox)
        if not point_in_polygon(x, y, self.polygon):
            self._enter.pop(track_id, None)
            return None
        start = self._enter.setdefault(track_id, now)
        dwell = now - start
        if dwell >= self.dwell_s and now - self._last_alert.get(track_id, -1e9) >= self.cooldown_s:
            self._last_alert[track_id] = now
            return dwell
        return None

    def forget(self, live_ids):
        for tid in set(self._enter) - set(live_ids):
            self._enter.pop(tid, None)
