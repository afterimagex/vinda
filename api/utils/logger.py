import atexit
import functools
import logging
import os

from rich.logging import RichHandler

LOG_BUFFER_SIZE_KEY: str = "LOG_BUFFER_SIZE"
DEFAULT_LOG_BUFFER_SIZE: int = 1024 * 1024  # 1MB


@functools.lru_cache()  # so that calling setup_logger multiple times won't add many handlers
def setup_logger(
    output=None,
    level=logging.INFO,
    distributed_rank=0,
    *,
    name="vinda",
    enable_propagation: bool = False,
    configure_stdout: bool = True,
):
    """
    Initialize the detectron2 logger and set its verbosity level to "DEBUG".

    Args:
        output (str): a file name or a directory to save log. If None, will not save log file.
            If ends with ".txt" or ".log", assumed to be a file name.
            Otherwise, logs will be saved to `output/log.txt`.
        name (str): the root module name of this logger
        abbrev_name (str): an abbreviation of the module, to avoid long names in logs.
            Set to "" to not log the root module in logs.
            By default, will abbreviate "detectron2" to "d2" and leave other
            modules unchanged.
        enable_propagation (bool): whether to propagate logs to the parent logger.
        configure_stdout (bool): whether to configure logging to stdout.


    Returns:
        logging.Logger: a logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = enable_propagation

    # stdout logging: master only
    if configure_stdout and distributed_rank == 0:
        rh = RichHandler(level)
        rh.setFormatter(logging.Formatter("%(name)s: %(message)s"))
        logger.addHandler(rh)

    # file logging: all workers
    if output is not None:
        if output.endswith(".txt") or output.endswith(".log"):
            filename = output
        else:
            filename = os.path.join(output, "log.txt")

        if distributed_rank > 0:
            filename = filename + ".rank{}".format(distributed_rank)

        os.makedirs(os.path.dirname(filename), exist_ok=True)

        fh = logging.StreamHandler(_cached_log_stream(filename))
        fh.setLevel(logging.DEBUG)
        plain_formatter = logging.Formatter(
            "[%(asctime)s] %(levelname)s [%(name)s:%(filename)s:%(lineno)d] %(message)s",
            datefmt="%m/%d/%y %H:%M:%S",
        )
        fh.setFormatter(plain_formatter)
        logger.addHandler(fh)
    return logger


# cache the opened file object, so that different calls to `setup_logger`
# with the same file name can safely write to the same file.
@functools.lru_cache(maxsize=None)
def _cached_log_stream(filename):
    # use 1K buffer if writing to cloud storage
    io = open(filename, "a", buffering=_get_log_stream_buffer_size(filename))
    atexit.register(io.close)
    return io


def _get_log_stream_buffer_size(filename: str) -> int:
    if "://" not in filename:
        # Local file, no extra caching is necessary
        return -1
    # Remote file requires a larger cache to avoid many small writes.
    if LOG_BUFFER_SIZE_KEY in os.environ:
        return int(os.environ[LOG_BUFFER_SIZE_KEY])
    return DEFAULT_LOG_BUFFER_SIZE
