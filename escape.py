import wx
import optparse
import canvas


class EscapeFrame(wx.Frame):
    def __init__(self, 
                 childFrames,
                 *args,
                 **kwds):
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        
        self.childFrames = childFrames
        self.canvas = canvas.EscapeCanvas(self,
                                          worldHeight=100000,
                                          worldWidth=100000)
        self._setProperties()
        self._doLayout()
        
    def _setProperties(self):
        self.SetTitle("Escape")
        self.SetSize((487, 455))
        self.SetBackgroundColour(wx.Colour(0, 0, 0))
        self.canvas.SetBackgroundColour(wx.Colour(0, 0, 0))

    def _doLayout(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.canvas, 1, wx.EXPAND, 0)
        self.SetAutoLayout(True)
        self.SetSizer(sizer)
        self.Layout()


class DebugFrame(wx.Frame):
    def __init__(self, title, *args, **kwargs):
        kwargs["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwargs)
        
        self._setProperties(title)
        self._doLayout()
        
        self.rows = {}
        self.freeSizers = []
        self.allSizers = {}
        self.nextSizerIndex = 0
        
        
    def _setProperties(self, title):
        self.SetTitle(title)
        self.SetSize((487,455))
        self.SetBackgroundColour(wx.Colour(0, 0, 0))
        self.SetForegroundColour(wx.Colour(255, 255, 255))
    
    def _doLayout(self):
        self.columnSizer = wx.BoxSizer(wx.VERTICAL)
        shipTypeTitle = wx.StaticText(self, -1, "Ship Type")
        shipNameTitle = wx.StaticText(self, -1, "Ship Name")
        shipHealthTitle = wx.StaticText(self, -1, "Health")
        goalStateTitle = wx.StaticText(self, -1, "Goal State")
        steeringStateTitle = wx.StaticText(self, -1, "Steering State")
        title_row_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.columnSizer.Add(title_row_sizer, 1, wx.EXPAND, 0)
        title_row_sizer.Add(shipTypeTitle, 1, wx.EXPAND, 0)
        title_row_sizer.Add(shipNameTitle, 1, wx.EXPAND, 0)
        title_row_sizer.Add(shipHealthTitle, 1, wx.EXPAND, 0)
        title_row_sizer.Add(goalStateTitle, 1, wx.EXPAND, 0)
        title_row_sizer.Add(steeringStateTitle, 1, wx.EXPAND, 0)
        
        self.SetSizer(self.columnSizer)
        self.SetAutoLayout(True)

        self.Layout()

        

    def notifyShipStartLife(self,
                            ship):
        typeAbbreviations = {'interceptor' : 'T/I',
                             'bomber' : 'T/B',
                             'fighter' : 'T/F'}
        flightGroup = ship.flightGroup
        if flightGroup is None:
            shipTypeString = 'Lt/Cal'
        else:
            shipTypeString = typeAbbreviations[flightGroup.shipType] 
        shipType = wx.StaticText(self, -1, shipTypeString)
        shipName = wx.StaticText(self, -1, ship.name)
        shipHealth = wx.StaticText(self, -1, "%s/%s" % (ship.health, ship.totalHealth))
        goalState = wx.StaticText(self, -1, getattr(ship.goalStateMachine.currentState, '__name__', 'None'))
        steeringState = wx.StaticText(self, -1, getattr(ship.steeringStateMachine.currentState, '__name__', 'None'))
        
        
        if self.freeSizers:
            sizerIndex = min(self.freeSizers)
            self.freeSizers.remove(sizerIndex)
            sizer = self.allSizers[sizerIndex]
        else:
            sizer = wx.BoxSizer(wx.HORIZONTAL)
            self.columnSizer.Add(sizer, 1, wx.EXPAND, 0)
            sizerIndex = self.nextSizerIndex
            self.allSizers[sizerIndex] = sizer  
            self.nextSizerIndex += 1
        
        sizer.Add(shipType, 1, wx.EXPAND, 0)
        sizer.Add(shipName, 1, wx.EXPAND, 0)
        sizer.Add(shipHealth, 1, wx.EXPAND, 0)
        sizer.Add(goalState, 1, wx.EXPAND, 0)
        sizer.Add(steeringState, 1, wx.EXPAND, 0)
        
        self.rows[ship.name] = {'sizerIndex' : sizerIndex,
                                'sizer' : sizer,
                                'shipType' : shipType,
                                'shipName' : shipName,
                                'shipHealth' : shipHealth,
                                'goalState' : goalState,
                                'steeringState' : steeringState}
        self.Layout()
    
    def notifyShipHit(self, 
                      ship):
        shipHealth = self.rows[ship.name]['shipHealth']
        shipHealth.SetLabel("%s/%s" % (ship.health, ship.totalHealth))
    
    def notifyStateChange(self,
                          stateMachine):
        assert stateMachine.owner.active
        if stateMachine.name == 'goal':
            stateLabel = self.rows[stateMachine.owner.name]['goalState']
        elif stateMachine.name == 'steering':
            stateLabel = self.rows[stateMachine.owner.name]['steeringState']
        
        stateLabel.SetLabel(getattr(stateMachine.currentState, '__name__', 'None'))

    
    def notifyShipEndLife(self,
                          ship):
        row_sizer_index = self.rows[ship.name]['sizerIndex']
        row_sizer = self.allSizers[row_sizer_index]
        
        [self.rows[ship.name][attributeName].Destroy() for attributeName in ("shipType",
                                                                             "shipName", 
                                                                             "shipHealth",
                                                                             "goalState",
                                                                             "steeringState")]

        self.Layout()
        self.freeSizers.append(row_sizer_index)
        del self.rows[ship.name]
        assert not ship.active
        print "Deleting %s" % ship.name
        
def run():
    app = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()
    attackerDebugFrame = DebugFrame("Attacker Status",
                                    None,
                                    -1, 
                                    "")
    defenderDebugFrame = DebugFrame("Defender Status",
                                    None,
                                    -1,
                                    "")
    childFrames = {'attackerDebug' : attackerDebugFrame,
                   'defenderDebug' : defenderDebugFrame}
    frame = EscapeFrame(childFrames,
                        None, 
                        -1, 
                        "")
    app.SetTopWindow(frame)
    frame.Show()
    attackerDebugFrame.Show()
    defenderDebugFrame.Show()
    app.MainLoop()


    
if __name__ == "__main__":
    run()
    