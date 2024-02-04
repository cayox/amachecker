import functools

from PyQt6.QtCore import QThread, pyqtSignal


class WorkerThread(QThread):
    """A QThread to run a method in a thread concurrently.

    Has custom signals for errors, messages and when its done.
    """

    error_signal = pyqtSignal(Exception)
    done_signal = pyqtSignal()
    message_signal = pyqtSignal(str)

    def __init__(self, function, args: tuple | None = None, kwargs: dict | None = None):
        super().__init__()
        self.function = function
        self.args = args if args is not None else ()
        self.kwargs = kwargs if kwargs is not None else {}

    def run(self):
        try:
            self.function(*self.args, **self.kwargs)
            self.done_signal.emit()
        except Exception as exc:  # noqa: BLE001, we want to catch all exceptions
            self.error_signal.emit(exc)

    def log(self, msg: str):
        self.message_signal.emit(msg)


def run_in_thread(method) -> callable:
    """Decorator that runs a method of a QWidget in a separate thread and passes a logging function.

    This decorator creates a WorkerThread to run the specified method and automatically
    connects the thread's signals to the QWidget's slot methods for error handling,
    completion, and message logging. It also adds a 'log_func' argument to the method
    that can be used within the method for logging purposes.

    Args:
        method (Callable): The method to be executed in a separate thread.

    Returns:
        Function: A wrapper function that starts the thread and passes the logging function.

    Usage:
        @run_in_thread
        def your_method(self, log_func=None, *args, **kwargs):
            # Your method logic here
            log_func("Some log message")
    """

    @functools.wraps(method)
    def wrapper(self, *args, **kwargs) -> WorkerThread:
        # Create a WorkerThread instance
        worker = WorkerThread(
            lambda: method(self, *args, log_func=worker.log, **kwargs),
        )

        # Connect the WorkerThread signals to the corresponding QWidget slots
        worker.error_signal.connect(self.handle_error)
        worker.done_signal.connect(self.handle_done)
        worker.message_signal.connect(self.handle_message)

        # Start the thread
        worker.start()
        return worker

    return wrapper
