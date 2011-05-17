from OpenGL import GL

def drawMotherShip(agent):
    width = agent.width
    length = agent.length
    color = agent.color
    GL.glPushMatrix()
    x, y = agent.position
    direction = agent.getDirectionDegrees()
    GL.glTranslate(x, y, 0)
    GL.glRotatef(direction, 0, 0, 1)
    GL.glColor3f(*color)
    GL.glBegin(GL.GL_LINE_LOOP)
    halfWidth = width / 2.0
    halfLength = length / 2.0
    sixthWidth = width / 6.0
    
    #Core of the ship
    
    GL.glVertex2f(0, halfWidth)
    GL.glVertex2f(-halfLength, sixthWidth)
    GL.glVertex2f(-halfLength, -sixthWidth)
    GL.glVertex2f(0, -halfWidth)
    GL.glVertex2f(halfLength, -sixthWidth)
    GL.glVertex2f(halfLength, sixthWidth)
    
    GL.glEnd()
    GL.glPopMatrix()

def drawBomber(agent):
    width = agent.width
    length = agent.length
    color = agent.color
    halfWidth = width / 2.0
    halfLength = length / 2.0
    quarterLength = length / 4.0
    GL.glPushMatrix()
    x, y = agent.position
    direction = agent.getDirectionDegrees()
    GL.glTranslate(x, y, 0)
    GL.glRotatef(direction, 0, 0, 1)
    GL.glColor3f(*color)
    GL.glBegin(GL.GL_LINES)
    
    GL.glVertex2f(halfLength,
                  halfWidth)
    GL.glVertex2f(-halfLength,
                  halfWidth)
    GL.glVertex2f(halfLength,
                  -halfWidth)
    GL.glVertex2f(-halfLength,
                  -halfWidth)
    GL.glVertex2f(quarterLength,
                  halfWidth)
    GL.glVertex2f(quarterLength,
                  -halfWidth)
    GL.glVertex2f(-quarterLength,
                  halfWidth)
    GL.glVertex2f(-quarterLength,
                  -halfWidth)
    GL.glVertex2f(quarterLength,
                  0)
    GL.glVertex2f(halfLength,
                  0)
    
    GL.glEnd()
    GL.glPopMatrix()
    
def drawInterceptor(agent):
    width = agent.width
    length = agent.length
    color = agent.color
    threeFifthsLength = (3.0 * length) / 5.0
    twoFifthsLength = (2.0 * length) / 5.0
    halfWidth = width / 2.0
    
    GL.glPushMatrix()
    x, y = agent.position
    direction = agent.getDirectionDegrees()
    GL.glTranslate(x, y, 0)
    GL.glRotatef(direction, 0, 0, 1)
    GL.glColor3f(*color)
    GL.glBegin(GL.GL_LINES)
    
    GL.glVertex2f(0, 0)
    GL.glVertex2f(threeFifthsLength, 0)
    GL.glVertex2f(-twoFifthsLength, halfWidth)
    GL.glVertex2f(twoFifthsLength, halfWidth)
    GL.glVertex2f(-twoFifthsLength, -halfWidth)
    GL.glVertex2f(twoFifthsLength, -halfWidth)
    GL.glVertex2f(0, halfWidth)
    GL.glVertex2f(0, -halfWidth)
    
    GL.glEnd()
    GL.glPopMatrix()
    

def drawFighter(agent):
    width = agent.width
    length = agent.length
    color = agent.color
    GL.glPushMatrix()
    x, y = agent.position
    direction = agent.getDirectionDegrees()
    GL.glTranslate(x, y, 0)
    GL.glRotatef(direction, 0, 0, 1)
    GL.glColor3f(*color)
    GL.glBegin(GL.GL_LINE_LOOP)
    
    halfLength = length / 2.0
    halfWidth = width / 2.0
    
    GL.glVertex2f(halfLength, 0)
    GL.glVertex2f(-halfLength, -halfWidth)
    GL.glVertex2f(-halfLength, halfWidth)
    
    GL.glEnd()
    GL.glPopMatrix()
    
def drawLaserShot(shot):
    color = shot.color
    height = shot.height
    GL.glPushMatrix()
    x, y = shot.getPosition()
    direction = shot.getDirectionDegrees()
    GL.glTranslate(x, y, 0)
    GL.glRotatef(direction, 0, 0, 1)
    GL.glColor3f(*color)
    GL.glBegin(GL.GL_LINES)
    GL.glVertex2f(0, 0)
    GL.glVertex2f(-height, 0)
    GL.glEnd()
    GL.glPopMatrix()
    
def drawSpaceBomb(shot):
    color = shot.color
    height = shot.height
    width = shot.width
    GL.glPushMatrix()
    x, y = shot.getPosition()
    direction = shot.getDirectionDegrees()
    GL.glTranslate(x, y, 0)
    GL.glRotatef(direction, 0, 0, 1)
    GL.glColor3f(*color)
    GL.glBegin(GL.GL_LINES)
    GL.glVertex2f(0, 0)
    GL.glVertex2f(0, height)
    GL.glVertex2f(0, 0)
    GL.glVertex2f(0, -height)
    GL.glVertex2f(0, 0)
    GL.glVertex2f(width, 0)
    GL.glVertex2f(0, 0)
    GL.glVertex2f(-width, 0)
    
    
    GL.glEnd()
    GL.glPopMatrix()
    
def drawJumpPoint(stationary):
    width = stationary.width
    length = stationary.length
    color = stationary.color
    halfWidth = width / 2
    halfLength = length / 2
    GL.glPushMatrix()
    x, y = stationary.getPosition()
    GL.glTranslate(x, y, 0)
    GL.glColor3f(*color)
    GL.glBegin(GL.GL_LINE_LOOP)
    GL.glVertex2f(halfWidth, halfLength)
    GL.glVertex2f(halfWidth, -halfLength)
    GL.glVertex2f(-halfWidth, -halfLength)
    GL.glVertex2f(-halfWidth, halfLength)
    GL.glEnd()
    GL.glPopMatrix()