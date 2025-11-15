from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar, Union

T = TypeVar('T')
E = TypeVar('E')

@dataclass(frozen=True)
class Result(Generic[T, E]):
    value: Union[T, None]
    error: Union[E, None]

    @property
    def is_success(self) -> bool:
        return self.error is None

    @property
    def is_failure(self) -> bool:
        return self.error is not None

    @classmethod
    def success(cls, value: T) -> 'Result[T, E]':
        return cls(value=value, error=None)

    @classmethod
    def failure(cls, error: E) -> 'Result[T, E]':
        return cls(value=None, error=error)
