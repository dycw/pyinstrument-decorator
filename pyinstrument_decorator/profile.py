from __future__ import annotations

import webbrowser
from contextlib import ContextDecorator
from functools import wraps
from pathlib import Path
from typing import Any
from typing import Callable
from typing import Optional
from typing import TypeVar
from typing import Union

from atomic_write_path import atomic_write_path
from functional_itertools import CIterable
from pyinstrument import Profiler


T = TypeVar("T")
_DEFAULT_PATH = "profile.html"


class WrappedProfiler:
    def __init__(
        self: WrappedProfiler,
        *,
        html: bool = False,
        path: Union[Path, str] = _DEFAULT_PATH,
        overwrite: bool = True,
    ) -> None:
        self._html = html
        self._path = path
        self._overwrite = overwrite

    def __call__(self, func, *args, **kwargs):
        with self:
            return func(*args, *kwargs)
        raise NotImplementedError(func, args, kwargs)

    def __enter__(self: WrappedProfiler) -> WrappedProfiler:
        self._profiler = Profiler()
        self._profiler.__enter__()
        return self

    def __exit__(self: WrappedProfiler, exc_type: Any, exc_val: Any, exc_tb: Any) -> Any:
        self._profiler.__exit__(exc_type, exc_val, exc_tb)
        print(_trim_output_text(self._profiler.output_text(unicode=True, color=True)))
        if self._html:
            path_obj = Path(self._path).with_suffix(".html")
            with atomic_write_path(path_obj, overwrite=self._overwrite) as temp:
                with open(temp, mode="w") as fh:
                    fh.write(self._profiler.output_html())
        return False

    def open(self: WrappedProfiler) -> None:
        webbrowser.open(str(Path(self._path).resolve()))


def _trim_output_text(text: str) -> str:
    lines = (
        CIterable(text.splitlines())
        .dropwhile(lambda x: not x.startswith("Program:"))[1:]
        .dropwhile(lambda x: x == "")
    )
    return "\n".join(lines)


class ProfileMeta(ContextDecorator, type):
    def __call__(  # noqa: U100
        cls: ContextDecorator,
        func: Optional[Callable[..., T]] = None,
        *,
        html: bool = False,
        path: Union[Path, str] = _DEFAULT_PATH,
        overwrite: bool = True,
    ) -> Union[WrappedProfiler, Callable[..., T]]:
        wrapped = WrappedProfiler(html=html, path=path, overwrite=overwrite)
        if func is None:
            return wrapped
        else:

            @wraps(func)
            def new_func(*args: Any, **kwargs: Any) -> T:
                with wrapped:
                    return func(*args, **kwargs)

            return new_func

    def __enter__(cls: ProfileMeta) -> ProfileMeta:
        cls._wrapped_profiler = WrappedProfiler()
        cls._wrapped_profiler.__enter__()
        return cls

    def __exit__(cls: ProfileMeta, exc_type: Any, exc_val: Any, exc_tb: Any) -> Any:
        cls._wrapped_profiler.__exit__(exc_type, exc_val, exc_tb)
        return False

    def open(cls: ProfileMeta):
        pass


class profile(ContextDecorator, metaclass=ProfileMeta):
    def __call__(self, *args, **kwargs):
        raise NotImplementedError("arst")

    def __enter__(self: profile) -> profile:
        self._wrapped_profiler = WrappedProfiler()
        self._wrapped_profiler.__enter__()
        return self

    def __exit__(self: profile, exc_type: Any, exc_val: Any, exc_tb: Any) -> Any:
        self._wrapped_profiler.__exit__(exc_type, exc_val, exc_tb)
        return False
