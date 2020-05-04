from __future__ import annotations

from functools import partial
from pathlib import Path
from typing import Any
from typing import Callable
from typing import Dict
from typing import Tuple
from typing import Union

from atomic_write_path import atomic_write_path
from functional_itertools import CIterable
from pyinstrument import Profiler
from wrapt import decorator


def profile(
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
