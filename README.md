# PipeGen Workplace Safety Sentinel (Track A scaffold)

Hackathon: Embedded SF CraftifAI Physical AI Hackathon, https://luma.com/5z8w42mq

## Status (honest)
This repo is a **scaffold**. The PipeGen pipeline has **not** been built or run: the author's machine (Apple M4 Mac) has no NVIDIA GPU or Jetson. No TensorRT engine, speed report or live run exists. The consumer below is tested only against simulated events.

## Plan
Person detection + hazard-zone check on a site camera. PipeGen compiles the detector to TensorRT (FP16/INT8), runs it in DeepStream and publishes JSON incident events over MQTT. See `docs/PIPEGEN_REQUIREMENT.md` for the requirement text to paste into PipeGen's Requirement stage.

## Files
- `sentinel/zone.py` : polygon + dwell/cooldown logic (**5 unit tests pass**, `python3 -m unittest discover -s tests -t .`)
- `sentinel/publisher.py` : MQTT + JSONL incident publisher
- `sentinel/deepstream_app.py` : DeepStream/pyds pipeline with zone probe (**hand-written, untested on a GPU**)
- `configs/` : nvinfer, tracker, zone and label configs; `run.sh` launcher
- `docs/PIPEGEN_REQUIREMENT.md` : requirement prompt and expected output schema
- `consumer/alert_consumer.py` : MQTT subscriber that logs incidents to JSONL (`--simulate` generates fake events, clearly marked)

## Run the consumer (no GPU needed)
    python3 consumer/alert_consumer.py --simulate
