import pyglet
from pyglet import shapes
from pyglet.window import key
import socket

#import main

xOffset = 200
yOffset = 200
xScale = 0.5
yScale = 0.5

window = pyglet.window.Window(400, 400, resizable=True)
window.set_caption('Egocentric memory')
batch = pyglet.graphics.Batch()
pyglet.gl.glClearColor(1, 1, 1, 1)
window.clear()
pyglet.gl.glTranslatef(xOffset, yOffset, 0.0)
pyglet.gl.glScalef(xScale, yScale, 1.0)
# pyglet.gl.glRotatef(0, 0, 0, 90)


class RobotGroup(pyglet.graphics.Group):
    def __init__(self):
        super().__init__()
        # pyglet.gl.glTranslatef(xOffset, yOffset, 0.0)
        # pyglet.gl.glScalef(xScale, yScale, 1.0)

    def set_state(self):
        pass


robot = RobotGroup()
robotBody = shapes.Rectangle(0, 0, 160, 200, color=(0, 0, 0), batch=batch, group=robot)
robotBody.anchor_position = 80, 100
FLWheel = shapes.Rectangle(0, 0, 30, 80, color=(0, 0, 0), batch=batch, group=robot)
FLWheel.anchor_position = 115, -10
FRWheel = shapes.Rectangle(0, 0, 30, 80, color=(0, 0, 0), batch=batch, group=robot)
FRWheel.anchor_position = -85, -10
RLWheel = shapes.Rectangle(0, 0, 30, 80, color=(0, 0, 0), batch=batch, group=robot)
RLWheel.anchor_position = 115, 90
RRWheel = shapes.Rectangle(0, 0, 30, 80, color=(0, 0, 0), batch=batch, group=robot)
RRWheel.anchor_position = -85, 90
robot = 100


circle = shapes.Circle(0, 0, 10, color=(50, 225, 30), batch=batch)
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
    #vertex_list = batch.add(2, pyglet.gl.GL_POINTS, None,
    #                        ('v2i', (10, 15, 30, 35)),
    #                        ('c3B', (0, 0, 255, 0, 255, 0))
    #                        )
    # robot.unset_state()
    batch.draw()
    # pyglet.graphics.draw(2, pyglet.gl.GL_POINTS, ('v2i', (10, 15, 30, 35)))
    #pyglet.graphics.draw_indexed(4, pyglet.gl.GL_TRIANGLES,
    #[0, 1, 2, 0, 2, 3],
    #('v2i', (100, 100, 150, 100, 150, 150, 100, 150)))
@window.event
def on_resize(width, height):
    global xOffset
    global yOffset
    pyglet.gl.glScalef(1 / xScale, 1 /yScale, 1.0)
    pyglet.gl.glTranslatef(-xOffset, -yOffset, 0.0)
    xOffset = width * 0.5
    yOffset = height * 0.5
    pyglet.gl.glTranslatef(xOffset, yOffset, 0.0)
    pyglet.gl.glScalef(xScale, yScale, 1.0)

    #xOffset = width / 2
    #yOffset = height / 2
    #robotBody.x = xOffset
    #robotBody.y = yOffset

@window.event
def on_key_press(symbol, modifiers):
    key_pressed_string = str(key.symbol_string(symbol)[4])
    print("sending action " + key_pressed_string)
    key_pressed_byte = bytes(key_pressed_string, 'utf-8')
    sock.sendto(key_pressed_byte, (UDP_IP, UDP_PORT))
    try:
        # Wait for outcome
        sock.settimeout(6)
        data, address = sock.recvfrom(1024)  # buffer size is 1024 bytes
        print("received  outcome %s" % data)
    except:
        print("reception timeout")

if __name__ == '__main__':
    UDP_IP = "192.168.4.1"  # AP mode
    # UDP_IP = "192.168.1.17"  # STA mode
    UDP_PORT = 8888
    print("UDP target IP: %s" % UDP_IP)
    print("UDP target port: %s" % UDP_PORT)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
    # Connect to the osoyoo car server
    sock.connect((UDP_IP, UDP_PORT))

    event_logger = pyglet.window.event.WindowEventLogger()
    window.push_handlers(event_logger)
    pyglet.app.run()

