import syst.threadpool as tp


THREADS_FOR_HANDLERS_PROCESSING = 10

handlers = []   # [[name, handler, filter]]


def handler(name=None, _filter=None):
    assert name is not None

    if _filter is None:
        _filter = name

    def handler_decorator(func):
        handlers.append((name, func, _filter))


def add_handler(name, handler_func, _filter):
    handlers.append((name, handler_func, _filter))


def process_updates(wrapper, message):
    threadpool = tp.ThreadPool(THREADS_FOR_HANDLERS_PROCESSING)

    for name, func, _filter in handlers:
        if _filter(message):
            threadpool.add_event(func, (wrapper, message))

    threadpool.activate()
