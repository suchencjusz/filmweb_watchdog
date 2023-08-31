import ujson
import os


class ConfigManager:
    def __init__(self, path):
        self.path = path
        self.config = None

    def deafult_config(self) -> dict:
        """
        Default config schema.

        :return: dict with default config
        """

        config_schema = {
            "discord": {"webhook_url": ""},
            "users": [{"name": "example", "embed_color": "faca1b"}],
        }

        return config_schema

    def save(self) -> None:
        """
        Save config to file.

        :return: None
        """

        with open(self.path, "w") as f:
            ujson.dump(self.config, f, indent=4)

    def load(self) -> dict:
        """
        Load config from file to self.config.

        :return: None
        """

        if not os.path.exists(self.path):
            self.config = self.deafult_config()
            self.save()
            raise Exception(
                "Config file not found. Created new one. Please fill it with data and run again."
            )

        with open(self.path, "r") as f:
            self.config = ujson.load(f)

        return self.config
