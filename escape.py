import optparse

import canvas

def run():
    world = canvas.EscapeCanvas(worldHeight=100000,
                                worldWidth=100000)
    world.start()


if __name__ == "__main__":
    run()

