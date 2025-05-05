from collections.abc import Generator, Iterable, Iterator
from typing import Final

class IntIterator(Iterator[int]):
    __n: Final[int]
    __i: int

    def __init__(self, n: int) -> None:
        self.__n = n
        self.__i = 0

    def __next__(self) -> int:
        if self.__i < self.__n:
            self.__i += 1
            return self.__i - 1
        else:
            raise StopIteration()

class IntRange(Iterable[int]):
    __n: Final[int]

    def __init__(self, n: int) -> None:
        self.__n = n

    def __iter__(self) -> IntIterator:
        return IntIterator(self.__n)

my_range = IntRange(5)
for x in my_range:
    print(x)

print([i * 2 for i in IntRange(5)])

class DoubleIterator(Iterator[int]):
    __underlying: Iterator[int]

    def __init__(self, underlying: Iterator[int]) -> None:
        self.__underlying = underlying

    def __next__(self) -> int:
        underlying_next = next(self.__underlying)
        return underlying_next * 2

class DoubleGenerator(Iterable[int]):
    __underlying: Iterator[int]

    def __init__(self, underlying: Iterator[int]) -> None:
        self.__underlying = underlying

    def __iter__(self) -> Iterator[int]:
        return DoubleIterator(self.__underlying)

def int_range(n: int) -> Iterator[int]:
    i = 0
    while i < n:
        yield i
        i += 1
