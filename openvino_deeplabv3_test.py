import sys
import os
from argparse import ArgumentParser
import numpy as np
import cv2
import time
from PIL import Image
import tensorflow as tf
from tensorflow.python.platform import gfile
try:
    from armv7l.openvino.inference_engine import IENetwork, IEPlugin
except:
    from openvino.inference_engine import IENetwork, IEPlugin

class _model_preprocess():
    def __init__(self):
        graph = tf.Graph()
        f_handle = gfile.FastGFile("pbmodels/PascalVOC/frozen_inference_graph.pb", "rb")
        graph_def = tf.GraphDef.FromString(f_handle.read())
        with graph.as_default():
            tf.import_graph_def(graph_def, name='')
        self. sess = tf.Session(graph=graph)

    def _pre_process(self, image):
        seg_map = self.sess.run("sub_7:0", feed_dict={"ImageTensor:0": [image]})
        return seg_map


class _model_postprocess():
    def __init__(self):
        graph = tf.Graph()
        f_handle = gfile.FastGFile("pbmodels/PascalVOC/frozen_inference_graph.pb", "rb")
        graph_def = tf.GraphDef.FromString(f_handle.read())
        with graph.as_default():
            new_input = tf.placeholder(tf.int64, shape=(1, 513, 513), name="new_input")
            tf.import_graph_def(graph_def, input_map={"ArgMax:0": new_input}, name='')
        self.sess = tf.Session(graph=graph)

    def _post_process(self, image_ir, image):
        seg_map = self.sess.run("SemanticPredictions:0", feed_dict={"ImageTensor:0": [image], "new_input:0": np.int64(image_ir)})
        return seg_map


_pre = _model_preprocess()
_post = _model_postprocess()


def build_argparser():
    parser = ArgumentParser()
    parser.add_argument("-pp", "--plugin_dir", help="Path to a plugin folder", type=str, default=None)
    parser.add_argument("-d", "--device", help="Specify the target device to infer on; CPU, GPU, FPGA or MYRIAD is acceptable. Sample will look for a suitable plugin for device specified (CPU by default)", default="CPU", type=str)
    parser.add_argument("-nt", "--number_top", help="Number of top results", default=10, type=int)
    parser.add_argument("-pc", "--performance", help="Enables per-layer performance report", action='store_true')

    return parser


def main_IE_infer():
    camera_width = 320
    camera_height = 240
    m_input_size=513
    fps = ""
    framepos = 0
    frame_count = 0
    vidfps = 0
    skip_frame = 0
    elapsedTime = 0

    args = build_argparser().parse_args()
    #model_xml = "lrmodels/PascalVOC/FP32/frozen_inference_graph.xml" #<--- CPU
    model_xml = "lrmodels/PascalVOC/FP16/frozen_inference_graph.xml" #<--- MYRIAD
    model_bin = os.path.splitext(model_xml)[0] + ".bin"

    seg_image = Image.open("data/input/009649.png")
    palette = seg_image.getpalette() # Get a color palette

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FPS, 10)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, camera_width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, camera_height)

    #cap = cv2.VideoCapture("data/input/testvideo.mp4")
    #camera_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    #camera_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    #frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    #vidfps = int(cap.get(cv2.CAP_PROP_FPS))
    #print("videosFrameCount =", str(frame_count))
    #print("videosFPS =", str(vidfps))

    time.sleep(1)

    plugin = IEPlugin(device=args.device, plugin_dirs=args.plugin_dir)
    if "CPU" in args.device:
        plugin.add_cpu_extension("lib/libcpu_extension.so")
    if args.performance:
        plugin.set_config({"PERF_COUNT": "YES"})
    # Read IR
    net = IENetwork(model=model_xml, weights=model_bin)
    input_blob = next(iter(net.inputs))
    exec_net = plugin.load(network=net)

    while cap.isOpened():
        t1 = time.time()

        #cap.set(cv2.CAP_PROP_POS_FRAMES, framepos)     # Uncomment only when playing video files

        ret, image = cap.read()
        if not ret:
            break

        ratio = 1.0 * m_input_size / max(image.shape[0], image.shape[1])
        shrink_size = (int(ratio * image.shape[1]), int(ratio * image.shape[0]))
        image = cv2.resize(image, shrink_size, interpolation=cv2.INTER_CUBIC)

        prepimg = _pre._pre_process(image)
        prepimg = prepimg.transpose((0, 3, 1, 2))  #NHWC to NCHW
        res = exec_net.infer(inputs={input_blob: prepimg})
        result = _post._post_process(res["ArgMax/Squeeze"], image)[0]

        outputimg = Image.fromarray(np.uint8(result), mode="P")
        outputimg.putpalette(palette)
        outputimg = outputimg.convert("RGB")
        outputimg = np.asarray(outputimg)
        outputimg = cv2.cvtColor(outputimg, cv2.COLOR_RGB2BGR)
        outputimg = cv2.addWeighted(image, 1.0, outputimg, 0.9, 0)
        outputimg = cv2.resize(outputimg, (camera_width, camera_height))

        cv2.putText(outputimg, fps, (camera_width-180,15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (38,0,255), 1, cv2.LINE_AA)
        cv2.imshow("Result", outputimg)

        if cv2.waitKey(1)&0xFF == ord('q'):
            break
        elapsedTime = time.time() - t1
        fps = "(Playback) {:.1f} FPS".format(1/elapsedTime)

        # frame skip, video file only
        skip_frame = int((vidfps - int(1/elapsedTime)) / int(1/elapsedTime))
        framepos += skip_frame

    cv2.destroyAllWindows()
    del net
    del exec_net
    del plugin


if __name__ == '__main__':
    sys.exit(main_IE_infer() or 0)
