"""
Importing these submodules (rather than star-importing them) registers each
ModelAdmin via its `@admin.register(...)` decorator without leaking their
internals into this package's namespace.
"""

from . import address, profile, rank, user  # noqa: F401
