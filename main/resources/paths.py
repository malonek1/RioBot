from pathlib import Path

# Absolute path to the resources/ directory, anchored to this file rather than
# the process working directory. Data files (CSVs, JSON config) load reliably no
# matter where the bot is started from.
RESOURCES_DIR = Path(__file__).resolve().parent
