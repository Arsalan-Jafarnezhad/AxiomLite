from questions.exceptions import UnsupportedEvaluator

_REGISTRY = {}

def register(name):
    def decorator(cls):
        _REGISTRY[name] = cls
        return cls
    return decorator

def get_executor(name):
    try:
        cls = _REGISTRY[name]
    except KeyError:
        raise UnsupportedEvaluator(f"Unsupported evaluator: {name}")
    return cls()

def registered_evaluators():
    return tuple(_REGISTRY)
