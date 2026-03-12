"""Renix graph nodes package.

All node functions are pure callables with the signature::

    (state: GraphState, config: RunnableConfig) -> dict

They read fields from ``state``, perform their action, and return a partial
dict of state updates. They never mutate the passed-in state object.
"""
