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
        
        
    def _setProperties(self, title):
        self.SetTitle(title)
        self.SetSize((487,455))
        #self.SetBackgroundColour(wx.Colour(1, 1, 1))
    
    def _doLayout(self):
        self.columnSizer = wx.BoxSizer(wx.VERTICAL)
        
        self.SetSizer(self.columnSizer)
        self.SetAutoLayout(True)

        self.Layout()

        

    def notifyShipStartLife(self,
                            ship):
        shipNameLabel = wx.StaticText(self, -1, ship.name)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(shipNameLabel, 1, wx.ADJUST_MINSIZE, 0)
        self.columnSizer.Add(sizer, 1, wx.ADJUST_MINSIZE, 0)  
        
        self.Layout()
          
    def notifyShipEndLife(self,
                          ship):
        pass
        
        
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
    