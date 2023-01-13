from .AllocentricMemory import AllocentricMemory


def test_convert_pos_in_cell():
    """Test the function convert_pos_in_cell()"""
    hx = AllocentricMemory(20, 20, cell_radius=10)
    error = 0

    # Test the initial position of the robot
    try:
        assert(round(hx.robot_point[0]) == 0 and round(hx.robot_point[1]) == 0)
    except AssertionError:
        error = 1
        print("Pos of the robot incorrect : ", round(hx.robot_point[0]), round(hx.robot_point[1]), " should be 0,0")
        
    # Test the initial cell of the robot
    try:
        assert(hx.robot_cell_x == 10 and hx.robot_cell_y == 10)
    except AssertionError:
        error = 2
        print("Cell of the robot at origin incorrect : ", hx.robot_cell_x, hx.robot_cell_y, " should be 10,10")

    # Robot 10mm up from origin
    hx.robot_point = [0, 10, 0]
    end_x, end_y = hx.convert_pos_in_cell(round(hx.robot_point[0]), round(hx.robot_point[1]))
    try:
        assert(end_x == 10 and end_y == 12)
    except AssertionError:
        error = 3
        print("Cell of the robot incorrect after moving robot up : ", end_x, end_y, " should be 10,12")
        
    # Robot at origin
    try:
        hx.robot_point = [0, 0, 0]
        end_x, end_y = hx.convert_pos_in_cell(round(hx.robot_point[0]), round(hx.robot_point[1]))
        assert(end_x == 10 and end_y == 10)
    except AssertionError:
        error = 4
        print("Cell of the robot at origin: ", end_x, end_y, " should be 10,10")

    # Robot 10mm down from origin
    try:
        hx.robot_point = [0, -10, 0]
        end_x, end_y = hx.convert_pos_in_cell(round(hx.robot_point[0]), round(hx.robot_point[1]))
        assert(end_x == 10 and end_y == 8)
    except AssertionError:
        error = 5
        print("Cell of the robot 10mm down incorrect: ", end_x, end_y, " should be 10,8")
        
    hx.robot_point = [0, 0, 0]

    # Robot 20mm down from origin
    try:
        hx.robot_point = [0, -20, 0]
        end_x, end_y = hx.convert_pos_in_cell(round(hx.robot_point[0]), round(hx.robot_point[1]))
        assert(end_x == 10 and end_y == 8)
    except AssertionError:
        error = 6
        print("Cell of the robot 20mm down incorrect: ", end_x, end_y, " should be 10,8", " error : ", error)

    # Robot 25mm down from origin
    try:
        hx.robot_point = [0, -25, 0]
        end_x, end_y = hx.convert_pos_in_cell(round(hx.robot_point[0]), round(hx.robot_point[1]))
        assert(end_x == 10 and end_y == 8)
    except AssertionError:
        error = 7
        print("Cell of the robot 25mm down incorrect: ", end_x, end_y, " should be 10,8", " error : ", error)
        error = 7

    # Robot 27mm down from origin
    try:
        hx.robot_point = [0, -27, 0]
        end_x, end_y = hx.convert_pos_in_cell(round(hx.robot_point[0]), round(hx.robot_point[1]))
        assert(end_x == 10 and end_y == 6)
    except AssertionError:
        error = 8
        print("Cell of the robot 27mm down incorrect: ", end_x, end_y, " should be 10,6", " error : ", error)

    # Robot 26mm up from origin
    try:
        hx.robot_point = [0, 26, 0]
        end_x, end_y = hx.convert_pos_in_cell(round(hx.robot_point[0]), round(hx.robot_point[1]))
        assert(end_x == 10 and end_y == 14)
    except AssertionError:
        error = 9
        print("Cell of the robot 26mm up incorrect: ", end_x, end_y, " should be 10,14", " error : ", error)

    # Robot 11mm right from origin
    try:
        hx.robot_point = [11, 0, 0]
        end_x, end_y = hx.convert_pos_in_cell(round(hx.robot_point[0]), round(hx.robot_point[1]))
        assert(end_x == 10 and end_y == 11)
    except AssertionError:
        error = 10
        print("Cell of the robot 11mm right incorrect: ", end_x, end_y, " should be 10,11", " error : ", error)

    # Robot 25mm right from origin
    try:
        hx.robot_point = [25, 0, 0]
        end_x, end_y = hx.convert_pos_in_cell(round(hx.robot_point[0]), round(hx.robot_point[1]))
        assert(end_x == 11 and end_y == 10)
    except AssertionError:
        error = 11
        print("Cell of the robot 25mm right incorrect: ", end_x, end_y, " should be 11,10", " error : ", error)
        
    # Robot 21mm right from origin
    try:
        hx.robot_point = [21, 0, 0]
        end_x, end_y = hx.convert_pos_in_cell(round(hx.robot_point[0]), round(hx.robot_point[1]))
        assert(end_x == 11 and end_y == 10)
    except AssertionError:
        error = 12.1
        print("Cell of the robot 21mm right incorrect: ", end_x, end_y, " should be 11,10", " error : ", error)
    
    # Robot 26mm right from origin
    try:
        hx.robot_point = [26, 0, 0]
        end_x, end_y = hx.convert_pos_in_cell(round(hx.robot_point[0]), round(hx.robot_point[1]))
        assert(end_x == 11 and end_y == 10)
    except AssertionError:
        error = 12.11
        print("Cell of the robot 26mm right incorrect: ", end_x, end_y, " should be 11,10", " error : ", error)
        
    # Robot 41mm right from origin
    try:
        hx.robot_point = [41, 0, 0]
        end_x, end_y = hx.convert_pos_in_cell(round(hx.robot_point[0]), round(hx.robot_point[1]))
        assert(end_x == 11 and end_y == 11)
    except AssertionError:
        error = 12.2
        print("Cell of the robot 41mm right incorrect: ", end_x, end_y, " should be 11,11", " error : ", error)

    # Robot 49mm right from origin
    try:
        hx.robot_point = [49, 0, 0]
        end_x, end_y = hx.convert_pos_in_cell(round(hx.robot_point[0]), round(hx.robot_point[1]))
        assert(end_x == 11 and end_y == 11)
    except AssertionError:
        error = 12.3
        print("Cell of the robot 49mm right incorrect: ", end_x, end_y, " should be 11,11", " error : ", error)
    
    # Robot 50mm right from origin
    try:
        hx.robot_point = [50, 0, 0]
        end_x, end_y = hx.convert_pos_in_cell(round(hx.robot_point[0]), round(hx.robot_point[1]))
        assert(end_x == 11 and end_y == 11)
    except AssertionError:
        error = 12.5
        print("Cell of the robot 50mm right incorrect: ", end_x, end_y, " should be 11,11", " error : ", error)
        
    # Robot 52mm right from origin
    try:
        hx.robot_point = [52, 0, 0]
        end_x, end_y = hx.convert_pos_in_cell(round(hx.robot_point[0]), round(hx.robot_point[1]))
        assert(end_x == 12 and end_y == 10)
    except AssertionError:
        error = 13
        print("Cell of the robot 52mm right incorrect: ", end_x, end_y, " should be 12,10", " error : ", error)

    # Robot 8mm right from origin
    try:
        hx.robot_point = [8, 0, 0]
        end_x, end_y = hx.convert_pos_in_cell(round(hx.robot_point[0]), round(hx.robot_point[1]))
        assert(end_x == 10 and end_y == 10)
    except AssertionError:
        error = 14
        print("Cell of the robot 8mm right incorrect: ", end_x, end_y, " should be 10,10", " error : ", error)

    # Robot 8mm left from origin
    try:
        hx.robot_point = [-8, 0, 0]
        end_x, end_y = hx.convert_pos_in_cell(round(hx.robot_point[0]), round(hx.robot_point[1]))
        assert(end_x == 10 and end_y == 10)
    except AssertionError:
        error = 15
        print("Cell of the robot 8mm left incorrect: ", end_x, end_y, " should be 10,10", " error : ", error)

    # Robot 11mm left from origin
    try:
        hx.robot_point = [-11, 0, 0]
        end_x, end_y = hx.convert_pos_in_cell(round(hx.robot_point[0]), round(hx.robot_point[1]))
        assert(end_x == 9 and end_y == 11)
    except AssertionError:
        error = 16
        print("Cell of the robot 11mm left incorrect: ", end_x, end_y, " should be 9,11", " error : ", error)

    # Robot 21mm left from origin
    try:
        hx.robot_point = [-21, 0, 0]
        end_x, end_y = hx.convert_pos_in_cell(round(hx.robot_point[0]), round(hx.robot_point[1]))
        assert(end_x == 9 and end_y == 10)
    except AssertionError:
        error = 17
        print("Cell of the robot 21mm left incorrect: ", end_x, end_y, " should be 9,10", " error : ", error)

    # Robot 41mm left from origin
    try:
        hx.robot_point = [-41, 0, 0]
        end_x, end_y = hx.convert_pos_in_cell(round(hx.robot_point[0]), round(hx.robot_point[1]))
        assert(end_x == 8 and end_y == 11)
    except AssertionError:
        error = 18
        print("Cell of the robot 41mm left incorrect: ", end_x, end_y, " should be 8,11", " error : ", error)

    # Robot 11mm right and 10mm up from origin
    try:
        hx.robot_point = [11, 10, 0]
        end_x, end_y = hx.convert_pos_in_cell(round(hx.robot_point[0]), round(hx.robot_point[1]))
        assert(end_x == 10 and end_y == 11)
    except AssertionError:
        error = 19
        print("Cell of the robot 11mm right, 10mm up incorrect: ", end_x, end_y, " should be 10,11", " error : ", error)

    # Robot 21mm right and 10mm up from origin
    try:
        hx.robot_point = [21, 10, 0]
        end_x, end_y = hx.convert_pos_in_cell(round(hx.robot_point[0]), round(hx.robot_point[1]))
        assert(end_x == 10 and end_y == 11)
    except AssertionError:
        error = 20
        print("Cell of the robot 21mm right, 10mm up incorrect: ", end_x, end_y, " should be 10,11", " error : ", error)

    # Robot 21mm right and 10mm down from origin
    try:
        hx.robot_point = [11, -10, 0]
        end_x, end_y = hx.convert_pos_in_cell(round(hx.robot_point[0]), round(hx.robot_point[1]))
        assert(end_x == 10 and end_y == 9)
    except AssertionError:
        error = 21
        print("Cell of the robot (11,-10) right, down incorrect: ", end_x, end_y, " should be 10,9", " error : ", error)

    # Robot 11mm left and 10mm down from origin
    good_end_x, good_end_y = 9, 9
    hx.robot_point = [-11, -10, 0]
    end_x, end_y = hx.convert_pos_in_cell(round(hx.robot_point[0]), round(hx.robot_point[1]))
    try:
        assert(end_x == good_end_x and end_y == good_end_y)
    except AssertionError:
        error = 22
        print("Cell of the robot (-11,-10) left, down incorrect: ", end_x, end_y, " should be", good_end_x, ",",
              good_end_y, " error : ", error)

    # Robot 11mm left and 10mm up from origin
    try:
        hx.robot_point = [-11, 10, 0]
        end_x, end_y = hx.convert_pos_in_cell(round(hx.robot_point[0]), round(hx.robot_point[1]))
        good_end_x, good_end_y = 9, 11
        assert(end_x == good_end_x and end_y == good_end_y)
    except AssertionError:
        error = 23
        print("Cell of the robot (-11,10) left, up incorrect: ", end_x, end_y, " should be", good_end_x, ",",
              good_end_y, " error : ", error)

    # Robot 15mm right and 30mm up from origin
    try:
        hx.robot_point = [15, 30, 0]
        end_x, end_y = hx.convert_pos_in_cell(round(hx.robot_point[0]), round(hx.robot_point[1]))
        good_end_x, good_end_y = 10, 13
        assert(end_x == good_end_x and end_y == good_end_y)
    except AssertionError:
        error = 24
        print("Cell of the robot incorrect after moving robot: ", end_x, end_y, " should be", good_end_x, ",",
              good_end_y, " error : ", error)

    try:
        hx.robot_point = [-15, 30, 0]
        end_x, end_y = hx.convert_pos_in_cell(round(hx.robot_point[0]), round(hx.robot_point[1]))
        good_end_x, good_end_y = 9, 13
        assert(end_x == good_end_x and end_y == good_end_y)
    except AssertionError:
        error = 25
        print("Cell of the robot incorrect after moving robot  : ", end_x, end_y, " should be", good_end_x, ",",
              good_end_y, " error : ", error)
        
    try:
        hx.robot_point = [6, 12, 0]
        end_x, end_y = hx.convert_pos_in_cell(round(hx.robot_point[0]), round(hx.robot_point[1]))
        good_end_x, good_end_y = 10, 12
        assert(end_x == good_end_x and end_y == good_end_y)
    except AssertionError:
        error = 26
        print("Cell of the robot incorrect after moving robot  : ", end_x, end_y, " should be", good_end_x, ",",
              good_end_y, " error : ", error)

    try:
        hx.robot_point = [7, 12, 0]
        end_x, end_y = hx.convert_pos_in_cell(round(hx.robot_point[0]), round(hx.robot_point[1]))
        good_end_x, good_end_y = 10, 11
        assert(end_x == good_end_x and end_y == good_end_y)
    except AssertionError:
        error = 27
        print("Cell of the robot incorrect after moving robot  : ", end_x, end_y, " should be", good_end_x, ",",
              good_end_y, " error : ", error)

    return error


def test_move():
    """Test the function move()"""
    hx = AllocentricMemory(20, 20, cell_radius=10)
    error = 0

    # Sweep left from Origin (orientation East)
    good_end_x, good_end_y = 0, 20  # OG 23/09/2022
    hx.robot_point = [0, 0, 0]
    rotation = 0
    move = [0, 20, 0]
    end_x, end_y, _ = hx.move(rotation, move)
    try:
        assert(end_x == good_end_x and end_y == good_end_y)
    except AssertionError:
        print("Position incorrect after sweeping left: ", end_x, end_y, " should be", good_end_x, ",", good_end_y)
        error = 1

    # Turn South and sweep left
    try:
        hx.robot_point = [0, 0, 0]
        rotation = -3.14/2
        move = [0, 20, 0]
        end_x, end_y, _ = hx.move(rotation, move)
        good_end_x, good_end_y = 20, 0
        assert(end_x == good_end_x and end_y == good_end_y)
    except AssertionError:
        print("Position incorrect after rotate south and sweep left: ", end_x, end_y, " should be", good_end_x, ",",
              good_end_y)
        error = 2

    # Move forward from Origin
    try:
        hx.robot_point = [0, 0, 0]
        hx.robot_angle = 0
        rotation = 0
        move = [20, 0, 0]
        end_x, end_y, _ = hx.move(rotation, move)
        good_end_x, good_end_y = 20, 0
        assert(end_x == good_end_x and end_y == good_end_y)
    except AssertionError:
        print("Position incorrect after moving forward from origin: ", end_x, end_y, " should be", good_end_x, ",",
              good_end_y)
        error = 3

    return error
