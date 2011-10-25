import wx.glcanvas
from OpenGL import GL, GLU
import agents, render, fleets


class EscapeCanvas(wx.glcanvas.GLCanvas):
    def __init__(self,
                 parent,
                 worldWidth,
                 worldHeight):
        wx.glcanvas.GLCanvas.__init__(self,
                                      parent,
                                      -1)
        self.frame = parent
        self.init = 0
        self.Bind(wx.EVT_PAINT, self.onPaint)
        self.Bind(wx.EVT_SIZE, self.onSize)
        self.Bind(wx.EVT_TIMER, self.handleTime)
        
        time = 10.0
        self.timer = wx.Timer(self)
        self.timer.Start(time)
        
        self.worldmaxleft = 0
        self.worldmaxright = worldWidth
        self.worldmaxtop = worldHeight
        self.worldmaxbottom = 0
        
        self.worldWidth = worldWidth
        self.worldHeight = worldHeight

        #initialized to actual values in setupView
        self.viewport_left = 0
        self.viewport_bottom = 0
        self.viewport_height = 0
        self.viewport_width = 0
        
        self.timeStep = 1
        self.timeElapsed = time / 1000
        
        self.jumpPoint = None
        self.escapingFleet = None
        self.pursuingFleet = None
        self.shots = []
        self.shotsByTarget = {}
        
        self.initWorld()

    def initWorld(self):
        self.jumpPoint = agents.Stationary(position=(90000, 90000),
                                           length=100,
                                           width=100,
                                           render=render.drawJumpPoint,
                                           color=(1, 1, 1))
        
        self.escapingFleet = fleets.createEscapingFleet(canvas=self)
        self.pursuingFleet = fleets.createPursuingFleet(canvas=self)
        
        self.escapingFleet.setEnemyFleet(self.pursuingFleet)
        self.pursuingFleet.setEnemyFleet(self.escapingFleet)
        
        escapingMotherShip = self.escapingFleet.getMotherShip()
        pursuingMotherShip = self.pursuingFleet.getMotherShip()
        self.escapingFleet.startAllStateMachines()
        self.pursuingFleet.startAllStateMachines()
    
    def getJumpPoint(self):
        return self.jumpPoint
    
    def getAllCanvasElements(self):
        return (self.escapingFleet.getAllShips() + 
                self.pursuingFleet.getAllShips() + 
                self.shots + 
                [self.jumpPoint])
        
    def getAllShips(self):
        return (self.escapingFleet.getAllShips() +
                self.pursuingFleet.getAllShips())
        
    def addShot(self,
                shot):
        self.shots.append(shot)
        target = shot.target
        if not self.shotsByTarget.has_key(target):
            self.shotsByTarget[target] = []
        self.shotsByTarget[target].append(shot)
        
    def removeShot(self,
                   shot):
        self.shots.remove(shot)
        target = shot.target
        self.shotsByTarget[target].remove(shot)
        
    #hooks for pyOpenGL

    def InitGL(self):
        """This function does some of the one time OpenGL initialization we need to perform. 
        """
        GL.glClearColor(0.0,0.0,0.0,0.0); # set clear color to black
        GL.glEnable(GL.GL_TEXTURE_2D)
        self.setupView()

    #methods on this function

    def setupView(self):
        """This function does the actual work to setup the window so we can 
        draw in it.  Most of its task is going to be sizing the Viewport to
        maintain aspect ratio and sizing the World Window to achieve the 
        maximum possible zoom.
        
        """
        
        self.clientsize = self.GetClientSizeTuple()
       
        height = self.worldHeight 
        width = self.worldWidth  
        
        #The ratio of the width to the height in the client-area
        screenratio = float(self.clientsize[0]) / float(self.clientsize[1])
        
        ratio = width / height
        #Should seem familiar, since we did it in class...
        if ratio > screenratio:
        
            self.viewport_left = 0
            self.viewport_bottom = (self.clientsize[1] - (self.clientsize[0] / ratio)) / 2
            self.viewport_width = self.clientsize[0]
            self.viewport_height = self.clientsize[0] / ratio
            
            
        if ratio < screenratio:
        
            self.viewport_left = (self.clientsize[0] - self.clientsize[1] * ratio) / 2
            self.viewport_bottom = 0
            self.viewport_width = self.clientsize[1] * ratio
            self.viewport_height = self.clientsize[1]
        
        self.viewport_right = self.viewport_left + self.viewport_width
        self.viewport_top = self.viewport_bottom + self.viewport_height
        
        #glViewport(0, 0, self.clientsize[0], self.clientsize[1])
        
        GL.glViewport(self.viewport_left, 
                      self.viewport_bottom, 
                      self.viewport_width, 
                      self.viewport_height)
         
        
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GLU.gluOrtho2D(self.worldmaxleft, 
                       self.worldmaxright, 
                       self.worldmaxbottom, 
                       self.worldmaxtop)

    def onPaint(self,event):
        """This function is called when the canvas recieves notice that it needs to repaint its surface. 
        This just makes sure that OpenGL is inited and passes the work off to another function.
        """
        
        dc = wx.PaintDC(self)
        if not self.init:
            self.InitGL()
            self.init = 1
        self.onDraw()
    
    def onDraw(self):
        self.SetCurrent()
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)       
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()

        for element in self.getAllCanvasElements():
            element.draw()
        self.SwapBuffers()
        self.setupView()
    
    def onSize(self,event):
        """ This function is called when a resize event occurs. The primary
        purpose for this is to readjust the viewport appropriately.
        """
        
        self.setupView()
        event.Skip()

    def handleTime(self,
                   event):
        self.timeStep += 1
        for canvasElement in self.getAllCanvasElements():
            if not canvasElement.active:
                continue
            canvasElement.update(timeStep=self.timeStep,
                                 timeElapsed=self.timeElapsed)
        self.onDraw()
        event.Skip()
        
    def getWorldWidth(self):
        return self.worldWidth
    
    def getWorldHeight(self):
        return self.worldHeight
