#!/usr/bin/env python3
"""Central configuration loading."""
import configparser
import importlib
import logging
import os

from . import merge
from .default_config import DEFAULT_CONFIG

LOG = logging.getLogger(__name__)

CONFIG_CFG_LOCATIONS = frozenset([
    '/etc/foremast/foremast.cfg',
    os.path.expanduser('~/.foremast/foremast.cfg'),
    './.foremast/foremast.cfg',
])

ENV_FOREMAST_CONFIG_DIRECTORY = 'FOREMAST_CONFIG_DIRECTORY'

CONFIG_MODULE_DIRECTORY = os.getenv(ENV_FOREMAST_CONFIG_DIRECTORY, os.getenv('PWD'))
CONFIG_MODULE_NAME = 'foremast_config'
CONFIG_MODULE_FILE = '{0}/{1}.py'.format(CONFIG_MODULE_DIRECTORY, CONFIG_MODULE_NAME)


class FrozenConfig(dict):
    """Immutable configuration values."""

    def __getitem__(self, key):
        """Return immutable form of value."""
        frozen_value = None

        value = super().__getitem__(key)

        LOG.debug('%s = %s %s', key, value, type(value))

        if isinstance(value, (self.__class__, frozenset)):
            frozen_value = value
        elif isinstance(value, (list, set, tuple)):
            frozen_value = frozenset(value)
            super().__setitem__(key, frozen_value)
        elif isinstance(value, (dict)):
            frozen_value = FrozenConfig(value)
            super().__setitem__(key, frozen_value)
        else:
            frozen_value = value

        return frozen_value

    def __setitem__(self, key, value):
        """Prevent setting values like :class:`types.MappingProxyType`."""
        raise TypeError('"{0}" object does not support item assignment'.format(self.__class__.__name__))


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
            locations = '\n'.join(list(CONFIG_CFG_LOCATIONS) + [CONFIG_MODULE_FILE])
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
