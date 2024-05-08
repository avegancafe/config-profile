import logging
import os
from typing import Optional

from pyprofile.DictUtil import DictUtil
from pyprofile.FileUtil import FileUtil
from pyprofile.SingletonUtil import singleton
from settings import Settings

logger = logging.getLogger(__name__)


class RequiredConfigKeyException(Exception):
    pass


def build_path(filename: str, rootdir: str) -> str:
    normalized = os.path.normpath(filename)
    # mac/linux absolutes start with / so lets just check if the file name starts with the root folder
    if not normalized.startswith(rootdir):
        if normalized.startswith("/") or normalized.startswith("\\"):
            normalized = normalized[1:]
    return os.path.abspath(os.path.join(cls.root_folder, normalized))


@singleton
class Config:
    """
    Gets a config value from various locations.
    The First location to supply a value wins.
    Values are searched for in this order:
        1) Pull from os env
        2) Pull from application-{env}.yml
        3) Pull from application.yml

    keys are lower case and use "." as a separator with the exception that
    not all os env vars support "." so for only env vars we also check for the uppercase key with "_" instead of "."
    (see unit tests for examples)

    Note: this class implements the singleton pattern
    """

    def __init__(self, *args, **kwargs):
        self._config = {}

        # load values from the default application cfile
        self._populate_with_values_from_yml("resources/application.yml")

        # load values from the env specific profile (ie local, dev, prod)
        profile = self.get_profile()
        self._populate_with_values_from_yml(f"resources/application-{profile}.yml")

    def get_dataset_name(self, base_name: str = "network_intel"):
        profile = self.get_profile()

        if profile in ["prod", "staging", "ci"]:
            return base_name
        elif profile in ["local"]:
            return f"{base_name}_qa"
        else:
            return f"{base_name}_{profile}"

    def _populate_with_values_from_yml(self, config_file: str, rootdir: str):
        config_fullpath = build_path(config_file, rootdir)
        try:
            values = FileUtil.load_toml_to_dict(config_fullpath)
            # also print because the logger is sometimes not initialized yet
            print(f"Populating config with {config_fullpath}")
            logger.info(f"Populating config with {config_fullpath}")
            for k, v in DictUtil.flatten_dict(values, sep=".").items():
                self._config[k.lower()] = v
        except FileNotFoundError:
            if "application-local.yml" not in config_file:
                # also print because the logger is sometimes not initialized yet
                print(f"Config file not found: {config_fullpath}")
                logger.warning(f"Config file not found: {config_fullpath}")

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
    def get_env_value(cls, key: str, default: Optional[str] = None) -> Optional[str]:
        v = os.environ.get(key)
        if v:
            return v
        # several os envs vars do not support "." in the name, so we also check for the key with "_" instead of "."
        v = os.environ.get(key.upper().replace(".", "_"))
        if v:
            return v
        return default
