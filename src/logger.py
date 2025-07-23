import logging.config
import yaml

with open("log_conf.yaml") as f:
    cfg = yaml.safe_load(f)

logging.config.dictConfig(cfg)
logger = logging.getLogger("hikariplus")