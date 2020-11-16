from syst.tools.output import println
from syst.tools.threadpool import ThreadPool

from traceback import format_exc


handlers = []   # [[name, handler, filter]]

tp = ThreadPool(10, exit_when_no_events=False)
tp.start()


def handler(name=None, _filter=None):
    assert name is not None

    if _filter is None:
        name, _filter = name.__name__, name

    def decorator(func):
        handlers.append((name, func, _filter))

        return func

    return decorator


def add_handler(name, handler_func, _filter):
    handlers.append((name, handler_func, _filter))


def process_update(wrapper, message):
    for name, func, _filter in handlers:
        try:
            filter_returns_true = _filter(message)
        except Exception as exc:
            println('UPDATE-MANAGER', f'Filter of the handler "{name}" raised an error: {exc}')
            print(format_exc())
            continue

        if filter_returns_true:
            tp.add_event(func, (wrapper, message))
