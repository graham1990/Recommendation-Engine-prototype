import hashlib
from typing import Generator


class RepeatableRandom:
    def __init__(self, seed: str) -> None:
        hash = str.encode(seed)
        self._forever = False
        self._hash = hashlib.md5(hash).digest()
        self._iterable = iter(self)
    
    @property
    def iterable(self):
        return self._iterable

    def __iter__(self) -> Generator[float, None, None]:
        while True:
            for c in self._hash:
                rand_value = self._min + (self._max - self._min) * (c / 250)
                if rand_value <= self._max:
                    yield rand_value
            if not self._forever:
                break

    def repeatable_random(
        self, min: int, max: int, forever=True
    ) -> Generator[float, None, None]:
        self._min = min
        self._max = max
        self._forever = forever
        return self


rr = RepeatableRandom("The quick brown fox jumps over a lazy dog.")


def not_so_random(min: int, max: int) -> float:
    rr.repeatable_random(min, max)
    return next(rr.iterable)


if __name__ == "__main__":
    assert not_so_random(4, 9) == 6.859999999999999
    assert not_so_random(4, 9) == 8.120000000000001

    rr = RepeatableRandom("The quick brown fox jumps over a lazy dog.")
    expected = [
        6.859999999999999,
        8.120000000000001,
        5.68,
        9.0,
        7.46,
        6.52,
        4.54,
        5.16,
        4.98,
        8.34,
        7.220000000000001,
        7.18,
        7.54,
        5.34,
        6.78,
        7.16,
    ]
    for indx, each in enumerate(rr.repeatable_random(4, 9, forever=False)):
        assert each == expected[indx]

    rr = RepeatableRandom("Waltz, bad nymph, for quick jigs vex.")
    expected = [
        8.32,
        7.96,
        5.8,
        5.24,
        8.04,
        4.3,
        6.9,
        7.12,
        5.22,
        8.48,
        4.12,
        4.36,
        6.82,
        8.600000000000001,
        6.7,
        4.8,
    ]
    for indx, each in enumerate(rr.repeatable_random(4, 9, forever=False)):
        assert each == expected[indx]

    rr = RepeatableRandom("Sphinx of black quartz, judge my vow.")
    expected = [
        5.62,
        5.5,
        8.9,
        4.14,
        4.26,
        8.4,
        4.14,
        7.2,
        4.52,
        8.76,
        6.52,
        5.22,
        8.1,
        5.48,
        7.24,
        6.46,
    ]
    for indx, each in enumerate(rr.repeatable_random(4, 9, forever=False)):
        assert each == expected[indx]
