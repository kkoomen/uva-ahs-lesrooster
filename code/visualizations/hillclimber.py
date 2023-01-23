"""
Generate a single graph for the hill climber algorithm that uses different other
algorithms as their starting solution.
"""

import matplotlib.pyplot as plt

from code.algorithms.greedy import Greedy, GreedyLSD
from code.algorithms.hillclimber import HillClimber
from code.algorithms.randomizer import Randomizer


def plot_hillclimber_stats(iterations: int) -> None:
    """
    Plot hill climber statistics using multiple algoritms in a single graph.
    """
    stats = {}
    algs = [Randomizer, Greedy, GreedyLSD]
    for class_ref in algs:
        instance = class_ref()
        hc = HillClimber(instance)
        hc.run(iterations)
        class_name = instance.__class__.__name__
        stats[class_name] = hc.statistics

    for (class_name, stats) in stats.items():
        plt.xlabel('iterations')
        plt.ylabel('malus points')

        x = [stat['iteration'] for stat in stats]
        y = [stat['malus_score'] for stat in stats]
        plt.plot(x, y, label=class_name)

    plt.legend()
    plt.title(f'HillClimber (iterations = {iterations})')
    plt.show()
