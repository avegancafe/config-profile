import logging
import os
from typing import Optional

from config_profile.dict_util import DictUtil
from config_profile.file_util import FileUtil

logger = logging.getLogger(__name__)


class RequiredConfigKeyException(Exception):
    pass


class Config:
    """
    Gets a config value from various locations.
    The First location to supply a value wins.
    Values are searched for in this order:
        1) Pull from os env
        2) Pull from application-{env}.toml
        3) Pull from application.toml

    keys are lower case and use "." as a separator with the exception that
    not all os env vars support "." so for only env vars we also check for the uppercase key with "_" instead of "."
    (see unit tests for examples)

    Note: this class implements the singleton pattern
    """

    def __init__(self, resource_dir: str):
        self._config = {}

        # load values from the default application cfile
        self._populate_with_values_from_toml(config_file=os.path.join(resource_dir, "application.toml"))

        # load values from the env specific profile (ie local, dev, prod)
        profile = self.get_profile()
        self._populate_with_values_from_toml(config_file=os.path.join(resource_dir, f"application-{profile}.toml"))

    def get_dataset_name(self, base_name: str = "network_intel"):
        profile = self.get_profile()

        if profile in ["prod", "staging", "ci"]:
            return base_name
        elif profile in ["local"]:
            return f"{base_name}_qa"
        else:
            return f"{base_name}_{profile}"

    def _populate_with_values_from_toml(self, config_file: str):
        try:
            values = FileUtil.load_toml_to_dict(config_file)
            # also print because the logger is sometimes not initialized yet
            print(f"Populating config with {config_file}")
            logger.info(f"Populating config with {config_file}")
            for k, v in DictUtil.flatten_dict(values, sep=".").items():
                self._config[k.lower()] = v
        except FileNotFoundError:
            if "application-local.toml" not in config_file:
                # also print because the logger is sometimes not initialized yet
                print(f"Config file not found: {config_file}")
                logger.warning(f"Config file not found: {config_file}")

    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        # first check the os env
        v = self.get_env_value(key)
        if v:
            return v

        # check the application configs
        v = self._config.get(key)
        if v:
            return v
        return default

    def get_required(self, key: str) -> str:
        v = self.get(key)
        if v is None:
            raise RequiredConfigKeyException(f"Required key [{key}] not found in config")
        return v

    def is_enabled(self, key: str) -> bool:
        return self.get_boolean(key, default=False)

    def has_feature(self, feature_name: str) -> bool:
        return self.is_enabled(f"feature.{feature_name}.enabled")

    def get_boolean(self, key, default: Optional[bool] = None) -> Optional[bool]:
        v = self.get(key)
        if isinstance(v, bool):
            return v

        if v:
            return v.lower() == "true"
        return default

    def get_boolean_required(self, key) -> bool:
        v = self.get_required(key)
        return v.lower() == "true"

    def get_int(self, key, default: Optional[int] = None) -> Optional[int]:
        v = self.get(key)
        if v:
            return int(v)

        return default

    def get_int_required(self, key) -> int:
        v = self.get_required(key)
        return int(v)

    def get_float(self, key, default: Optional[float] = None) -> Optional[float]:
        v = self.get(key)
        if v:
            return float(v)

        return default

    def get_profile(self) -> str:
        # by design, the profile value can only be set from an os env
        profile = self.get_env_value("application.profile")

        if profile:
            return profile.lower()

        return "local"

    @classmethod
    def get_env_value(self, key: str, default: Optional[str] = None) -> Optional[str]:
        v = os.environ.get(key)
        if v:
            return v
        # several os envs vars do not support "." in the name, so we also check for the key with "_" instead of "."
        v = os.environ.get(key.upper().replace(".", "_"))
        if v:
            return v
        return default
