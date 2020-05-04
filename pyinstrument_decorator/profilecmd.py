from __future__ import annotations

from contextlib import ContextDecorator
from contextlib import contextmanager
from functools import partial
from functools import wraps
from pathlib import Path
from typing import Any
from typing import Callable
from typing import Dict
from typing import Generator
from typing import Optional
from typing import Tuple
from typing import Union

from atomic_write_path import atomic_write_path
from functional_itertools import CIterable
from pyinstrument import Profiler
from wrapt import decorator


_DEFAULT_PATH = "profile.html"


def profile_old(
    func: Any = None,
    *,
    html: bool = False,
    path: Union[Path, str] = "profile.html",
    overwrite: bool = True,
) -> Any:
    if func is None:
        return partial(profile, html=html, path=path)
    else:

        @decorator
        def wrapper(
            wrapped: Callable[..., Any],
            _: Any,  # dead: disable
            args: Tuple[Any, ...],
            kwargs: Dict[str, Any],
        ) -> Any:
            with Profiler() as profiler:
                wrapped(*args, **kwargs)
            print(_trim_output_text(profiler.output_text(unicode=True, color=True)))
            if html:
                path_obj = Path(path).with_suffix(".html")
                with atomic_write_path(path_obj, overwrite=overwrite) as temp:
                    with open(temp, mode="w") as fh:
                        fh.write(profiler.output_html())

        return wrapper(func)


def _trim_output_text(text: str) -> str:
    lines = (
        CIterable(text.splitlines())
        .dropwhile(lambda x: not x.startswith("Program:"))[1:]
        .dropwhile(lambda x: x == "")
    )
    return "\n".join(lines)


@contextmanager
def core_profiler(
    *, html: bool = False, path: Union[Path, str] = _DEFAULT_PATH, overwrite: bool = True,
) -> Generator[None, None, None]:
    with Profiler() as profiler:
        yield
    print(_trim_output_text(profiler.output_text(unicode=True, color=True)))
    if html:
        path_obj = Path(path).with_suffix(".html")
        with atomic_write_path(path_obj, overwrite=overwrite) as temp:
            with open(temp, mode="w") as fh:
                fh.write(profiler.output_html())


class ProfileMeta(ContextDecorator, type):
    def __call__(cls, func=None, *, html=False):
        if func is None:
            #### context manager
            return core_profiler(html=html)
            raise NotImplementedError

        else:
            if html:
                breakpoint()

            def newfunc():
                @wraps(func)
                def arst(*args, html=False, **kwargs):
                    if html:
                        breakpoint()
                    with core_profiler():
                        return func(*args, **kwargs)

                return arst

            return newfunc()
            cls._html = html
            breakpoint()
            return super().__call__(cls, func)

    def __enter__(self):
        self.profiler = Profiler()
        self.profiler.start()
        return self

    def __exit__(self, *exc):
        self.profiler.stop()
        print(self.profiler.output_text(unicode=True, color=True))
        return False


class ProfileCMD(ContextDecorator, metaclass=ProfileMeta):
    def __new__(
        cls: ProfileCMD,
        func: Optional[Callable] = None,
        *,
        html: bool = False,
        path: Union[Path, str] = _DEFAULT_PATH,
    ) -> None:
        if func is None:
            raise NotImplementedError
        else:
            obj = super().__new__(func)
            return obj

    def __call__(self, func, *, html: bool = False):
        self._html = html
        return super().__call__(func)

    def __enter__(self: ProfileCMD) -> ProfileCMD:
        self.profiler = Profiler()
        self.profiler.start()
        return self

    def __exit__(self: ProfileCMD, *exc: Any) -> bool:
        self.profiler.stop()
        if self.html:
            print("html!!!")
        print(self.profiler.output_text(unicode=True, color=True))
        return False


profile = ProfileCMD
