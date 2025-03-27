import json
import os

# Determine the path to the config file relative to this file.
CONFIG_FILE_PATH = os.path.join(os.path.dirname(__file__), "templates_config.json")


def load_config() -> dict:
    """Load the entire configuration (templates and models) from the JSON config file."""
    try:
        with open(CONFIG_FILE_PATH, "r") as f:
            config = json.load(f)
        return config
    except Exception as e:
        raise Exception(f"Error reading config file: {str(e)}")

def save_config(config: dict):
    """Save the entire configuration dictionary to the JSON config file."""
    try:
        with open(CONFIG_FILE_PATH, "w") as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        raise Exception(f"Error writing to config file: {str(e)}")
    


# def load_templates() -> dict:
#     """Load templates from the JSON config file."""
#     try:
#         with open(CONFIG_FILE_PATH, "r") as f:
#             templates = json.load(f)
#         return templates
#     except Exception as e:
#         # You might want to add logging here.
#         raise Exception(f"Error reading config file: {str(e)}")

# def save_templates(templates: dict):
#     """Save the provided templates dictionary to the JSON config file."""
#     try:
#         with open(CONFIG_FILE_PATH, "w") as f:
#             json.dump(templates, f, indent=4)
#     except Exception as e:
#         raise Exception(f"Error writing to config file: {str(e)}")

