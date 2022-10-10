from typing import NamedTuple


class User(NamedTuple):
    email: str
    last_login: str
    name: str
    registration_date: str
