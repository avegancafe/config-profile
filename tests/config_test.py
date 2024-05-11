import os

from config_profile.config import Config

def test_base_config():
    config = Config(resource_dir=os.path.abspath(os.path.join(os.path.dirname(__file__), "fixtures", "resources")))

    assert config.get("top_level_key.some_sub_key") == "a value"

def test_config_profile_ordering():
    os.environ["APPLICATION_PROFILE"] = "test"
    config = Config(resource_dir=os.path.abspath(os.path.join(os.path.dirname(__file__), "fixtures", "resources")))

    assert config.get("top_level_key.key_to_be_overwritten") == "I have been overwritten"
