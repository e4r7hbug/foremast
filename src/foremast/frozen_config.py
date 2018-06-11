"""Emulate a frozen :obj:`dict` by returning frozen objects on access."""
import logging

LOG = logging.getLogger(__name__)


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
