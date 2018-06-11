#!/usr/bin/env python3
"""Central configuration loading."""
import configparser
import importlib
import logging
import os
import pathlib

from . import merge
from .default_config import DEFAULT_CONFIG
from .frozen_config import FrozenConfig

LOG = logging.getLogger(__name__)

CONFIG_CFG_LOCATIONS = [
    '/etc/foremast/foremast.cfg',
    os.path.expanduser('~/.foremast/foremast.cfg'),
    './.foremast/foremast.cfg',
]

ENV_FOREMAST_CONFIG_DIRECTORY = 'FOREMAST_CONFIG_DIRECTORY'
"""Environment variable name for Foremast Python configuration directory."""

_UNRESOLVED_CONFIG_MODULE_DIRECTORY = os.getenv(ENV_FOREMAST_CONFIG_DIRECTORY, os.getenv('PWD'))
CONFIG_MODULE_DIRECTORY = pathlib.Path(_UNRESOLVED_CONFIG_MODULE_DIRECTORY).expanduser().resolve()
"""Directory location where 'foremast_config.py' resides."""

CONFIG_MODULE_NAME = 'foremast_config'
"""Name of Foremast configuration Python file."""

_CONFIG_MODULE_FILE_PATH = CONFIG_MODULE_DIRECTORY / (CONFIG_MODULE_NAME + '.py')
CONFIG_MODULE_FILE = str(_CONFIG_MODULE_FILE_PATH)
"""Fully qualified path for 'foremast_config.py'."""


class ForemastConfig(object):
    """Foremast configurations."""

    def __init__(self):
        self._config = None
        self.config_from_cfg = None
        self.config_from_module = None

    def load_config_cfg(self):
        """Use :mod:`configparser` to load static configuration files."""
        if self.config_from_cfg:
            return self.config_from_cfg

        config_cfg = configparser.ConfigParser()

        cfg_files_read = config_cfg.read(CONFIG_CFG_LOCATIONS)
        if not cfg_files_read:
            LOG.debug('No configuration files found in the following locations:\n%s', '\n'.join(CONFIG_CFG_LOCATIONS))
        else:
            self.config_from_cfg = dict(config_cfg)

        return self.config_from_cfg

    def load_config_module(self):
        """Import Foremast configuration Module if available."""
        if self.config_from_module:
            return self.config_from_module

        loader = importlib.machinery.SourceFileLoader(CONFIG_MODULE_NAME, CONFIG_MODULE_FILE)

        try:
            config_module = loader.load_module()
        except FileNotFoundError as error:
            LOG.debug('Foremast configuration Module not found in "$%s": %s', ENV_FOREMAST_CONFIG_DIRECTORY, error)
        else:
            self.config_from_module = dict(config_module.CONFIG)

        return self.config_from_module

    def load(self):
        """Load configurations."""
        if self._config:
            return self._config

        loaded_config = self.load_config_module() or self.load_config_cfg()

        if not loaded_config:
            locations = '\n'.join(CONFIG_CFG_LOCATIONS + [CONFIG_MODULE_FILE])
            LOG.warning('No configuration files found in:\n%s\nUsing defaults.', locations)

        config = merge.MERGE(DEFAULT_CONFIG, loaded_config)

        self._config = FrozenConfig(config)
        LOG.debug('Complete configuration: %s', self._config)
        return self._config

    @property
    def config(self):
        """Load configuration on access."""
        if not self._config:
            self.load()
        return self._config

    def __getitem__(self, key):
        """Retrieve value from configuration."""
        return self.config[key]

    def __repr__(self):
        """Dump full configuration."""
        return repr(self.config)


CONFIG = ForemastConfig()
