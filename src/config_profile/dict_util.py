from functools import reduce
from typing import Dict, List


class DictUtil:
    @staticmethod
    def merge(dicts: List[Dict]) -> Dict:
        """
        Merges dictionary recursively returning a new Dict
        """

        def _merge(a, b, path=None):
            # "merges b into a"
            if path is None:
                path = []
            for key in b:
                if key in a:
                    if isinstance(a[key], dict) and isinstance(b[key], dict):
                        _merge(a[key], b[key], path + [str(key)])
                    elif a[key] == b[key]:
                        pass  # same leaf value
                    else:
                        # raise Exception('Conflict at %s' % '.'.join(path + [str(key)]))
                        a[key] = b[key]
                else:
                    a[key] = b[key]
            return a

        return reduce(_merge, ([{}, *dicts]))

    @staticmethod
    def flatten_dict(d: dict, parent_key: str = "", sep: str = ".") -> dict:
        items = []
        for k, v in d.items():
            new_key = parent_key + sep + k if parent_key else k
            if isinstance(v, dict):
                items.extend(DictUtil.flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)

    @staticmethod
    def sort_keys(input_dict: dict) -> dict:
        """
        Sorts the keys of a dictionary and returns a new dictionary
        """
        # Get the keys from the dictionary and sort them
        sorted_keys = sorted(input_dict.keys())

        # Create a new dictionary with the sorted keys
        sorted_dict = {key: input_dict[key] for key in sorted_keys}

        return sorted_dict
