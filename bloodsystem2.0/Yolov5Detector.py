# -*- coding: utf-8 -*-
# @Time    : 2021/4/23 下午7:56
# @Author  : red0orange
# @File    : Yolov5Detector.py
# @Content :
import sys
import os
import cv2
import numpy as np
import time
from openvino.inference_engine import IECore
import logging

logger = logging.getLogger("root.yolov5_detector")


class OpenVinoDetector(object):
    def __init__(self):
        raise BaseException("")
        pass

    def preprocess(self, image):
        raise BaseException("")
        pass

    def postprocess(self, outputs):
        raise BaseException("")
        pass


class Yolov5Detector(OpenVinoDetector):
    def __init__(self, model_xml, model_bin, conf_thres=0.25, iou_thres=0.45, print_result=False):
        self.print_result = print_result
        self.conf_thres = conf_thres
        self.iou_thres = iou_thres
        self.img_size = (640, 640)
        self.stride = 32

        self.ie_core = IECore()
        self.network = self.ie_core.read_network(model=model_xml, weights=model_bin)

        supported_layers = self.ie_core.query_network(self.network, "CPU")

        assert len(self.network.inputs.keys()) == 1, "error: model should one input"
        assert len(self.network.outputs) == 3, "error: model should 3 output"

        print("Preparing input blobs")
        self.image_input_key = list(self.network.inputs.keys())[0]
        image_input = self.network.inputs[self.image_input_key]
        assert len(image_input.shape) == 4 and image_input.shape[0] == 1 and image_input.shape[1] == 3 and \
               image_input.shape[2] == 640 and image_input.shape[3] == 640, "error: input shape not fix !"

        # prepare input image buffer
        n, c, h, w = self.network.inputs[self.image_input_key].shape
        self.images = np.ndarray(shape=(n, c, h, w))

        self.output_keys = list(self.network.outputs.keys())
        self.outputs = [self.network.outputs[i] for i in self.output_keys]
        assert len(self.outputs[0].shape) == 4, "error: output shape not fix!"

        # Loading model to the plugin
        print("Loading model to the plugin")
        self.exec_net = self.ie_core.load_network(network=self.network, device_name="CPU")

        # Load Yolo detect params
        self.grid_sizes = [80, 40, 20]
        self.layer_names = self.output_keys
        self.per_box_num = 3
        anchors = [
            [10, 13, 16, 30, 33, 23],
            [30, 61, 62, 45, 59, 119],
            [116, 90, 156, 198, 373, 326]
        ]
        self.anchor_grid = np.array(anchors).reshape([len(self.grid_sizes), 1, -1, 1, 1, 2])

        pass

    @staticmethod
    def letterbox(img, new_shape=(640, 640), color=(114, 114, 114), auto=True, scaleFill=False, scaleup=True,
                  stride=32):
        # Resize and pad image while meeting stride-multiple constraints
        shape = img.shape[:2]  # current shape [height, width]
        if isinstance(new_shape, int):
            new_shape = (new_shape, new_shape)

        # Scale ratio (new / old)
        r = min(new_shape[0] / shape[0], new_shape[1] / shape[1])
        if not scaleup:  # only scale down, do not scale up (for better test mAP)
            r = min(r, 1.0)

        # Compute padding
        ratio = r, r  # width, height ratios
        new_unpad = int(round(shape[1] * r)), int(round(shape[0] * r))
        dw, dh = new_shape[1] - new_unpad[0], new_shape[0] - new_unpad[1]  # wh padding
        if auto:  # minimum rectangle
            dw, dh = np.mod(dw, stride), np.mod(dh, stride)  # wh padding
        elif scaleFill:  # stretch
            dw, dh = 0.0, 0.0
            new_unpad = (new_shape[1], new_shape[0])
            ratio = new_shape[1] / shape[1], new_shape[0] / shape[0]  # width, height ratios

        dw /= 2  # divide padding into 2 sides
        dh /= 2

        if shape[::-1] != new_unpad:  # resize
            img = cv2.resize(img, new_unpad, interpolation=cv2.INTER_LINEAR)
        top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
        left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
        img = cv2.copyMakeBorder(img, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)  # add border
        return img, ratio, (dw, dh)

    @staticmethod
    def xyxy2xywh(x):
        # Convert nx4 boxes from [x1, y1, x2, y2] to [x, y, w, h] where xy1=top-left, xy2=bottom-right
        y = np.copy(x)
        y[:, 0] = (x[:, 0] + x[:, 2]) / 2  # x center
        y[:, 1] = (x[:, 1] + x[:, 3]) / 2  # y center
        y[:, 2] = x[:, 2] - x[:, 0]  # width
        y[:, 3] = x[:, 3] - x[:, 1]  # height
        return y

    @staticmethod
    def xywh2xyxy(x):
        # Convert nx4 boxes from [x, y, w, h] to [x1, y1, x2, y2] where xy1=top-left, xy2=bottom-right
        y = np.copy(x)
        y[:, 0] = x[:, 0] - x[:, 2] / 2  # top left x
        y[:, 1] = x[:, 1] - x[:, 3] / 2  # top left y
        y[:, 2] = x[:, 0] + x[:, 2] / 2  # bottom right x
        y[:, 3] = x[:, 1] + x[:, 3] / 2  # bottom right y
        return y

    @staticmethod
    def scale_bbox(x, y, height, width, class_id, confidence, im_h, im_w, resized_im_h=640, resized_im_w=640):
        gain = min(resized_im_w / im_w, resized_im_h / im_h)  # gain  = old / new
        pad = (resized_im_w - im_w * gain) / 2, (resized_im_h - im_h * gain) / 2  # wh padding
        x = int((x - pad[0]) / gain)
        y = int((y - pad[1]) / gain)

        w = int(width / gain)
        h = int(height / gain)

        xmin = max(0, int(x - w / 2))
        ymin = max(0, int(y - h / 2))
        xmax = min(im_w, int(xmin + w))
        ymax = min(im_h, int(ymin + h))
        # Method item() used here to convert NumPy types to native types for compatibility with functions, which don't
        # support Numpy types (e.g., cv2.rectangle doesn't support int64 in color parameter)
        return dict(xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax, class_id=class_id.item(), confidence=confidence.item())

    @staticmethod
    def intersection_over_union(box_1, box_2):
        width_of_overlap_area = min(box_1['xmax'], box_2['xmax']) - max(box_1['xmin'], box_2['xmin'])
        height_of_overlap_area = min(box_1['ymax'], box_2['ymax']) - max(box_1['ymin'], box_2['ymin'])
        if width_of_overlap_area < 0 or height_of_overlap_area < 0:
            area_of_overlap = 0
        else:
            area_of_overlap = width_of_overlap_area * height_of_overlap_area
        box_1_area = (box_1['ymax'] - box_1['ymin']) * (box_1['xmax'] - box_1['xmin'])
        box_2_area = (box_2['ymax'] - box_2['ymin']) * (box_2['xmax'] - box_2['xmin'])
        area_of_union = box_1_area + box_2_area - area_of_overlap
        if area_of_union == 0:
            return 0
        return area_of_overlap / area_of_union

    @staticmethod
    def make_grid(nx=20, ny=20):
        yv, xv = np.meshgrid(np.arange(ny), np.arange(nx))
        return np.stack((yv, xv), 2).reshape(1, 1, ny, nx, 2)

    def parser_yolo_output(self, idx, blob, resized_image_shape, original_im_shape, threshold):
        out_blob_c, out_blob_h, out_blob_w = blob.shape
        predictions = 1.0 / (1.0 + np.exp(-blob))

        assert out_blob_w == out_blob_h, "Invalid size of output blob. It sould be in NCHW layout and height should " \
                                         "be equal to width. Current height = {}, current width = {}" \
                                         "".format(out_blob_h, out_blob_w)

        origin_image_h, origin_image_w = original_im_shape
        resized_image_h, resized_image_w = resized_image_shape

        stride = (resized_image_w / out_blob_w)
        grid = Yolov5Detector.make_grid(out_blob_w, out_blob_h)

        predictions = predictions.reshape([self.per_box_num, out_blob_c // self.per_box_num,
                                           predictions.shape[-2], predictions.shape[-1]]).transpose(0, 2, 3, 1)
        predictions = np.ascontiguousarray(predictions)
        predictions[..., 0:2] = (predictions[..., 0:2] * 2. - 0.5 + grid) * stride  # xy
        predictions[..., 2:4] = (predictions[..., 2:4] * 2) ** 2 * self.anchor_grid[idx]  # wh
        predictions = predictions.reshape(-1, predictions.shape[-1])
        predictions = predictions[predictions[:, 4] > threshold]

        gain = min(resized_image_w / origin_image_w, resized_image_h / origin_image_h)  # gain  = old / new
        pad = (resized_image_w - origin_image_w * gain) / 2, (resized_image_h - origin_image_h * gain) / 2  # wh padding
        predictions[:, 0] = (predictions[:, 0] - pad[0]) / gain
        predictions[:, 1] = (predictions[:, 1] - pad[1]) / gain
        predictions[:, 2] = predictions[:, 2] / gain
        predictions[:, 3] = predictions[:, 3] / gain

        return predictions

    def preprocess(self, image):
        img = self.letterbox(image, self.img_size, stride=self.stride, auto=False, scaleFill=False)[0]
        img = img[:, :, ::-1].transpose(2, 0, 1)
        img = np.ascontiguousarray(img)
        return img / 255.0

    def postprocess(self, outputs, ori_img_size):
        dimensions = int(self.outputs[0].shape[1] / self.per_box_num)
        result = np.zeros([0, dimensions], dtype=np.float)
        for i in range(len(self.layer_names)):
            layer_result = self.parser_yolo_output(i, outputs[self.layer_names[i]][0], self.img_size[::-1], ori_img_size[::-1], self.conf_thres)
            result = np.concatenate([result, layer_result], axis=0)
            pass
        result[:, 5:] *= result[:, 4][:, None]
        result = np.concatenate([result[:, :4], np.max(result[:, 5:], axis=1)[:, None], np.argmax(result[:, 5:], axis=1)[:, None]], axis=1)
        boxes, score, class_id = result[:, :4], result[:, 4], result[:, 5]
        index = cv2.dnn.NMSBoxes(boxes.tolist(), score.tolist(), self.conf_thres, self.iou_thres)
        if len(index) != 0:
            index = index.squeeze()
        result = result[index]

        # print result
        if self.print_result:
            if len(result):
                print("\nDetected boxes for batch {}:".format(1))
                print(" Class ID | Confidence | X | Y | WIDTH | HEIGHT | COLOR ")
            for obj in result:
                x, y, width, height, conf, class_id = obj
                color = (int(min(class_id * 12.5, 255)),
                         min(class_id * 7, 255), min(class_id * 5, 255))
                det_label = str(class_id)

                print(
                    "{:^9} | {:10f} | {:4} | {:4} | {:4} | {:4} | {} ".format(det_label, conf, x, y, width, height, color))
        return result

    def detect(self, images):
        """
        输入单张图片或者包含多张图片的列表
        """

        one_image_flag = not(isinstance(images, list) or isinstance(images, tuple))
        if one_image_flag:
            images = [images]

        begin = time.perf_counter()
        preprocess_images = [self.preprocess(image) for image in images]
        batch_result = []
        end = time.perf_counter()
        logger.info('yolov5 detector preprocess time: {}'.format(end - begin))

        for image in preprocess_images:
            begin = time.perf_counter()
            self.images[0] = image
            outputs = self.exec_net.infer(inputs={self.image_input_key: self.images})
            end = time.perf_counter()
            logger.info('yolov5 detector infer time: {}'.format(end - begin))

            begin = time.perf_counter()
            predict = self.postprocess(outputs, images[0].shape[:2][::-1])
            if len(predict.shape) == 1:
                predict = predict[None, ...]
            end = time.perf_counter()
            logger.info('yolov5 detector postprocess time: {}'.format(end - begin))
            batch_result.append(predict)

        # for i in range(len(images)):
        #     show_image = images[i].copy()
        #     image_predict = batch_result[i]
        #     for obj in image_predict:
        #         x, y, width, height, conf, class_id = obj
        #         x1, y1, x2, y2 = int(x - width // 2), int(y - height // 2), int(x + width // 2), int(y + height // 2)
        #         cv2.rectangle(show_image, (x1, y1), (x2, y2), (127, 255, 0), 2)
        #     cv2.imshow("show", show_image)
        #     cv2.waitKey(0)

        return_result = [i.tolist() for i in batch_result]

        if one_image_flag:
            return_result = return_result[0]
        return return_result
