import copy

from easydict import EasyDict


def get_cfg() -> EasyDict:
    """
    Get a copy of the default config.

    Returns:
        a EasyDict instance.
    """
    from api.config.defaults import _C

    return copy.deepcopy(_C)


if __name__ == "__main__":
    cfg = get_cfg()
    print(cfg)
