import matplotlib
import matplotlib.pyplot as plt


def plot(data_dict, caption, file_name, y_label, parameters=None):
    """Plot the values in this dictionary"""
    marker = 'o'
    color = 'b'
    line_style = '-'
    if parameters is not None:
        marker = 's'
        if 'color' in parameters:
            color = parameters['color']
        line_style = ''
        if 'bottom' in parameters and 'top' in parameters:
            plt.ylim(parameters['bottom'], parameters['top'])
            # plt.axis(ymin=parameters['bottom'], ymax=parameters['top'])
            point_x = [key for key, value in data_dict.items() if parameters['bottom'] < value < parameters['top']]
            point_y = [value for value in data_dict.values() if parameters['bottom'] < value < parameters['top']]
            plt.plot(0, parameters['top'], marker='o')
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
    plt.plot(point_x, point_y, marker=marker, linestyle=line_style, color=color, label=None)
    if parameters is not None:
        plt.plot(0, parameters['top'], marker='.', color='w')
        plt.plot(0, parameters['bottom'], marker='.', color='w')

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
    parameters_100 = {'bottom': -100, 'top': 100, 'color': 'r'}
    plot(test_dict, "Title", "test_file", "(unit)", parameters_100)
