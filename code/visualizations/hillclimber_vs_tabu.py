"""
Plot a single graph showing the result of hillclimber and tabu search.
"""

import concurrent.futures
import matplotlib.pyplot as plt

from code.algorithms.hillclimber import HillClimber
from code.algorithms.tabu_search import TabuSearch


def plot_hillclimber_vs_tabu_stats(iterations: int) -> None:
    """
    Run the hill climber and tabu search in parallel and plot the results.
    """
    stats = {}
    algorithms = [TabuSearch, HillClimber]

    # Run the algorithms in parallel to speed up the generation.
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(algorithms)) as executor:
        workers = []
        for class_ref in algorithms:
            def worker():
                instance = class_ref()
                instance.run(iterations)
                class_name = instance.__class__.__name__
                stats[class_name] = instance.statistics
            workers.append(executor.submit(worker))

        # Wait for all workers to be completed.
        concurrent.futures.wait(workers)

    # Plot the gathered data.
    for (class_name, stats) in stats.items():
        plt.xlabel('iterations')
        plt.ylabel('malus points')

        iterations = len(stats)
        x = range(1, iterations + 1)
        y = [stat['malus_score'] for stat in stats]
        plt.plot(x, y, label=class_name)

    plt.legend()
    plt.title(f'TabuSearch vs HillClimber (iterations = {iterations})')
    plt.show()
