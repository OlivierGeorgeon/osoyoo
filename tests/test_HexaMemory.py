
import sys
import os
import time

sys.path.insert(1, os.path.join(sys.path[0], '..'))
from HexaMemory import HexaMemory
def test_convert_robot_pos_in_robot_cell():
    """Test the"""
    hx = HexaMemory(20,20,cells_radius = 10)
    error = 0
    try :
        assert(hx.robot_pos_x == 0 and hx.robot_pos_y ==0)
    except AssertionError:
        print("Pos of the robot incorrects : ", hx.robot_pos_x, hx.robot_pos_y, " should be 0,0")
        error = 1

    
    try :
        assert(hx.robot_cell_x == 10 and hx.robot_cell_y == 10)
    except AssertionError:
        print("Cells of the robot incorrects : ", hx.robot_cell_x, hx.robot_cell_y, " should be 10,10")
        error = 2


    try :
        hx.robot_pos_x = 0
        hx.robot_pos_y = 10
        end_x,end_y = hx.convert_robot_pos_in_robot_cell()
        assert(end_x == 10 and end_y == 12)
    except AssertionError:
        print("Cells of the robot incorrects after moving robot up : ", end_x, end_y, " should be 10,12")
        error = 3


    try :
        hx.robot_pos_x = 0
        hx.robot_pos_y = 0
        end_x,end_y = hx.convert_robot_pos_in_robot_cell()
        assert(end_x == 10 and end_y == 10)
    except AssertionError:
        print("Cells of the robot incorrects after resetting robot : ", end_x, end_y, " should be 10,10")
        error = 4

    try :
        hx.robot_pos_x = 0
        hx.robot_pos_y = -10
        end_x,end_y = hx.convert_robot_pos_in_robot_cell()
        assert(end_x == 10 and end_y == 8)
    except AssertionError:
        print("Cells of the robot incorrects after moving robot down : ", end_x, end_y, " should be 10,8")
        error = 5
    hx.robot_pos_x = 0
    hx.robot_pos_y = 0

    try :
        hx.robot_pos_x = 0
        hx.robot_pos_y = -20
        end_x,end_y = hx.convert_robot_pos_in_robot_cell()
        assert(end_x == 10 and end_y == 8)
    except AssertionError:
        print("Cells of the robot incorrects after moving robot down : ", end_x, end_y, " should be 10,8")
        error = 6

    try :
        hx.robot_pos_x = 0
        hx.robot_pos_y = -25
        end_x,end_y = hx.convert_robot_pos_in_robot_cell()
        assert(end_x == 10 and end_y == 8)
    except AssertionError:
        print("Cells of the robot incorrects after moving robot down : ", end_x, end_y, " should be 10,8")
        error = 7

    try :
        hx.robot_pos_x = 0
        hx.robot_pos_y = -27
        end_x,end_y = hx.convert_robot_pos_in_robot_cell()
        assert(end_x == 10 and end_y == 6)
    except AssertionError:
        print(int(-0.77))
        print("Cells of the robot incorrects after moving robot down : ", end_x, end_y, " should be 10,6")
        error = 8

    try :
        hx.robot_pos_x = 0
        hx.robot_pos_y = 26
        end_x,end_y = hx.convert_robot_pos_in_robot_cell()
        assert(end_x == 10 and end_y == 14)
    except AssertionError:
        print("Cells of the robot incorrects after moving robot down : ", end_x, end_y, " should be 10,14")
        error = 9


    try :
        hx.robot_pos_x = 11
        hx.robot_pos_y = 0
        end_x,end_y = hx.convert_robot_pos_in_robot_cell()
        assert(end_x == 10 and end_y == 11)
    except AssertionError:
        print("Cells of the robot incorrects after moving robot right : ", end_x, end_y, " should be 10,11")
        error = 10

    try :
        hx.robot_pos_x = 25
        hx.robot_pos_y = 0
        end_x,end_y = hx.convert_robot_pos_in_robot_cell()
        assert(end_x == 11 and end_y == 10)
    except AssertionError:
        print("Cells of the robot incorrects after moving robot right : ", end_x, end_y, " should be 11,10")
        error = 11

    try :
        hx.robot_pos_x = 41
        hx.robot_pos_y = 0
        end_x,end_y = hx.convert_robot_pos_in_robot_cell()
        assert(end_x == 11 and end_y == 11)
    except AssertionError:
        print("Cells of the robot incorrects after moving robot right : ", end_x, end_y, " should be 11,11")
        error = 12
    try :
        hx.robot_pos_x = 51
        hx.robot_pos_y = 0
        end_x,end_y = hx.convert_robot_pos_in_robot_cell()
        assert(end_x == 12 and end_y == 10)
    except AssertionError:
        print("Cells of the robot incorrects after moving robot right : ", end_x, end_y, " should be 12,10")
        error = 13

    try :
        hx.robot_pos_x = 8
        hx.robot_pos_y = 0
        end_x,end_y = hx.convert_robot_pos_in_robot_cell()
        assert(end_x == 10 and end_y == 10)
    except AssertionError:
        print("Cells of the robot incorrects after moving robot right : ", end_x, end_y, " should be 10,10")
        error = 14

    try :
        hx.robot_pos_x = -8
        hx.robot_pos_y = 0
        end_x,end_y = hx.convert_robot_pos_in_robot_cell()
        assert(end_x == 10 and end_y == 10)
    except AssertionError:
        print("Cells of the robot incorrects after moving robot left : ", end_x, end_y, " should be 10,10")
        error = 15

    try :
        hx.robot_pos_x = -11
        hx.robot_pos_y = 0
        end_x,end_y = hx.convert_robot_pos_in_robot_cell()
        assert(end_x == 9 and end_y == 11)
    except AssertionError:
        print("Cells of the robot incorrects after moving robot left : ", end_x, end_y, " should be 9,11")
        error = 16

    try :
        hx.robot_pos_x = -21
        hx.robot_pos_y = 0
        end_x,end_y = hx.convert_robot_pos_in_robot_cell()
        assert(end_x == 9 and end_y == 10)
    except AssertionError:
        print("Cells of the robot incorrects after moving robot left : ", end_x, end_y, " should be 9,10")
        error = 17

    try :
        hx.robot_pos_x = -41
        hx.robot_pos_y = 0
        end_x,end_y = hx.convert_robot_pos_in_robot_cell()
        assert(end_x == 8 and end_y == 11)
    except AssertionError:
        print("Cells of the robot incorrects after moving robot left : ", end_x, end_y, " should be 8,11")
        error = 18

    
    try :
        hx.robot_pos_x = 11
        hx.robot_pos_y = 10
        end_x,end_y = hx.convert_robot_pos_in_robot_cell()
        assert(end_x == 10 and end_y == 11)
    except AssertionError:
        print("Cells of the robot incorrects after moving robot one cell upper right  ", end_x, end_y, " should be 10,11")
        error = 19


    try :
        hx.robot_pos_x = 21
        hx.robot_pos_y = 10
        end_x,end_y = hx.convert_robot_pos_in_robot_cell()
        assert(end_x == 11 and end_y == 12)
    except AssertionError:
        print("Cells of the robot incorrects after moving robot two cells upper right : ", end_x, end_y, " should be 11,12")
        error = 20

    try :
        hx.robot_pos_x = 11
        hx.robot_pos_y = -10
        end_x,end_y = hx.convert_robot_pos_in_robot_cell()
        assert(end_x == 10 and end_y == 9)
    except AssertionError:
        print("Cells of the robot incorrects after moving robot one cell lower right : ", end_x, end_y, " should be 10,9")
        error = 21

    try :
        hx.robot_pos_x = -11
        hx.robot_pos_y = -10
        end_x,end_y = hx.convert_robot_pos_in_robot_cell()
        good_end_x,good_end_y = 9,9
        assert(end_x == good_end_x and end_y == good_end_y)
    except AssertionError:
        print("Cells of the robot incorrects after moving robot one cell lower left : ", end_x, end_y, " should be" , good_end_x,",", good_end_y)
        error = 22

    try :
        hx.robot_pos_x = -11
        hx.robot_pos_y = 10
        end_x,end_y = hx.convert_robot_pos_in_robot_cell()
        good_end_x,good_end_y = 9,11
        assert(end_x == good_end_x and end_y == good_end_y)
    except AssertionError:
        print("Cells of the robot incorrects after moving robot one cell upper left : ", end_x, end_y, " should be" , good_end_x,",", good_end_y)
        error = 23

    try :
        hx.robot_pos_x = 15
        hx.robot_pos_y = 30
        end_x,end_y = hx.convert_robot_pos_in_robot_cell()
        good_end_x,good_end_y = 10,13
        assert(end_x == good_end_x and end_y == good_end_y)
    except AssertionError:
        print("Cells of the robot incorrects after moving robot  : ", end_x, end_y, " should be" , good_end_x,",", good_end_y)
        error = 24

    try :
        hx.robot_pos_x = -15
        hx.robot_pos_y = 30
        end_x,end_y = hx.convert_robot_pos_in_robot_cell()
        good_end_x,good_end_y = 9,13
        assert(end_x == good_end_x and end_y == good_end_y)
    except AssertionError:
        print("Cells of the robot incorrects after moving robot  : ", end_x, end_y, " should be" , good_end_x,",", good_end_y)
        error = 24

    
    return error




if __name__ == '__main__':
    error = 0
    try :
        error = test_convert_robot_pos_in_robot_cell()
        assert( error == 0 )
        print("Every test in test_convert_robot_pos_in_robot_cell() passed without error")
    except AssertionError:
        print("test_convert_robot_pos_in_robot_cell failed with error : ", error)