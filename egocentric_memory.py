import pyglet
from pyglet.gl import *
from pyglet import shapes
from pyglet.window import key
import socket
import json


window_center_x = 0
window_center_y = 0
window_scale_x = 0.5
window_scale_y = 0.5

window = pyglet.window.Window(400, 400, "Egocentric memory", resizable=True)
batch = pyglet.graphics.Batch()
pyglet.gl.glClearColor(1, 1, 1, 1)
# pyglet.gl.glTranslatef(window_center_x, window_center_y, 0.0)
# pyglet.gl.glScalef(window_scale_x, window_scale_y, 1.0)
# pyglet.gl.glRotatef(0, 0, 0, 90)


class RobotGroup(pyglet.graphics.Group):
    def __init__(self):
        super().__init__()


robot = RobotGroup()
robotBody = shapes.Rectangle(0, 0, 160, 200, color=(0, 0, 0), batch=batch, group=robot)
robotBody.anchor_position = 80, 100
FLWheel = shapes.Rectangle(0, 0, 36, 80, color=(0, 0, 0), batch=batch, group=robot)
FLWheel.anchor_position = 120, -10
FRWheel = shapes.Rectangle(0, 0, 36, 80, color=(0, 0, 0), batch=batch, group=robot)
FRWheel.anchor_position = -85, -10
RLWheel = shapes.Rectangle(0, 0, 36, 80, color=(0, 0, 0), batch=batch, group=robot)
RLWheel.anchor_position = 120, 90
RRWheel = shapes.Rectangle(0, 0, 36, 80, color=(0, 0, 0), batch=batch, group=robot)
RRWheel.anchor_position = -85, 90
robotHead = shapes.Rectangle(0, 80, 50, 20, color=(150, 150, 150), batch=batch, group=robot)
robotHead.anchor_position = 25, 0

head_angle = 0

# circle = shapes.Circle(0, 0, 10, color=(50, 225, 30), batch=batch)
# square = shapes.Rectangle(200, 200, 200, 200, color=(55, 55, 255), batch=batch)
# robotBody = shapes.Rectangle(0, 0, 160, 200, color=(255, 22, 20), batch=batch)
# rectangle.opacity = 128
# rectangle.rotation = 33
# line = shapes.Line(100, 100, 100, 200, width=19, batch=batch)
# line2 = shapes.Line(150, 150, 444, 111, width=4, color=(200, 20, 20), batch=batch)
# star = shapes.Star(800, 400, 60, 40, num_spikes=20, color=(255, 255, 0), batch=batch)


@window.event
def on_draw():
    window.clear()
    #glClear(GL_COLOR_BUFFER_BIT)
    #glViewport(0, 0, 400, 400)
    #glLoadIdentity()
    robotHead.rotation = -head_angle
    batch.draw()


@window.event
def on_resize(width, height):
    glViewport(0, 0, width, height)
    #glMatrixMode(gl.GL_PROJECTION)
    #glLoadIdentity()
    #glOrtho(0, width, 0, height, -1, 1)
    #glMatrixMode(gl.GL_MODELVIEW)
    pass

    # # keep the robot at the center of the window
    # global window_center_x
    # global window_center_y
    # pyglet.gl.glScalef(1 / window_scale_x, 1 / window_scale_y, 1.0)
    # pyglet.gl.glTranslatef(-window_center_x, -window_center_y, 0.0)
    # window_center_x = width * 0.5
    # window_center_y = height * 0.5
    # pyglet.gl.glTranslatef(window_center_x, window_center_y, 0.0)
    # pyglet.gl.glScalef(window_scale_x, window_scale_y, 1.0)


@window.event
def on_key_press(symbol, modifiers):
    global head_angle
    key_byte = b'0'
    if symbol == key.NUM_1:
        key_byte = b'1'
    if symbol == key.NUM_2:
        key_byte = b'2'
    if symbol == key.NUM_3:
        key_byte = b'3'
    if symbol == key.NUM_4:
        key_byte = b'4'
    if symbol == key.NUM_5:
        key_byte = b'5'
    if symbol == key.NUM_6:
        key_byte = b'6'
    if symbol == key.NUM_7:
        key_byte = b'7'
    if symbol == key.NUM_8:
        key_byte = b'8'
    if symbol == key.NUM_9:
        key_byte = b'9'
    if symbol == key.NUM_MULTIPLY:
        key_byte = b'*'
    if symbol == key.NUM_DIVIDE:
        key_byte = b'/'
    if symbol == key.NUM_SUBTRACT:
        key_byte = b'-'

    print("Sending action ", end='')
    print(key_byte)
    sock.sendto(key_byte, (UDP_IP, UDP_PORT))
    try:
        outcome_string, address = sock.recvfrom(1024)  # buffer size is 1024 bytes
        print("received  outcome %s" % outcome_string)
    except:
        print("reception timeout")
    outcome = json.loads(outcome_string)
    head_angle = outcome['head_angle']
    print("Head angle %i" % head_angle)


@window.event
def on_mouse_press(x, y, button, modifiers):
    # Get the color at the window's position
    # https://stackoverflow.com/questions/367684/get-data-from-opengl-glreadpixelsusing-pyglet
    a = (pyglet.gl.GLuint * 1)(0)
    pyglet.gl.glReadPixels(x, y, 1, 1, pyglet.gl.GL_RGB, pyglet.gl.GL_UNSIGNED_INT, a)
    print(a[0])


if __name__ == '__main__':
    # UDP_IP = "192.168.4.1"  # AP mode
    # UDP_IP = "192.168.1.17"  # STA mode
    UDP_IP = "192.168.1.19"  # STA mode sur Olivier's wifi
    UDP_PORT = 8888
    print("UDP target IP: %s" % UDP_IP)
    print("UDP target port: %s" % UDP_PORT)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
    # Connect to the osoyoo car server
    sock.connect((UDP_IP, UDP_PORT))
    sock.settimeout(6)

    # event_logger = pyglet.window.event.WindowEventLogger()
    # window.push_handlers(event_logger)
    pyglet.app.run()

