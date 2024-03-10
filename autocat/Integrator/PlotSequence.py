import matplotlib
import matplotlib.pyplot as plt


def plot(data_dict, caption, file_name, y_label, **kwargs):
    """Plot the values in this dictionary"""
    # See plot parameters
    # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.plot.html
    # Default blue circles with lines
    fmt = kwargs.get('fmt', 'o-b')

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
    plt.plot(point_x, point_y, fmt)  # marker=marker, linestyle=line_style, color=color, label=None)

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


# Test plot
if __name__ == "__main__":
    test_dict = {0: 10, 1: 20, 2: 20, 3: 200, 4: 0, 5: -10, 6: -20, 7: 0, 8: -50, 9: -50, 10: -40}
    matplotlib.use('agg')
    plot(test_dict, "Title", "00_test_file", "(unit)")
    parameters = {'bottom': -100, 'top': 100, 'fmt': 'sr'}
    plot(test_dict, "Title", "01_test_file", "(unit)", **parameters)
