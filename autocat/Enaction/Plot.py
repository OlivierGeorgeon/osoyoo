import matplotlib.pyplot as plt


def plot(data_dict, caption=""):
    """Plot the values in this dictionary"""
    point_x = list(data_dict.keys())
    point_y = list(data_dict.values())

    # Create the figure
    plt.figure(figsize=(6, 3))
    # Set plot properties
    plt.title(caption)
    plt.xlabel('clock')
    plt.ylabel('prediction error')
    # plt.axhline(0, color='black', linewidth=0.5)
    # plt.axvline(0, color='black', linewidth=0.5)
    plt.grid(color='gray', linestyle='--', linewidth=0.5)
    # plt.legend()
    # plt.axis('equal')  # Ensure equal scaling of axes

    # The points
    plt.plot(point_x, point_y, marker='o', linestyle='-', color='b', label=None)

    # Show the plot
    # plt.ion()
    # plt.draw()
    plt.show()
    # plt.pause(1)
    # plt.savefig("test.pdf")


# Test plot
if __name__ == "__main__":
    test_dict = {0: 1, 1: 2, 2: 2, 3: 1, 4: 0}
    plot(test_dict, "Test")
