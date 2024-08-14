

# import cv2
import contextlib
import datetime
import time
import numpy as np

from PIL import Image
from pathlib import Path, PosixPath


def get_path_tree(path: str | PosixPath):
    """
    递归地获取目录结构，并构建一个包含目录和文件的字典。
    """
    if isinstance(path, str):
        path = Path(path)

    tree = {
        'name': path.name,
        'type': 'directory' if path.is_dir() else 'file',
        'children': []
    }
    
    if path.is_dir():
        with path.resolve() as p:
            for child in p.iterdir():
                tree['children'].append(get_path_tree(child))
                
    return tree


class Timer(object):
    """A simple timer."""

    def __init__(self):
        self.total_time = 0.
        self.calls = 0
        self.start_time = 0.
        self.diff = 0.
        self.average_time = 0.

    def add_diff(self, diff, average=True):
        self.total_time += diff
        self.calls += 1
        self.average_time = self.total_time / self.calls
        if average:
            return self.average_time
        else:
            return self.diff

    @contextlib.contextmanager
    def tic_and_toc(self):
        try:
            yield self.tic()
        finally:
            self.toc()

    def tic(self):
        # Using time.time instead of time.clock because time time.clock
        # does not normalize for multithreading
        self.start_time = time.time()

    def toc(self, average=True):
        self.diff = time.time() - self.start_time
        self.total_time += self.diff
        self.calls += 1
        self.average_time = self.total_time / self.calls
        if average:
            return self.average_time
        else:
            return self.diff

    @classmethod
    def new(cls, *args):
        """Return a dict that contains specified timers.

        Parameters
        ----------
        args : str...
            The key(s) to create timers.

        Returns
        -------
        Dict[Timer]
            The timer dict.

        """
        return dict([(k, Timer()) for k in args])
   

def get_progress_info(timer, curr_step, max_steps):
    """Return a info of current progress.

    Parameters
    ----------
    timer : Timer
        The timer to get progress.
    curr_step : int
        The current step.
    max_steps : int
        The total number of steps.

    Returns
    -------
    str
        The progress info.

    """
    average_time = timer.average_time
    eta_seconds = average_time * (max_steps - curr_step)
    eta = str(datetime.timedelta(seconds=int(eta_seconds)))
    progress = (curr_step + 1.) / max_steps
    return '< PROGRESS: {:.2%} | SPEED: {:.3f}s / iter | ETA: {} >' \
        .format(progress, timer.average_time, eta)


def export_onnx_model(model, file):
    pass


# def cv2pil(image):
#     '''
#     将bgr格式的numpy的图像转换为pil
#     :param image:   图像数组
#     :return:    Image对象
#     '''
#     assert isinstance(image, np.ndarray), 'input image type is not cv2'
#     if len(image.shape) == 2:
#         return Image.fromarray(image)
#     elif len(image.shape) == 3:
#         return Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))


# def pil2cv(image):
#     '''
#     将Image对象转换为ndarray格式图像
#     :param image:   图像对象
#     :return:    ndarray图像数组
#     '''
#     N = image.split()
#     if len(N) <= 2:
#         return np.asarray(image)
#     elif len(N) == 3:
#         return cv2.cvtColor(np.asarray(image), cv2.COLOR_RGB2BGR)
#     elif len(N) == 4:
#         return cv2.cvtColor(np.asarray(image), cv2.COLOR_RGBA2BGR)
    

# def get_pil_image(image):
#     '''
#     将图像统一转换为PIL格式\n",
#     :param image:   图像\n",
#     :return:    Image格式的图像\n",
#     '''
#     if isinstance(image, Image.Image):  # or isinstance(image, PIL.JpegImagePlugin.JpegImageFile):
#         return image
#     elif isinstance(image, np.ndarray):
#         return cv2pil(image)


# def get_cv_image(image):
#     '''
#     将图像转换为numpy格式的数据
#     :param image:   图像
#     :return:    ndarray格式的图像数据
#     '''
#     if isinstance(image, np.ndarray):
#         return image
#     elif isinstance(image, Image.Image):  # or isinstance(image, PIL.JpegImagePlugin.JpegImageFile):
#         return pil2cv(image)
