import syst.tools.threadpool as tp


THREADS_FOR_HANDLERS_PROCESSING = 10

handlers = []   # [[name, handler, filter]]
threadpool = tp.ThreadPool(THREADS_FOR_HANDLERS_PROCESSING, exit_when_no_events=False)
threadpool.start()


def handler(name=None, _filter=None):
    assert name is not None

    if _filter is None:
        _filter = name

    def decorator(func):
        handlers.append((name, func, _filter))

        return func

    return decorator


def add_handler(name, handler_func, _filter):
    handlers.append((name, handler_func, _filter))


def process_update(wrapper, message):
    for name, func, _filter in handlers:
        if _filter(message):
            threadpool.add_event(func, (wrapper, message))
