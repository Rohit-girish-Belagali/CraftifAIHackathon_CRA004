"""DeepStream pipeline: file/RTSP/USB -> nvinfer (TensorRT) -> nvtracker -> probe (zone check) -> OSD -> sink.
NOTE: written by hand, NOT exported by PipeGen and NOT yet run on an NVIDIA GPU. Needs DeepStream 7.x + pyds.
For the hackathon, replace this with PipeGen's exported app and keep zone.py/publisher.py as the action layer."""
import argparse, json, sys, time
import gi
gi.require_version("Gst", "1.0")
from gi.repository import Gst, GLib
import pyds
from sentinel.zone import DwellTracker
from sentinel.publisher import Publisher

PERSON_CLASS_ID = 0

def build(uri, pgie_cfg, tracker_cfg, sink):
    Gst.init(None)
    p = Gst.Pipeline()
    src = Gst.ElementFactory.make("uridecodebin", "src"); src.set_property("uri", uri)
    mux = Gst.ElementFactory.make("nvstreammux", "mux")
    for k, v in (("batch-size", 1), ("width", 1280), ("height", 720), ("batched-push-timeout", 40000)): mux.set_property(k, v)
    pgie = Gst.ElementFactory.make("nvinfer", "pgie"); pgie.set_property("config-file-path", pgie_cfg)
    trk = Gst.ElementFactory.make("nvtracker", "trk")
    trk.set_property("ll-lib-file", "/opt/nvidia/deepstream/deepstream/lib/libnvds_nvmultiobjecttracker.so")
    trk.set_property("ll-config-file", tracker_cfg)
    conv = Gst.ElementFactory.make("nvvideoconvert", "conv"); osd = Gst.ElementFactory.make("nvdsosd", "osd")
    out = Gst.ElementFactory.make("nveglglessink" if sink == "display" else "fakesink", "out"); out.set_property("sync", False)
    for e in (src, mux, pgie, trk, conv, osd, out): p.add(e)
    src.connect("pad-added", lambda s, pad: pad.link(mux.get_request_pad("sink_0")))
    mux.link(pgie); pgie.link(trk); trk.link(conv); conv.link(osd); osd.link(out)
    return p, osd

def make_probe(tracker, pub):
    def probe(pad, info, _):
        batch = pyds.gst_buffer_get_nvds_batch_meta(hash(info.get_buffer()))
        l = batch.frame_meta_list
        while l:
            fm = pyds.NvDsFrameMeta.cast(l.data); live = []
            o = fm.obj_meta_list
            while o:
                ob = pyds.NvDsObjectMeta.cast(o.data)
                if ob.class_id == PERSON_CLASS_ID:
                    r = ob.rect_params; bbox = (r.left, r.top, r.width, r.height); live.append(ob.object_id)
                    dwell = tracker.update(ob.object_id, bbox, time.time())
                    if dwell is not None:
                        print(pub.incident(ob.object_id, tracker.zone_name, dwell, bbox))
                o = o.next
            tracker.forget(live); l = l.next
        return Gst.PadProbeReturn.OK
    return probe

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--uri", required=True, help="file:///..., rtsp://..., or v4l2 via a wrapper")
    ap.add_argument("--zones", default="configs/zones.json"); ap.add_argument("--pgie", default="configs/pgie_config.txt")
    ap.add_argument("--tracker", default="configs/tracker_config.yml"); ap.add_argument("--broker"); ap.add_argument("--sink", default="display")
    a = ap.parse_args()
    z = json.load(open(a.zones))
    tracker = DwellTracker(z["polygon"], z["name"], z.get("dwell_s", 2.0))
    pipe, osd = build(a.uri, a.pgie, a.tracker, a.sink)
    osd.get_static_pad("sink").add_probe(Gst.PadProbeType.BUFFER, make_probe(tracker, Publisher(a.broker)), None)
    loop = GLib.MainLoop(); bus = pipe.get_bus(); bus.add_signal_watch()
    bus.connect("message", lambda b, m: loop.quit() if m.type in (Gst.MessageType.EOS, Gst.MessageType.ERROR) else None)
    pipe.set_state(Gst.State.PLAYING)
    try: loop.run()
    finally: pipe.set_state(Gst.State.NULL)

if __name__ == "__main__":
    sys.exit(main())
