import yaml
from yaml import SafeLoader
from typing import Dict, List, Optional

def load_yaml_and_get_group(path: str) -> Dict[str, List[str]]:
    """Load and parse YAML file containing customer group mappings"""
    try:
        with open(path) as f:
            data = yaml.load(f, Loader=SafeLoader)
            customers = {}
            for item in data:
                for key in item:
                    customers[key] = item[key]
            return customers
    except (yaml.YAMLError, FileNotFoundError) as e:
        print(f"Error loading YAML file: {e}")
        return {}


def find_matching_chat_id(name: str, items: dict) -> Optional[int]:
    """Find matching Telegram chat ID for a given Group name"""
    if name in items:
        return items[name]
    return None