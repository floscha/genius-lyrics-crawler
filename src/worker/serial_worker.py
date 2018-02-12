class SerialTask(object):
    """Dummy task that allows invoking a function at a later point in time.

    Args:
        fn (class 'function'): The function object to later invoke.
    """
    def __init__(self, fn):
        self.fn = fn

    def delay(self, *args, **kwargs):
        """Calls the contained function with the given parameters."""
        self.fn(*args, **kwargs)


class SerialWorker(object):
    """Dummy worker that imitates Celery's task decorator.

    The motivation behind the `SerialWorker` is to use it as a substitute for
    Celery in scenarios where Celery is not available or concurrent processing
    is not required. Since it replicates Celery's API, it can simply be used
    as a drop-in replacement without any effects on the program's behaviour
    except that all processing will happen in a serial/non-concurrent fashion.
    """

    def task(self, fn):
        """Decorator to wrap a function in a `SerialTask` object."""
        return SerialTask(fn)


if __name__ == '__main__':
    worker = SerialWorker()
    #
    @worker.task
    def testfn(string):
        print(string)
    #
    testfn.delay("test working")