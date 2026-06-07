import time
import cProfile
from collections.abc import Callable


def run_collect_info(func: Callable, func_args: tuple, do_name: str):
    profiler = cProfile.Profile()
    profiler.enable()

    start = time.perf_counter()
    result = func(*func_args)
    end = time.perf_counter()

    profiler.disable()

    print(f'\n\n{do_name}: {end - start} seconds')
    profiler.print_stats(sort='cumulative')

    return result
