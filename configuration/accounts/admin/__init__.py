"""Django admin configuration for the accounts application."""

from .address import AddressAdmin
from .profile import ProfileAdmin
from .rank import RankAdmin
from .user import UserAdmin

__all__ = [
    "AddressAdmin",
    "ProfileAdmin",
    "RankAdmin",
    "UserAdmin",
]