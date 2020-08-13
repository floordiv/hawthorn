import threading
from time import sleep


class ThreadPool:
    def __init__(self, size, exit_when_no_events=True):
        self.size = size
        self.exit_if_no_events = exit_when_no_events

        self.events = []    # [event_func, event_args, event_kwargs]
        self.active = False

    def activate(self):
        self.active = True

        while True:
            while self.events:
                for func, args, kwargs in self.events[:self.size]:
                    threading.Thread(target=func, args=args, kwargs=kwargs).start()

                del self.events[:self.size]

            if self.exit_if_no_events:
                self.active = False
                return

            sleep(0.1)

    def start(self):
        threading.Thread(target=self.activate).start()

    def add_event(self, func, args=(), kwargs=None):
        if kwargs is None:
            kwargs = {}

        self.events.append((func, args, kwargs))
