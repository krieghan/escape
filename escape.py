import optparse

from escape import canvas

def run():
    world = canvas.EscapeWorld(height=100000,
                               width=100000)
    escape_canvas = canvas.EscapeCanvas(world=world)
    escape_canvas.start()


if __name__ == "__main__":
    run()

