from typing import Protocol


class IPaper(Protocol):
    """Interface para representar um documento."""

    page: int
    content: str
