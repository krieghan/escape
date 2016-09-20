import optparse

from game_common import canvas

from escape import world

def run():
    escape_world = world.EscapeWorld(height=100000,
                               width=100000)
    escape_canvas = canvas.Canvas(world=escape_world)
    escape_canvas.start()


if __name__ == "__main__":
    run()

