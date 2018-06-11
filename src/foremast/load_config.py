#!/usr/bin/env python3
"""Central configuration loading."""
import configparser
import importlib
import json
import logging
import os

import deepmerge

LOG = logging.getLogger(__name__)

DEFAULT_CONFIG = {
    'base': {
        'ami_json_url': None,
        'default_ec2_securitygroups': {},
        'default_elb_securitygroups': {},
        'default_securitygroup_rules': {},
        'domain': 'example.com',
        'ec2_pipeline_types': [],
        'envs': [],
        'gate_api_url': None,
        'gate_ca_bundle': '',
        'gate_client_cert': '',
        'git_url': None,
        'regions': [],
        'securitygroup_replacements': {},
        'templates_path': None,
        'types': [
            'datapipeline',
            'ec2',
            'lambda',
            'rolling',
            's3',
        ],
    },
    'credentials': {
        'gitlab_token': None,
        'slack_token': None,
    },
    'formats': {},
    'headers': {
        'accept': '*/*',
        'content-type': 'application/json',
        'user-agent': 'foremast',
    },
    'links': {},
    'task_timeouts': {
        'default': 120,
        'envs': {},
    },
    'whitelists': {
        'asg_whitelist': [],
    },
}

CONFIG_CFG_LOCATIONS = frozenset([
    '/etc/foremast/foremast.cfg',
    os.path.expanduser('~/.foremast/foremast.cfg'),
    './.foremast/foremast.cfg',
])

ENV_FOREMAST_CONFIG_DIRECTORY = 'FOREMAST_CONFIG_DIRECTORY'

CONFIG_MODULE_DIRECTORY = os.getenv(ENV_FOREMAST_CONFIG_DIRECTORY, os.getenv('PWD'))
CONFIG_MODULE_NAME = 'foremast_config'
CONFIG_MODULE_FILE = '{0}/{1}.py'.format(CONFIG_MODULE_DIRECTORY, CONFIG_MODULE_NAME)


class TypeConflictStrategies(deepmerge.strategy.type_conflict.TypeConflictStrategies):
    """Add conflict strategy."""

    @staticmethod
    def strategy_comma_split_append(config, path, base, nxt):
        """Merge comma separated :obj:`str` and :obj:`list`."""
        if isinstance(base, str) and isinstance(nxt, list):
            value = base.split(',') + nxt
        elif isinstance(base, list) and isinstance(nxt, str):
            value = base + nxt.split(',')
        else:
            value = deepmerge.strategy.core.STRATEGY_END
        return value

    @staticmethod
    def strategy_not_empty(config, path, base, nxt):
        """Return whichever value is not empty."""
        if not base and nxt:
            value = nxt
        elif base and not nxt:
            value = base
        else:
            value = deepmerge.strategy.core.STRATEGY_END
        return value

    @staticmethod
    def strategy_configparser(config, path, base, nxt):
        """Convert :obj:`configparser.SectionProxy` to :obj:`dict` for merge."""
        value = deepmerge.strategy.core.STRATEGY_END
        if isinstance(base, configparser.SectionProxy):
            value = Merge().merge(dict(base), nxt)
        elif isinstance(nxt, configparser.SectionProxy):
            value = Merge().merge(base, dict(nxt))
        return value

    @staticmethod
    def strategy_override_str_to_int(config, path, base, nxt):
        """Convert :obj:`str` to :obj:`int` for comparison."""
        value = deepmerge.strategy.core.STRATEGY_END
        if isinstance(base, int) and isinstance(nxt, str):
            value = int(nxt)
        return value

    @staticmethod
    def strategy_json(config, path, base, nxt):
        """Try to convert JSON to Python object."""
        value = deepmerge.strategy.core.STRATEGY_END
        if isinstance(base, dict) and isinstance(nxt, str):
            code = json.loads(nxt)
            value = Merge().merge(base, code)
        return value


class FallbackStrategies(deepmerge.strategy.fallback.FallbackStrategies):
    """Add fallback strategies when Types are unhandled by builtins."""

    @staticmethod
    def strategy_equality(config, path, base, nxt):
        """Check for equality and return first one."""
        value = deepmerge.strategy.core.STRATEGY_END
        if base == nxt:
            value = base
        return value


class Merge(deepmerge.Merger):
    """Handle Foremast configuration legacy values."""

    def __init__(self):
        super().__init__(
            type_strategies=[
                (list, 'append'),
                (dict, 'merge'),
            ],
            fallback_strategies=[],
            type_conflict_strategies=[],
        )

        self._fallback_strategy = FallbackStrategies([
            'equality',
        ])

        self._type_conflict_strategy = TypeConflictStrategies([
            'comma_split_append',
            'json',
            'not_empty',
            'configparser',
            'override_str_to_int',
        ])


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
        """Prevent setting values."""
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

        config = Merge().merge(DEFAULT_CONFIG, loaded_config)

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
