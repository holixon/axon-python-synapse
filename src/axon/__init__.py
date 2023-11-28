from pathlib import Path
import logging.config
import yaml

logging_cfg_path = Path(__file__).parent / "logging.yaml"
print("CONFIG: ", logging_cfg_path)
with open(logging_cfg_path) as f:
    config = yaml.full_load(f)
    logging.config.dictConfig(config)
