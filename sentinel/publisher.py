"""Publishes incident JSON to MQTT and always appends to a local JSONL log."""
import json, datetime

class Publisher:
    def __init__(self, broker=None, topic="site/safety/incidents", log_path="incidents.jsonl"):
        self.topic, self.log_path, self.client = topic, log_path, None
        if broker:
            import paho.mqtt.client as mqtt
            self.client = mqtt.Client()
            self.client.connect(broker)
            self.client.loop_start()

    def incident(self, track_id, zone, dwell_s, bbox, source="pipegen"):
        evt = {"ts": datetime.datetime.now().isoformat(timespec="seconds"), "track_id": int(track_id), "class": "person",
               "zone": zone, "dwell_s": round(dwell_s, 1), "bbox": [round(v) for v in bbox], "source": source}
        with open(self.log_path, "a") as f:
            f.write(json.dumps(evt) + "\n")
        if self.client:
            self.client.publish(self.topic, json.dumps(evt), qos=1)
        return evt
