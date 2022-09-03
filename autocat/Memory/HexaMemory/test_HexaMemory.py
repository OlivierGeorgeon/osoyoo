import sys
import os
from .HexaMemory import HexaMemory

sys.path.insert(1, os.path.join(sys.path[0], '../../..'))


def test_convert_pos_in_cell():
    """Test the the alocentric hexagonal memory
    py -m stage_titouan.Memory.HexaMemory.test_HexaMemory"""
    hx = HexaMemory(20, 20, cell_radius=10)
    error = 0
    try:
        assert(hx.robot_pos_x == 0 and hx.robot_pos_y ==0)
    except AssertionError:
        error = 1
        print("Pos of the robot incorrect : ", hx.robot_pos_x, hx.robot_pos_y, " should be 0,0")
        
    try:
        assert(hx.robot_cell_x == 10 and hx.robot_cell_y == 10)
    except AssertionError:
        error = 2
        print("Cells of the robot incorrect : ", hx.robot_cell_x, hx.robot_cell_y, " should be 10,10")
        
    try:
        hx.robot_pos_x = 0
        hx.robot_pos_y = 10
        end_x,end_y = hx.convert_pos_in_cell(hx.robot_pos_x, hx.robot_pos_y)
        assert(end_x == 10 and end_y == 12)
    except AssertionError:
        error = 3
        print("Cells of the robot incorrect after moving robot up : ", end_x, end_y, " should be 10,12")
        
    try:
        hx.robot_pos_x = 0
        hx.robot_pos_y = 0
        end_x,end_y = hx.convert_pos_in_cell(hx.robot_pos_x, hx.robot_pos_y)
        assert(end_x == 10 and end_y == 10)
    except AssertionError:
        error = 4
        print("Cells of the robot incorrect after resetting robot : ", end_x, end_y, " should be 10,10")

    try:
        hx.robot_pos_x = 0
        hx.robot_pos_y = -10
        end_x,end_y = hx.convert_pos_in_cell(hx.robot_pos_x, hx.robot_pos_y)
        assert(end_x == 10 and end_y == 8)
    except AssertionError:
        error = 5
        print("Cells of the robot incorrect after moving robot down : ", end_x, end_y, " should be 10,8")
        
    hx.robot_pos_x = 0
    hx.robot_pos_y = 0

    try:
        hx.robot_pos_x = 0
        hx.robot_pos_y = -20
        end_x,end_y = hx.convert_pos_in_cell(hx.robot_pos_x, hx.robot_pos_y)
        assert(end_x == 10 and end_y == 8)
    except AssertionError:
        error = 6
        print("Cells of the robot incorrect after moving robot down : ", end_x, end_y, " should be 10,8", " error : ", error)

    try:
        hx.robot_pos_x = 0
        hx.robot_pos_y = -25
        end_x,end_y = hx.convert_pos_in_cell(hx.robot_pos_x, hx.robot_pos_y)
        assert(end_x == 10 and end_y == 8)
    except AssertionError:
        error = 7
        print("Cells of the robot incorrect after moving robot down : ", end_x, end_y, " should be 10,8", " error : ", error)
        error = 7

    try:
        hx.robot_pos_x = 0
        hx.robot_pos_y = -27
        end_x,end_y = hx.convert_pos_in_cell(hx.robot_pos_x, hx.robot_pos_y)
        assert(end_x == 10 and end_y == 6)
    except AssertionError:
        error = 8
        print("Cells of the robot incorrect after moving robot down : ", end_x, end_y, " should be 10,6", " error : ", error)

    try:
        hx.robot_pos_x = 0
        hx.robot_pos_y = 26
        end_x,end_y = hx.convert_pos_in_cell(hx.robot_pos_x, hx.robot_pos_y)
        assert(end_x == 10 and end_y == 14)
    except AssertionError:
        error = 9
        print("Cells of the robot incorrect after moving robot down : ", end_x, end_y, " should be 10,14", " error : ", error)

    try:
        hx.robot_pos_x = 11
        hx.robot_pos_y = 0
        end_x,end_y = hx.convert_pos_in_cell(hx.robot_pos_x, hx.robot_pos_y)
        assert(end_x == 10 and end_y == 11)
    except AssertionError:
        error = 10
        print("Cells of the robot incorrect after moving robot right : ", end_x, end_y, " should be 10,11", " error : ", error)

    try:
        hx.robot_pos_x = 25
        hx.robot_pos_y = 0
        end_x,end_y = hx.convert_pos_in_cell(hx.robot_pos_x, hx.robot_pos_y)
        assert(end_x == 11 and end_y == 10)
    except AssertionError:
        error = 11
        print("Cells of the robot incorrect after moving robot right : ", end_x, end_y, " should be 11,10", " error : ", error)
        
    try:
        hx.robot_pos_x = 21
        hx.robot_pos_y = 0
        end_x,end_y = hx.convert_pos_in_cell(hx.robot_pos_x, hx.robot_pos_y)
        assert(end_x == 11 and end_y == 10)
    except AssertionError:
        error = 12.1
        print("Cells of the robot incorrect after moving robot right : ", end_x, end_y, " should be 11,10", " error : ", error)
    
    try:
        hx.robot_pos_x = 26
        hx.robot_pos_y = 0
        end_x,end_y = hx.convert_pos_in_cell(hx.robot_pos_x, hx.robot_pos_y)
        assert(end_x == 11 and end_y == 10)
    except AssertionError:
        error = 12.11
        print("Cells of the robot incorrect after moving robot right : ", end_x, end_y, " should be 11,10", " error : ", error)
        
    try:
        hx.robot_pos_x = 41
        hx.robot_pos_y = 0
        end_x,end_y = hx.convert_pos_in_cell(hx.robot_pos_x, hx.robot_pos_y)
        assert(end_x == 11 and end_y == 11)
    except AssertionError:
        error = 12.2
        print("Cells of the robot incorrect after moving robot right : ", end_x, end_y, " should be 11,11", " error : ", error)

    try:
        hx.robot_pos_x = 49
        hx.robot_pos_y = 0
        end_x,end_y = hx.convert_pos_in_cell(hx.robot_pos_x, hx.robot_pos_y)
        assert(end_x == 11 and end_y == 11)
    except AssertionError:
        error = 12.3
        print("Cells of the robot incorrect after moving robot right : ", end_x, end_y, " should be 11,11", " error : ", error)
    
    try:
        hx.robot_pos_x = 50
        hx.robot_pos_y = 0
        end_x,end_y = hx.convert_pos_in_cell(hx.robot_pos_x, hx.robot_pos_y)
        assert(end_x == 11 and end_y == 11)
    except AssertionError:
        error = 12.5
        print("Cells of the robot incorrect after moving robot right : ", end_x, end_y, " should be 11,11", " error : ", error)
        
    try:
        hx.robot_pos_x = 52
        hx.robot_pos_y = 0
        end_x,end_y = hx.convert_pos_in_cell(hx.robot_pos_x, hx.robot_pos_y)
        assert(end_x == 12 and end_y == 10)
    except AssertionError:
        error = 13
        print("Cells of the robot incorrect after moving robot right : ", end_x, end_y, " should be 12,10", " error : ", error)

    try:
        hx.robot_pos_x = 8
        hx.robot_pos_y = 0
        end_x,end_y = hx.convert_pos_in_cell(hx.robot_pos_x, hx.robot_pos_y)
        assert(end_x == 10 and end_y == 10)
    except AssertionError:
        error = 14
        print("Cells of the robot incorrect after moving robot right : ", end_x, end_y, " should be 10,10", " error : ", error)

    try:
        hx.robot_pos_x = -8
        hx.robot_pos_y = 0
        end_x,end_y = hx.convert_pos_in_cell(hx.robot_pos_x, hx.robot_pos_y)
        assert(end_x == 10 and end_y == 10)
    except AssertionError:
        error = 15
        print("Cells of the robot incorrect after moving robot left : ", end_x, end_y, " should be 10,10", " error : ", error)

    try:
        hx.robot_pos_x = -11
        hx.robot_pos_y = 0
        end_x,end_y = hx.convert_pos_in_cell(hx.robot_pos_x, hx.robot_pos_y)
        assert(end_x == 9 and end_y == 11)
    except AssertionError:
        error = 16
        print("Cells of the robot incorrect after moving robot left : ", end_x, end_y, " should be 9,11", " error : ", error)

    try:
        hx.robot_pos_x = -21
        hx.robot_pos_y = 0
        end_x,end_y = hx.convert_pos_in_cell(hx.robot_pos_x, hx.robot_pos_y)
        assert(end_x == 9 and end_y == 10)
    except AssertionError:
        error = 17
        print("Cells of the robot incorrect after moving robot left : ", end_x, end_y, " should be 9,10", " error : ", error)

    try:
        hx.robot_pos_x = -41
        hx.robot_pos_y = 0
        end_x,end_y = hx.convert_pos_in_cell(hx.robot_pos_x, hx.robot_pos_y)
        assert(end_x == 8 and end_y == 11)
    except AssertionError:
        error = 18
        print("Cells of the robot incorrect after moving robot left : ", end_x, end_y, " should be 8,11", " error : ", error)
    
    try:
        hx.robot_pos_x = 11
        hx.robot_pos_y = 10
        end_x,end_y = hx.convert_pos_in_cell(hx.robot_pos_x, hx.robot_pos_y)
        assert(end_x == 10 and end_y == 11)
    except AssertionError:
        error = 19
        print("Cells of the robot incorrect after moving robot one cell upper right  ", end_x, end_y, " should be 10,11", " error : ", error)

    try:
        hx.robot_pos_x = 21
        hx.robot_pos_y = 10
        end_x,end_y = hx.convert_pos_in_cell(hx.robot_pos_x, hx.robot_pos_y)
        assert(end_x == 10 and end_y == 11)
    except AssertionError:
        error = 20
        print("Cells of the robot incorrect after moving robot two cells upper right : ", end_x, end_y, " should be 10,11", " error : ", error)

    try:
        hx.robot_pos_x = 11
        hx.robot_pos_y = -10
        end_x,end_y = hx.convert_pos_in_cell(hx.robot_pos_x, hx.robot_pos_y)
        assert(end_x == 10 and end_y == 9)
    except AssertionError:
        error = 21
        print("Cells of the robot incorrect after moving robot one cell lower right : ", end_x, end_y, " should be 10,9", " error : ", error)

    try:
        hx.robot_pos_x = -11
        hx.robot_pos_y = -10
        end_x,end_y = hx.convert_pos_in_cell(hx.robot_pos_x, hx.robot_pos_y)
        good_end_x,good_end_y = 9,9
        assert(end_x == good_end_x and end_y == good_end_y)
    except AssertionError:
        error = 22
        print("Cells of the robot incorrect after moving robot one cell lower left : ", end_x, end_y, " should be" , good_end_x,",", good_end_y, " error : ", error)

    try:
        hx.robot_pos_x = -11
        hx.robot_pos_y = 10
        end_x,end_y = hx.convert_pos_in_cell(hx.robot_pos_x, hx.robot_pos_y)
        good_end_x,good_end_y = 9,11
        assert(end_x == good_end_x and end_y == good_end_y)
    except AssertionError:
        error = 23
        print("Cells of the robot incorrect after moving robot one cell upper left : ", end_x, end_y, " should be" , good_end_x,",", good_end_y, " error : ", error)

    try:
        hx.robot_pos_x = 15
        hx.robot_pos_y = 30
        end_x,end_y = hx.convert_pos_in_cell(hx.robot_pos_x, hx.robot_pos_y)
        good_end_x,good_end_y = 10,13
        assert(end_x == good_end_x and end_y == good_end_y)
    except AssertionError:
        error = 24
        print("Cells of the robot incorrect after moving robot  : ", end_x, end_y, " should be" , good_end_x,",", good_end_y, " error : ", error)

    try:
        hx.robot_pos_x = -15
        hx.robot_pos_y = 30
        end_x,end_y = hx.convert_pos_in_cell(hx.robot_pos_x, hx.robot_pos_y)
        good_end_x,good_end_y = 9,13
        assert(end_x == good_end_x and end_y == good_end_y)
    except AssertionError:
        error = 25
        print("Cells of the robot incorrect after moving robot  : ", end_x, end_y, " should be" , good_end_x,",", good_end_y, " error : ", error)
        
    try:
        hx.robot_pos_x = 6
        hx.robot_pos_y = 12
        end_x,end_y = hx.convert_pos_in_cell(hx.robot_pos_x, hx.robot_pos_y)
        good_end_x,good_end_y = 10,12
        assert(end_x == good_end_x and end_y == good_end_y)
    except AssertionError:
        error = 26
        print("Cells of the robot incorrect after moving robot  : ", end_x, end_y, " should be" , good_end_x,",", good_end_y, " error : ", error)

    try:
        hx.robot_pos_x = 7
        hx.robot_pos_y = 12
        end_x,end_y = hx.convert_pos_in_cell(hx.robot_pos_x, hx.robot_pos_y)
        good_end_x,good_end_y = 10,11
        assert(end_x == good_end_x and end_y == good_end_y)
    except AssertionError:
        error = 27
        print("Cells of the robot incorrect after moving robot  : ", end_x, end_y, " should be" , good_end_x,",", good_end_y, " error : ", error)

    return error


def test_move():
    """blala"""
    hx = HexaMemory(20, 20, cell_radius=10)
    error = 0
    try:
        hx.robot_pos_x = 0
        hx.robot_pos_y = 0
        rotation, move_x, move_y = 0, 0, 20
        end_x, end_y = hx.move(rotation, move_x, move_y)
        good_end_x, good_end_y = 0, 20
        assert(end_x == good_end_x and end_y == good_end_y)
    except AssertionError:
        print("Cells of the robot incorrects after moving robot  : ", end_x, end_y, " should be" , good_end_x,",", good_end_y)
        error = 1

    try:
        hx.robot_pos_x = 0
        hx.robot_pos_y = 0
        rotation, move_x, move_y = 90, 0, 20
        end_x, end_y = hx.move(rotation, move_x, move_y)
        good_end_x, good_end_y = 20, 0
        assert(end_x == good_end_x and end_y == good_end_y)
    except AssertionError:
        print("Cells of the robot incorrects after moving robot  : ", end_x, end_y, " should be" , good_end_x,",", good_end_y)
        error = 2

    try:
        hx.robot_pos_x = 0
        hx.robot_pos_y = 0
        hx.robot_angle = 0
        rotation, move_x, move_y = 360,0,20
        end_x, end_y = hx.move(rotation, move_x, move_y)
        good_end_x, good_end_y = 0,20
        assert(end_x == good_end_x and end_y == good_end_y)
    except AssertionError:
        print("Cells of the robot incorrects after moving robot  : ", end_x, end_y, " should be" , good_end_x,",", good_end_y)
        error = 3

    return error


def test_new_convert_pos_to_cell():
    hx = HexaMemory(20,20,cells_radius = 10)
    error = 0

    try:
        pos_x = 11
        pos_y = 0
        end_x,end_y = hx.new_convert_pos_to_cell(pos_x,pos_y)
        good_end_x,good_end_y = 0,1
        assert(end_x == good_end_x and end_y == good_end_y)
    except AssertionError:
        print("Cells of the robot incorrects after convert_pos : ", end_x, end_y, " should be" , good_end_x,",", good_end_y)
        error = 1

    try:
        pos_x = 15
        pos_y = 15
        end_x,end_y = hx.new_convert_pos_to_cell(pos_x,pos_y)
        good_end_x,good_end_y = 0,1
        assert(end_x == good_end_x and end_y == good_end_y)
    except AssertionError:
        print("Cells of the robot incorrects after convert_pos : ", end_x, end_y, " should be" , good_end_x,",", good_end_y)
        error = 1

    try:
        pos_x = 8
        pos_y = 8
        end_x,end_y = hx.new_convert_pos_to_cell(pos_x,pos_y)
        good_end_x,good_end_y = 0,1
        assert(end_x == good_end_x and end_y == good_end_y)
    except AssertionError:
        print("Cells of the robot incorrects after convert_pos : ", end_x, end_y, " should be" , good_end_x,",", good_end_y)
        error = 1

    try:
        pos_x = 6
        pos_y = 6
        end_x,end_y = hx.new_convert_pos_to_cell(pos_x,pos_y)
        good_end_x,good_end_y = 0,0
        assert(end_x == good_end_x and end_y == good_end_y)
    except AssertionError:
        print("Cells of the robot incorrects after convert_pos : ", end_x, end_y, " should be" , good_end_x,",", good_end_y)
        error = 1
    return error


# Run the test
# py -m stage_titouan.Memory.HexaMemory.test_HexaMemory
if __name__ == '__main__':
    error = 0
    try:
        error = test_move()
        assert(error == 0)
        print("Every test in test_move passed without error")
    except AssertionError:
        print("test_move failed with error : ", error)

    try:
        error = test_convert_pos_in_cell()
        assert(error == 0)
        print("Every test in test_convert_pos_in_cell(hx.robot_pos_x, hx.robot_pos_y) passed without error")
    except AssertionError:
        print("test_convert_robot_pos_in_robot_cell failed with error : ", error)
