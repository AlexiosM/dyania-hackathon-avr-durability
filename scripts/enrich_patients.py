import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.enricher import enrich


if __name__ == "__main__":
    enrich()
