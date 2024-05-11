# `pip install config-profile`

*file-based config for all of your python needs*

## Usage

```python
import os

from config_profile import Config

config = Config(resource_dir=os.path.abspath(os.path.join(os.path.dirname(__file__), 'resources')))

config.get("some_key.optional_key", "default_value")
config.get_required("some_key.required_key")
```
