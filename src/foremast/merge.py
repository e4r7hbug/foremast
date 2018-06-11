"""Extend :mod:`deepmerge` with new strategies."""
import configparser
import json

import deepmerge


class TypeConflictStrategies(deepmerge.strategy.type_conflict.TypeConflictStrategies):
    """Add conflict strategy."""

    @staticmethod
    def strategy_comma_split_append(_config, _path, base, nxt):
        """Merge comma separated :obj:`str` and :obj:`list`."""
        if isinstance(base, str) and isinstance(nxt, list):
            value = base.split(',') + nxt
        elif isinstance(base, list) and isinstance(nxt, str):
            value = base + nxt.split(',')
        else:
            value = deepmerge.strategy.core.STRATEGY_END
        return value

    @staticmethod
    def strategy_not_empty(_config, _path, base, nxt):
        """Return whichever value is not empty."""
        if not base and nxt:
            value = nxt
        elif base and not nxt:
            value = base
        else:
            value = deepmerge.strategy.core.STRATEGY_END
        return value

    @staticmethod
    def strategy_configparser(_config, _path, base, nxt):
        """Convert :obj:`configparser.SectionProxy` to :obj:`dict` for merge."""
        value = deepmerge.strategy.core.STRATEGY_END
        if isinstance(base, configparser.SectionProxy):
            value = Merge().merge(dict(base), nxt)
        elif isinstance(nxt, configparser.SectionProxy):
            value = Merge().merge(base, dict(nxt))
        return value

    @staticmethod
    def strategy_override_str_to_int(_config, _path, base, nxt):
        """Convert :obj:`str` to :obj:`int` for comparison."""
        value = deepmerge.strategy.core.STRATEGY_END
        if isinstance(base, int) and isinstance(nxt, str):
            value = int(nxt)
        return value

    @staticmethod
    def strategy_json_security_groups(_config, _path, base, nxt):
        """Try to convert JSON to Python object of Security Groups."""
        value = deepmerge.strategy.core.STRATEGY_END
        if isinstance(base, dict) and isinstance(nxt, str):
            try:
                code = json.loads(nxt)
            except json.JSONDecodeError:
                code = {'all_envs': nxt.split(',')}
            value = Merge().merge(base, code)
        return value


class FallbackStrategies(deepmerge.strategy.fallback.FallbackStrategies):
    """Add fallback strategies when Types are unhandled by builtins."""

    @staticmethod
    def strategy_equality(_config, _path, base, nxt):
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
            'json_security_groups',
            'not_empty',
            'configparser',
            'override_str_to_int',
        ])


MERGE = Merge().merge
