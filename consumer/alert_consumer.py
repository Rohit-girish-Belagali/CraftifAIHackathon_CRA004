#!/usr/bin/env python3
"""Subscribe to PipeGen incident events and append them to incidents.jsonl.
--simulate emits fake events (source='SIMULATED') so the consumer can be tested without a GPU."""
import argparse, json, time, random, datetime

def handle(evt, path):
    with open(path, "a") as f:
        f.write(json.dumps(evt) + "\n")
    print(f"[INCIDENT] {evt['ts']} track={evt['track_id']} zone={evt['zone']} dwell={evt['dwell_s']}s source={evt['source']}")

def simulate(path, n=5):
    for i in range(n):
        handle({"ts": datetime.datetime.now().isoformat(timespec="seconds"), "track_id": i + 1, "class": "person",
                "zone": "press-line", "dwell_s": round(random.uniform(2, 6), 1), "bbox": [100, 80, 60, 140], "source": "SIMULATED"}, path)
        time.sleep(0.5)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--simulate", action="store_true")
    ap.add_argument("--broker", default="localhost")
    ap.add_argument("--topic", default="site/safety/incidents")
    ap.add_argument("--out", default="incidents.jsonl")
    a = ap.parse_args()
    if a.simulate:
        return simulate(a.out)
    import paho.mqtt.client as mqtt  # pip install paho-mqtt
    c = mqtt.Client()
    c.on_message = lambda cl, u, m: handle(json.loads(m.payload), a.out)
    c.connect(a.broker); c.subscribe(a.topic); c.loop_forever()

if __name__ == "__main__":
    main()
