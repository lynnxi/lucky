import wx
import win32gui
class Desktop(wx.Frame):
    def __init__(self):
        super(Desktop,self).__init__(None,-1,'')
        self.AssociateHandle(win32gui.GetDesktopWindow())
        dc = wx.WindowDC(self)
        dc.DrawRectangle( 100, 100, 800, 800 )

app = wx.App(0)
mf = Desktop()
app.MainLoop()