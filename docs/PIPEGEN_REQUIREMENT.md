# Requirement prompt for PipeGen
"Detect people on a video stream from a site camera. Define a polygon hazard zone. When a person's bounding-box bottom-centre stays inside the zone for 2 seconds, publish a JSON incident to MQTT topic `site/safety/incidents` and save an annotated clip. Use a TensorRT FP16 person detector with tracking. Report latency per stage."

## Event schema (JSON)
{"ts": "ISO-8601", "track_id": 7, "class": "person", "zone": "press-line", "dwell_s": 2.4, "bbox": [x,y,w,h], "source": "pipegen"}
