from pathlib import Path
import logging
from src.pipeline import run

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

if __name__ == "__main__":
    path=run(Path(__file__).resolve().parent)
    print(f"\nCompleted: {path}")
