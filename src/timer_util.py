import timeit


class ContextTimer:

    def __enter__(self, threshold: float = 3):
        self.threshold = threshold
        self.start = timeit.default_timer()

    def __exit__(self, *args, **kwargs):
        duration = timeit.default_timer() - self.start
        if duration > self.threshold:
            print(f'duration: {duration:.02f}s')
