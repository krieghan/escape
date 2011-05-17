import wx
import optparse
import canvas


class EscapeFrame(wx.Frame):
    def __init__(self, 
                 *args,
                 **kwds):
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        
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
    def __init__(self, *args, **kwargs):
        kwargs["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwargs)
        
        self._setProperties()
        
    def _setProperties(self):
        self.SetTitle("Ship Status")
        self.SetSize((487,455))
        self.SetBackgroundColour(wx.Colour(0, 0, 0))
        
    def _doLayout(self):
        self.SetAutoLayout(True)
        self.Layout()
        
        
def run():
    app = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()
    frame = EscapeFrame(None, 
                        -1, 
                        "")
    debugFrame = DebugFrame(None,
                            -1, 
                            "")
    app.SetTopWindow(frame)
    frame.Show()
    debugFrame.Show()
    app.MainLoop()


    
if __name__ == "__main__":
    run()
    