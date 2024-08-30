import matplotlib
import matplotlib.pyplot as plt
import networkx as nx


def plot(data_dict, caption, file_name, y_label, **kwargs):
    """Plot the values in this dictionary"""
    # See plot parameters at
    # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.plot.html
    # Default blue circles size 12 with lines
    fmt = kwargs.get('fmt', 'o-b')
    marker_size = kwargs.get('marker_size', 12)

    # Filter out the points out of range y
    if 'bottom' in kwargs and 'top' in kwargs:
        plt.ylim(kwargs['bottom'], kwargs['top'])
        point_x = [key for key, value in data_dict.items() if kwargs['bottom'] < value < kwargs['top']]
        point_y = [value for value in data_dict.values() if kwargs['bottom'] < value < kwargs['top']]
    else:
        point_x = list(data_dict.keys())
        point_y = list(data_dict.values())

    # Create the figure
    plt.figure(figsize=(6, 2))
    # Set plot properties
    plt.title(caption)
    plt.xlabel('Step')
    plt.ylabel(y_label)
    plt.axhline(0, color='black', linewidth=0.5)
    # plt.axvline(0, color='black', linewidth=0.5)
    plt.grid(color='gray', linestyle='--', linewidth=0.5)
    # plt.legend()
    # plt.axis('equal')  # Ensure equal scaling of axes

    # The points
    plt.plot(point_x, point_y, fmt, markersize=marker_size)  # marker=marker, linestyle=line_style, color=color, label=None)

    # Plot invisible points to scale the y axis
    if 'bottom' in kwargs and 'top' in kwargs:
        plt.plot(0, kwargs['top'], marker=' ')
        plt.plot(0, kwargs['bottom'], marker=' ')

    # Show the plot
    # plt.ion()
    # plt.draw()
    # plt.show()
    # plt.pause(1)
    plt.savefig("log/" + file_name + ".pdf", bbox_inches='tight')
    plt.close()


def plot_places(G, pos):
    """Plot the graph at the given positions"""
    nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=500, font_size=16, font_color='black',
            edge_color='gray')
    # plt.show()
    plt.xlim(-1000, 1000)  # Adjust the range according to node positions
    plt.ylim(-1000, 1000)  # Adjust the range according to node positions
    plt.savefig("log/13_place_cells.pdf", bbox_inches='tight')
    plt.close()


# Test plot
if __name__ == "__main__":
    # test_dict = {0: 10, 1: 20, 2: 20, 3: 200, 4: 0, 5: -10, 6: -20, 7: 0, 8: -50, 9: -50, 10: -40}
    # matplotlib.use('agg')
    # plot(test_dict, "Title", "00_test_file", "(unit)")
    # parameters = {'bottom': -100, 'top': 100, 'fmt': 'sr', 'marker_size': 5}
    # plot(test_dict, "Title", "01_test_file", "(unit)", **parameters)

    # Plot graph
    G = nx.Graph()
    # Adding nodes
    G.add_node(1)
    G.add_node(2)
    G.add_node(3)
    # Adding edges
    G.add_edge(1, 2)
    G.add_edge(2, 3)
    G.add_edge(3, 1)
    # Step 3: Specify the positions of the nodes
    pos = {
        1: (0, 0),  # Position of node 1
        2: (100, 100),  # Position of node 2
        3: (200, 0)  # Position of node 3
    }
    plot_places(G, pos)
