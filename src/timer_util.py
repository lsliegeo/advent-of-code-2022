import timeit


class ContextTimer:

    def __enter__(self):
        self.start = timeit.default_timer()

    def __exit__(self, *args, **kwargs):
        print(f'duration: {timeit.default_timer() - self.start:.02f}s')
