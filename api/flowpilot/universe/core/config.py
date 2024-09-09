import argparse
import os
from dataclasses import dataclass, fields

__all__ = ["Config", "get_argparser_config"]


@dataclass
class Config:
    runtime_class: str = os.getenv("RUNTIME_CLASS", "URuntime")
    tick_interval: float = 0.016


def get_argparser_config(cls):
    parser = argparse.ArgumentParser(description=f"Reflow check {cls.__name__}")
    for fd in fields(cls):
        parser.add_argument(
            f"--{fd.name}",
            type=fd.type,
            default=fd.default if fd.default != fd.default_factory else None,
            help=f"{fd.name} of type {fd.type.__name__}",
        )
    arg = parser.parse_args()
    cfg = cls(**{k: v for k, v in vars(arg).items() if v is not None})
    msg = "\n  ".join(
        [
            f"{k}: ***" if ("key" in k or "token" in k) else f"{k}: {v}"
            for k, v in cfg.__dict__.items()
        ]
    )
    print(f"\nConfig: (\n  {msg}\n)")
    return cfg
