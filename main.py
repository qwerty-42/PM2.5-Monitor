import wx
import FPMMonitor
def monitor():
    FPMapp=wx.App()
    FPMframe = FPMMonitor.Mainframe(None)
    FPMframe.Show()
    FPMapp.MainLoop()

if __name__ == '__main__':
    monitor()