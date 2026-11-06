"""Same known signals, sent to a Collector at :4317 for the end-to-end demo."""
import os

os.environ.setdefault("DCE_OTLP_ENDPOINT", "http://127.0.0.1:4317")
from emitter import *  # noqa: F403
