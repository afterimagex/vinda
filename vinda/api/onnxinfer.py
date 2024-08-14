import os
# import cv2
import onnxruntime
import numpy as np

from vinda.api.utils import Timer
from vinda.api.trainer import ImageTransform
from vinda.api.pattern import SingletonBase

class OrtEngine:
    '''模型'''
    _TIMER_STAGE = ('PreProcess', 'Forward', 'PostProcess')

    def __init__(self, onnxfile):
        self._file = onnxfile
        self._sess = onnxruntime.InferenceSession(onnxfile)
        self._timer = Timer.new(*OrtEngine._TIMER_STAGE)

    def computation_metrics(self):
        device = onnxruntime.get_device()
        metrics = {
            'Evaluating Model': os.path.basename(self._file),
            'Inputs': [f'{x.name}={x.shape}' for x in self._sess.get_inputs()],
            'Outputs': [f'{x.name}={x.shape}' for x in self._sess.get_outputs()],
            'Total Calls': self._timer['Forward'].calls,
        }
        metrics.update({
            f'[{device}] BS: 1 Elapsed Time {x}': f"{self._timer[x].average_time * 1000:.6f} ms"
            for x in OrtEngine._TIMER_STAGE
        })
        return metrics

    # @staticmethod
    # def resize_and_pad(img, dsize=(640, 640), channel=3, color=255):
    #     '''
    #     :param img: (H, W, C)
    #     :param dsize: (W, H)
    #     :return:
    #     '''
    #     h, w = img.shape[:2]
    #     if dsize[0] == -1:
    #         ratio = 1.0 * dsize[1] / h
    #         resized = cv2.resize(img, None, fx=ratio, fy=ratio)
    #         if channel == 1:
    #             resized = resized[..., np.newaxis]
    #         if resized.shape[1] % 32 != 0:
    #             newW = int((resized.shape[1] / 32.0 + 1.0) * 32)
    #             newI = np.zeros((dsize[1], newW, channel), dtype=np.uint8) + color
    #             newI[:resized.shape[0], :resized.shape[1]] = resized
    #             resized = newI
    #     else:
    #         if (1.0 * w / h) > (1.0 * dsize[0] / dsize[1]):
    #             ratio = 1.0 * dsize[0] / w
    #         else:
    #             ratio = 1.0 * dsize[1] / h
    #         resized = cv2.resize(img, None, fx=ratio, fy=ratio)
    #         if channel == 1:
    #             resized = resized[..., np.newaxis]
    #         newI = np.zeros((dsize[1], dsize[0], channel), dtype=np.uint8) + color
    #         newI[:resized.shape[0], :resized.shape[1]] = resized
    #         resized = newI
    #     if channel == 1:
    #         resized = np.squeeze(resized, axis=2)
    #     return resized
    

class OrtClsInfer(OrtEngine):
    def __init__(self, onnxfile: str):
        super(OrtClsInfer, self).__init__(onnxfile)
        self._x = self._sess.get_inputs()[0].name
        self._y = self._sess.get_outputs()[0].name

    def __call__(self, image, img_size: int):
        with self._timer['PreProcess'].tic_and_toc():
            tensor = ImageTransform(is_train=False, img_size=img_size)(image)
            tensor = tensor.unsqueeze(0).numpy()
   
        with self._timer['Forward'].tic_and_toc():
            preds = self._sess.run([self._y], input_feed={
                self._x: tensor,
            })
    
        with self._timer['PostProcess'].tic_and_toc():
            ret = np.argmax(preds[0])
   
        return ret


class OnnxGlobalInfer(metaclass=SingletonBase):
    def __init__(self):
        self.cls_engine: OrtClsInfer = None