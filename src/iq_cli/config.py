"""Configuration management for iq CLI."""

import os
from pathlib import Path
from typing import Optional
import yaml


class Config:
    """Configuration manager for iq CLI."""

    def __init__(self):
        self.config_dir = Path.home() / ".iq"
        self.config_file = self.config_dir / "config.yaml"
        self.cookies_file = self.config_dir / "cookies.txt"
        self.config_dir.mkdir(exist_ok=True)

        self._config = self._load_config()

    def _load_config(self) -> dict:
        """Load configuration from file."""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return yaml.safe_load(f) or {}
        return {}

    def save_config(self):
        """Save configuration to file."""
        with open(self.config_file, 'w') as f:
            yaml.dump(self._config, f)

    @property
    def api_url(self) -> str:
        """Get API URL from config or environment."""
        return self._config.get('api_url') or os.getenv('IQ_API_URL', 'http://core-api.mat.svc.cluster.local:8000')

    @api_url.setter
    def api_url(self, value: str):
        """Set API URL."""
        self._config['api_url'] = value
        self.save_config()

    @property
    def frontend_url(self) -> str:
        """Get frontend URL from config or environment."""
        return self._config.get('frontend_url') or os.getenv('IQ_FRONTEND_URL', 'http://frontend.mat.svc.cluster.local:80')

    @frontend_url.setter
    def frontend_url(self, value: str):
        """Set frontend URL."""
        self._config['frontend_url'] = value
        self.save_config()

    @property
    def default_environment(self) -> str:
        """Get default environment."""
        return self._config.get('default_environment', 'sandbox')

    @default_environment.setter
    def default_environment(self, value: str):
        """Set default environment."""
        self._config['default_environment'] = value
        self.save_config()

    @property
    def output_format(self) -> str:
        """Get default output format."""
        return self._config.get('output_format', 'table')

    @output_format.setter
    def output_format(self, value: str):
        """Set default output format."""
        self._config['output_format'] = value
        self.save_config()


# Global config instance
config = Config()
