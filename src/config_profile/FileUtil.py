import glob
import json
import os
import shutil
from typing import Dict
import tomllib


class FileUtil:
    @staticmethod
    def load_to_string(path: str) -> str:
        with open(path, encoding="UTF-8") as user_file:
            file_contents = user_file.read()
        return file_contents

    @staticmethod
    def load_toml_to_dict(path: str) -> Dict:
        with open(path, 'rb') as toml_file:
            toml_dict = tomllib.load(toml_file)
        return toml_dict

    @staticmethod
    def load_json_to_dict(path: str) -> Dict:
        json_str = FileUtil.load_to_string(path)
        return json.loads(json_str)

    @staticmethod
    def save_to_json(path: str, data: Dict):
        json_object = json.dumps(data, indent=4)

        # Writing to sample.json
        with open(path, "w") as outfile:
            outfile.write(json_object)

    @staticmethod
    def save_to_toml(path: str, data: Dict):
        with open(path, "wb") as toml_file:
            tomllib.dump(data, toml_file)

    @staticmethod
    def move_files_with_prefix(file_pattern: str, target_folder: str, prefix: str = ""):
        """
        file_pattern = 'path/to/files/*.txt'
        target_folder = 'path/to/target/folder'
        prefix = 'new_'

        move_files_with_prefix(file_pattern, target_folder, prefix)
        """
        files = glob.glob(file_pattern)
        for file_path in files:
            file_name = os.path.basename(file_path)
            new_file_name = prefix + file_name
            new_file_path = os.path.join(target_folder, new_file_name)
            shutil.move(file_path, new_file_path)
