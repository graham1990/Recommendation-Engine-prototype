import random
import time
from typing import Any, Callable


class Duration:
    """Calculate the time interval for the retry interval"""
    @staticmethod
    def of_milliseconds(interval_time: int) -> float:
        """Specify the number of milliseci=onds in seconds"""
        return interval_time / 1000

    @staticmethod
    def of_seconds(interval_time: int) -> int:
        """Specify number of seconds in seconds"""
        return interval_time

    @staticmethod
    def of_minutes(interval_time: int) -> int:
        """Specify number of minutes in seconds"""
        return interval_time * 60

class SearchPolicies:    
    @staticmethod
    def on_value_type_and_value(target_type: type, op: Callable, target_val: Any):
        """Search heterogeneous collections value attr for both type and value"""
        return lambda key, val: isinstance(val, target_type) and op(val, target_val)

class SearchableDict:
    def __init__(self, initial: dict) -> None:
        self._detail = initial if initial else {}

    def extract(self, fn: Callable):
        res = {
                key: val for key, val in self._detail.items() if fn(key, val)}
        return res

    def __setitem__(self, __key: Any, __value: Any) -> None:
        """Update a log item already in the logs"""
        self._detail[__key] = __value

    def __getitem__(self, __key: Any) -> Any:
        """Get log item number __key"""
        return self._detail[__key]

    def __contains__(self, __key: Any) -> bool:
        """Is log item present in log"""
        return self._detail.__contains__(__key)

    def __str__(self) -> str:
        return str(self._detail)

    def __repr__(self) -> str:
        return repr(self._detail)


class LogEntry(SearchableDict):
    pass


class RetryLogs:
    def __init__(self) -> None:
        self._detail = []

    def append(self, item: dict[str, Any]) -> None:
        """Append log item to end of the logs"""
        self._detail.append(item)

    def extract_entry(self, fn: Callable):
        return [each for each in self._detail if each.extract(fn) != dict()]

    def extract(self, fn: Callable):
        res = []
        for each in self._detail:
            attrs = each.extract(fn)
            if attrs != dict():
                res.append(attrs)
        return res

    def __setitem__(self, __key: Any, __value: Any) -> None:
        """Update a log item already in the logs"""
        self._detail[__key] = __value

    def __getitem__(self, __key: Any) -> Any:
        """Get log item number __key"""
        return self._detail[__key]

    def __contains__(self, __key: Any) -> bool:
        """Is log item present in log"""
        return self._detail.__contains__(__key)

    def __str__(self) -> str:
        return str(self._detail)

    def __repr__(self) -> str:
        """pprint style formatting"""
        from pprint import pformat
        return pformat(self._detail, indent=4, width=1)


class RetryPolicy:
    """Policy that offers retry policies that will back off retrying
    for a speified period though a context manager."""
    def __init__(self) -> None:
        self._initial_interval = 1
        self._backoff_rate = 2
        self._multiplier = 1
        self._max_interval = 500

    def __enter__(self):
        """Enter the context manager"""
        self._current_wait = 0.0
        self._attempt = 0
        self._last_wait_time = 0.0
        self._start_time = time.time()
        return self

    def __exit__(self, type, value, traceback):
        """Exit the context manager"""
        self._attempt = 0
        self._current_wait = 0.0
        self._last_wait_time = 0.0

    def set_initial_interval(self, interval_timer: Duration | int) -> "RetryPolicy":
        """Configure the intial retry wait period in seconds"""
        self._intial_interval = interval_timer
        return self

    def set_maximum_interval(self, interval_time: Duration | int) -> "RetryPolicy":
        """Configure the maximum runtime in seconds"""
        self._max_interval = interval_time
        return self

    def set_backoff_coefficient(self, coeffficient: int | float) -> "RetryPolicy":
        """Configure the backoff coefficient (Exponential Backoff)"""
        self._backoff_rate = coeffficient
        self._calc_wait_interval = self.calc_backoff_wait_interval
        return self

    def set_jitter_backoff(
        self,
        power: float,
        add: bool = True,
        min_limit: int = 0,
        max_limit: int = 5,
        **options,
    ) -> "RetryPolicy":
        """Adding jitter provides a way to break the synchronization across the clients thereby avoiding collisions by setting the limits of the amount of random jitter"""
        self._random_fn = options.get("randon_fn", random.randint)
        self._min_jitter = min_limit
        self._max_jitter = max_limit
        self._power = power
        self._add = add
        self._calc_wait_interval = self.calc_jitter_wait_interval
        return self

    def set_exponential_backoff(self, multiplier: float):
        """Provide a breathing space to the system to recover from intermittent failures, or even more severe problems"""
        self._multiplier = multiplier
        self._calc_wait_interval = self.calc_exponential_wait_interval
        return self

    def set_maximum_attempts(self, attempts: int) -> "RetryPolicy":
        """Maximum number of retries (excluding intial)"""
        self._max_attempts = attempts
        return self

    def calc_backoff_wait_interval(self) -> float:
        """Basic backoff using coefficient"""
        return self._intial_interval + (self._backoff_rate * self._last_wait_time)

    def calc_jitter_wait_interval(self) -> float:
        """Calculate the current wait jitter wait interval"""
        random_interval = self._random_fn(self._min_jitter, self._max_jitter)
        if self._add:
            wait_interval = (self._initial_interval * 2**self._power) + random_interval
        else:
            wait_interval = (self._initial_interval * 2**self._power) - random_interval
        return wait_interval

    def calc_exponential_wait_interval(self) -> float:
        """Calculate the current wait exponential wait interval"""
        return self._intial_interval * self._multiplier**self.attempts

    @property
    def run_time(self) -> float:
        """Get the total runtime of the method being tried in seconds"""
        return time.time() - self._start_time

    @property
    def attempts(self) -> int:
        """Number of attemps made (including initial attempt)"""
        return self._attempt

    def run_resource(self, fn: Callable, success_fn: Callable) -> RetryLogs:
        """Run a callable function, with the retry policy"""
        successful_operation = False
        retry_log = RetryLogs()
        while (
            self._start_time + self._current_wait
            <= self._start_time + self._max_interval
        ) and self._attempt <= self._max_attempts:
            self._attempt += 1
            time.sleep(self._current_wait)
            result = fn()
            pass_run = success_fn(result, self)
            retry_log.append(
                LogEntry(
                    {
                        "attempt": self._attempt,
                        "pass": pass_run,
                        "total_retry_time": f"{self.run_time:.2f}",
                    }
                )
            )
            if result is not None:
                retry_log[-1]["result"] = result
            if pass_run:
                successful_operation = True
                break
            self._last_wait_time = self._current_wait
            self._current_wait = self._calc_wait_interval()
            retry_log[-1]['next_attempt_in'] = self._current_wait
        if successful_operation and self.attempts > 1:
            print(
                f"Operation passed after {self.attempts} attempts lasting {self.run_time:.2f}"
            )
        elif not successful_operation:
            print(
                f"Operation failed after {self.attempts} attempts lasting {self.run_time:.2f}"
            )
        return retry_log


if __name__ == "__main__":
    import operator as op
    import pprint
    import predictable_random as pr

    def success(result: Any, retry_policy: RetryPolicy) -> bool:
        """Passes application on chosen policy after 3 attempts (2 retries)"""
        if retry_policy.attempts == 3:
            return True
        return False

    def failure(result: Any, return_policy: RetryPolicy) -> bool:
        """Fails application on every attempt"""
        return False

    def run_unbound_method(a):
        """Stub Normal function (unbound method) to run"""
        print("run_unbound_method", a)

    class TestClass:
        def run_bound_method(self, a, b):
            """Stub Class instance method to run"""
            print("run_bound_method", a, b)

    # Text the durations calculated
    assert Duration.of_milliseconds(50) == 0.05
    assert Duration.of_minutes(50) == 50 * 60

    retry_policy = (
        RetryPolicy()
        .set_initial_interval(Duration.of_seconds(1))
        .set_maximum_interval(Duration.of_seconds(60))
        .set_backoff_coefficient(1.5)
        .set_maximum_attempts(5)
    )

    with retry_policy as retry:
        log_inspect = retry.run_resource(lambda: run_unbound_method(16), failure)
        attempts = retry.attempts
        exec_time = retry.run_time
    print(
        "extract",
        log_inspect[4].extract(SearchPolicies.on_value_type_and_value(int, op.ge, 2)),
    )
    print(
        "extract all",
        log_inspect.extract_entry(
            SearchPolicies.on_value_type_and_value(int, op.ge, 2)
        ),
    )
    print(
        "extract attrs", log_inspect.extract(SearchPolicies.on_value_type_and_value(int, op.ge, 2))
    )
    pprint.pprint(log_inspect)

    # Check that all retrys failed
    assert attempts == 6
    assert exec_time > 29.4 and exec_time < 30.0

    with retry_policy as retry:
        log_inspect = retry.run_resource(lambda: run_unbound_method(16), success)
        attempts = retry.attempts
        exec_time = retry.run_time
    pprint.pprint(log_inspect)

    # Check rerun recovers
    # and recovery took place on the 3rd atempt and that the time taken is as expected
    assert attempts == 3
    assert exec_time > 3.5 and exec_time < 4.0

    # Test instance method invocation
    tc = TestClass()
    with retry_policy as retry:
        log_inspect = retry.run_resource(lambda: tc.run_bound_method(10, 20), success)
        attempts = retry.attempts
        exec_time = retry.run_time
    pprint.pprint(log_inspect)

    # Test that recovery took place on the 3rd atempt and that the time taken is as expected
    assert attempts == 3
    assert exec_time > 3.5 and exec_time < 4.0

    print("exponential retry policy")
    exponential_retry_policy = (
        RetryPolicy()
        .set_initial_interval(Duration.of_seconds(1))
        .set_exponential_backoff(3)
        .set_maximum_attempts(5)
    )

    with exponential_retry_policy as retry:
        log_inspect = retry.run_resource(lambda: run_unbound_method(16), success)
        attempts = retry.attempts
        exec_time = retry.run_time
    pprint.pprint(log_inspect)

    assert attempts == 3
    assert exec_time > 11.95 and exec_time < 12.5

    print("jitter retry policy")
    jitter_retry_policy = (
        RetryPolicy()
        .set_initial_interval(Duration.of_seconds(1))
        .set_jitter_backoff(1.0, randon_fn=pr.not_so_random)
        .set_maximum_attempts(5)
    )

    with jitter_retry_policy as retry:
        log_inspect = retry.run_resource(lambda: tc.run_bound_method(10, 20), failure)
        attempts = retry.attempts
        exec_time = retry.run_time
    pprint.pprint(log_inspect)

    assert attempts == 6
    assert exec_time > 27.0 and exec_time < 27.4
