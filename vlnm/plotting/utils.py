"""
    Plotting utilities
    ~~~~~~~~~~~~~~~~~~

"""
from typing import Callable, Dict, Iterable, Tuple, Union

import matplotlib.pyplot as plt

from vlnm.utils import merge, strip


def create_figure(*args, **kwargs) -> Figure:
    """Wrapper around matplotlib.pyplot.figure"""
    return plt.figure(*args, **kwargs)


def translate_props(props: Dict, translator: Dict[str, Union[str, Iterable, Callable]]) -> Dict:
    """
    Translate from user-supplied properties to internal properties.

    Parameters
    ----------
    props:
        Dictionary of properties.
    translator:
        Dictionary mapping property names to one or more property names,
        or a function to return multiple properties as a dictionary.

    Returns
    -------
    :
        Dictionary of translated properties.
    """
    translated = {}
    for prop, value in props.items():
        if prop in translator:
            translation = translator[prop]
            try:
                translated.update(**translation(value))
            except TypeError:
                if isinstance(translation, list):
                    translated.update(**{key: value for key in translation})
                else:
                    translated[translation] = value
        else:
            translated[prop] = value
    return translated


def context_from_kwargs(
        kwargs: Dict,
        include: List[str] = None,
        exclude: List[str] = None) -> Tuple(Dict, Dict):
    r"""
    Separate context and non-context keyword arguments.

    Parameters
    ----------
    \*\*kwargs:
        Keyword arguments.
    include:
        Keywords that are always in the context.
    exclude:
        Keywords that are never in the context.

    Returns
    -------
    :
        The context keywords and the rest.

    """
    include = include or []
    exclude = exclude or []

    context = {}
    rest = kwargs.copy()
    for key, value in kwargs.items():
        if key in include:
            context[key] = value
            del rest[key]
        elif key in exclude:
            continue
        elif key.endswith('_by'):
            context[key] = value
            del rest[key]
            prop = key[:-3]
            if prop in kwargs:
                context[prop] = kwargs[prop]
                del rest[prop]

    context = strip(context)
    return context
