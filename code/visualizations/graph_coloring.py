"""
Create a graph visualization where each vertice represents a course and the edge
in between two vertices indicates that there is at least one student enrolled in
both courses, meaning that all neighbors for a node in the graph represent the
conflicting courses for a course respectively.
"""


from code.utils.data import load_courses, load_students
import networkx as nx
import itertools
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors


def plot_course_conflict_graph():
    courses = load_courses()
    students = load_students()

    # Create the graph.
    network = nx.Graph()
    network.add_nodes_from([course.name for course in courses])

    # Get all courses that are overlapping for each student.
    list_of_overlaps = [student.enrolled_courses for student in students]

    # Create each possible combination per overlap and add it as an edge.
    for courses in list_of_overlaps:
        for pair in itertools.combinations(courses, 2):
            network.add_edge(pair[0], pair[1])

    # Color the nodes.
    nx.coloring.greedy_color(network, 'largest_first')

    # Get the amount of degrees in the network.
    n_degrees = max(dict(network.degree).values())

    # The minimum amount of colors is the n degrees + 1.
    n_colors = n_degrees + 1

    # Get a list of color names.
    color_names = list(mcolors.CSS4_COLORS.keys())[:n_colors]

    # Plot the results.
    plt.figure(figsize=(20,12))
    nx.draw(network, node_color=color_names, edge_color='lightgray', with_labels=True)
    plt.show()
