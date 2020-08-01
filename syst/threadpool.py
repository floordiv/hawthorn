import threading


class ThreadPool:
    def __init__(self, size):
        self.size = size

        self.events = []    # [event_func, event_args, event_kwargs]

    def activate(self, activated=False):
        if not activated:
            threading.Thread(target=self.activate, kwargs={'activated': True}).start()
        else:
            while self.events:
                for func, args, kwargs in self.events[:self.size]:
                    threading.Thread(target=func, args=args, kwargs=kwargs).start()

                del self.events[:self.size]

    def add_event(self, func, args=(), kwargs=None):
        if kwargs is None:
            kwargs = {}

        self.events.append((func, args, kwargs))
