"""
Generate a single graph for the hill climber algorithm that uses different other
algorithms as their starting solution.
"""

import matplotlib.pyplot as plt

from code.algorithms.greedy import Greedy
from code.algorithms.hillclimber import HillClimber
from code.algorithms.randomizer import Randomizer


def plot_hillclimber_stats(iterations: int) -> None:
    """
    Plot hill climber statistics using multiple algoritms in a single graph.
    """
    stats = {}
    algs = [Randomizer, Greedy]
    for alg in algs:
        instance = alg()
        hc = HillClimber(instance)
        hc.run(iterations)
        class_name = instance.__class__.__name__
        stats[class_name] = hc.statistics

    for (class_name, stats) in stats.items():
        plt.xlabel('# of iterations')
        plt.ylabel('# of malus points')

        x = [stat['iteration'] for stat in stats]
        y = [stat['malus_score'] for stat in stats]
        plt.plot(x, y, label=class_name)

    plt.legend()
    plt.title(f'HillClimber (iterations = {iterations})')
    plt.show()
