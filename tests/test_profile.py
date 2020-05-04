from __future__ import annotations

from time import sleep

from pyinstrument_decorator import profile


def sleep_and_return(secs: float) -> float:
    sleep(secs)
    return secs


def test_context_manager_without_arguments() -> None:
    with profile:
        sleep(0.1)


def test_context_manager_with_arguments() -> None:
    with profile(html=True):
        sleep(0.1)


def test_decorator_without_arguments() -> None:
    decorated = profile(sleep_and_return)
    assert decorated(0.1) == 0.1


def test_decorator_with_arguments() -> None:
    @profile(html=True)
    def func(secs: float) -> float:
        sleep(secs)
        return secs

    assert func(0.1) == 0.1
