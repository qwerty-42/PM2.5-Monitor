import wx
import requests
import json
from sys import exit
#使用的运行库

keys=['aqi','area','so2','no2','pm10','co','o3','pm2_5','primary_pollutant','quality']
fpmkeys=['so2','no2','pm10','co','o3','pm2_5']
#预先保存的数据字段，方便调用

#主窗口
class Mainframe(wx.Frame):
    def __init__(self, parent):
        self.data=[]#获取数据
        self.cities=[]#城市清单
        wx.Frame.__init__(self, parent, id=wx.ID_ANY, title="PM2.5 Monitor", pos=wx.DefaultPosition,
                          size=wx.Size(800, 500))#父类生成方法
        self.maketoolbar()#实现工具栏

        self.notebook=wx.Notebook(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0)#分页面容器
        self.searchpage=search(self.notebook)#搜索页面
        self.rankpage=rank(self.notebook)#排行页面
        self.listpage=fpmp(self.notebook)#污染物页面

        self.notebook.AddPage(self.searchpage,u"Position Search")
        self.notebook.AddPage(self.rankpage,u"City Rank")
        self.notebook.AddPage(self.listpage,u"Primary pollutant")
        #添加各页面到分页面容器中

        self.Bind(wx.EVT_LISTBOX,self.listoption,self.rankpage.listbox)
        self.Bind(wx.EVT_BUTTON,self.search,self.searchpage.searchbutton)
        self.Bind(wx.EVT_LISTBOX,self.mpoption,self.listpage.listbox)
        #事件监听器，绑定到主窗口中

        Mainsizer = wx.BoxSizer(wx.VERTICAL)
        Mainsizer.Add(self.notebook, 1, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(Mainsizer)
        self.Layout()
        #窗口主体布局
        self.refresh_data()
        #获取数据


    def maketoolbar(self): #生成工具栏
        icon1 = wx.ArtProvider.GetBitmap(wx.ART_GO_DOWN, wx.ART_TOOLBAR, (20, 20))
        icon2 = wx.ArtProvider.GetBitmap(wx.ART_CLOSE, wx.ART_TOOLBAR, (20, 20))
        #自带美术资源，获取图标

        self.toolbar = self.CreateToolBar(wx.TB_HORIZONTAL, wx.ID_ANY)
        self.toolbar.SetToolBitmapSize(wx.DefaultSize)
        self.tools = []
        self.tool_labels = ['Download', 'Exit']#图标功能提示
        self.tool_icons = [icon1, icon2]
        for i in range(len(self.tool_icons)):
            self.tools.append(self.toolbar.AddTool(wx.ID_ANY, self.tool_labels[i], self.tool_icons[i]))
            self.tools[-1].SetShortHelp(self.tool_labels[i])
        self.toolbar.Realize()
        #图标栏实现
        self.toolbar.Bind(wx.EVT_TOOL, self.clicktoolbar)
    def clicktoolbar(self,event): #点击工具栏触发绑定事件
        toolbar = event.GetEventObject()
        id = event.GetId()
        pos = toolbar.GetToolPos(id)
        #获取点击位置
        if pos==0:#数据下载
            self.download_data()
            self.refresh_data()
        elif pos==1:#退出
            exit()
    def listoption(self,event):#排行榜获取
        key=fpmkeys[self.rankpage.listbox.GetSelection()]
        cities={}
        for i in range(len(self.data)):
            if (self.data[i]['area'] not in cities):
                cities[self.data[i]['area']]=self.data[i][key]
            else:
                cities[self.data[i]['area']]+=self.data[i][key]
        scities=sorted(cities.items(),key=lambda item:item[1])#对获取污染数据排序
        s=''#生成静态文本（正排行榜用）
        for i in range(min(10,len(scities))):
            s+=scities[i][0]+'('+str(scities[i][1])+')\n\n'
        self.rankpage.rankstat1.SetLabel(s)
        s=''#生成静态文本（逆排行榜用）
        for i in range(min(10,len(scities))):
            s+=scities[-i-1][0]+'('+str(scities[-i-1][1])+')\n\n'
        self.rankpage.rankstat2.SetLabel(s)

    def mpoption(self,event):#主要污染物获取
        key = fpmkeys[self.listpage.listbox.GetSelection()]
        s=''
        for i in range(len(self.data)):
            if (self.data[i]['primary_pollutant']==key):
                s+=self.data[i]['position_name']+' '
        self.listpage.mp.SetLabel(s)

    def search(self,event):#搜索功能，点击搜索按钮触发
        s=self.searchpage.searchinput.GetValue()#获取搜索框内文本
        if (s in self.poss):
            self.searchpage.searchresult.SetLabel(self.positionstring(s))
        else:
            self.searchpage.searchresult.SetLabel('查无此地')

    def download_data(self):#数据下载

        #print('download PM2.5 data from Internet')
        url='http://www.pm25.in/api/querys/all_cities.json?token=5j1znBVAsnSf5xQyNQyq'
        getr=requests.get(url,headers={'Connection':'close'})#数据下载
        data=getr.json()

        if (not ('error' in data)):#判断错误
            with open("./testdata_all.json", 'w', encoding='utf-8') as json_file:
                json.dump(data, json_file, ensure_ascii=False)
        else:
            wx.MessageBox('API access to all cities denied', 'Sorry!', wx.OK | wx.ICON_INFORMATION)

    def refresh_data(self): #数据更新（从本地）
        print('refresh data')
        self.poss={}
        self.slist='可查询地点：'
        with open('./testdata_all.json', 'r', encoding='utf-8') as json_file:
            self.data = json.load(json_file)
            for i in range(len(self.data)):
                    self.poss[self.data[i]['position_name']]=self.data[i]
                    self.slist+=self.data[i]['position_name']+' '
        self.searchpage.plist.SetLabel(self.slist)

    def quit(self):#退出程序
        print('exit.')

    def positionstring(self,position):#获取某查询点信息汇总成的字符串
        if (position in self.poss):
            t=self.poss[position]
            return ('城市：'+t['area']+'\nso2:'+str(t['so2'])+'\nno2:'+str(t['no2'])+'\nco:'+
                    str(t['co'])+'\no3:'+str(t['o3'])+'\npm10:'+str(t['pm10'])+'\npm2.5:'+str(t['pm2_5'])+'\nquality:'+str(t['quality'])+'\n')
        else:
            return ''

class search(wx.Panel):#搜索分页
    def __init__(self,parent):
        wx.Panel.__init__(self,parent,id=wx.ID_ANY)
        self.searchinput=wx.TextCtrl(self,-1, pos=(80, 25), size=(180, -1))
        self.searchbutton=wx.Button(self,id=wx.ID_ANY,label=u'开始搜索',pos=(300,25),size=(70,-1))
        font1 = wx.Font(14, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        font2 = wx.Font(10,wx.DEFAULT, wx.NORMAL, wx.NORMAL)#字体定义
        self.searchresult=wx.StaticText(self, id=wx.ID_ANY, pos=(90, 120))
        self.plist=wx.StaticText(self, id=wx.ID_ANY, pos=(90, 90))
        self.plist.SetFont(font2)
        self.searchresult.SetFont(font1)



class rank(wx.Panel):#排行分页
    def __init__(self,parent):
        wx.Panel.__init__(self,parent,id=wx.ID_ANY)
        self.listbox=wx.ListBox(self,id=wx.ID_ANY,size=(100,150),pos=(10,10),choices=fpmkeys,style=wx.LB_SINGLE,name='Choose Pollutant')
        self.ranktitle1=wx.StaticText(self,id=wx.ID_ANY,pos=(170,30))
        self.ranktitle2=wx.StaticText(self, id=wx.ID_ANY, pos=(470,30))
        font1 = wx.Font(14, wx.ROMAN, wx.ITALIC, wx.NORMAL)
        font2 = wx.Font(14,wx.DEFAULT,wx.NORMAL,wx.NORMAL)
        self.ranktitle1.SetFont(font1)
        self.ranktitle2.SetFont(font1)
        self.ranktitle1.SetLabel('Cities with least average fpm selected')
        self.ranktitle2.SetLabel('Cities with most average fpm selected')
        self.rankstat1=wx.StaticText(self, id=wx.ID_ANY, pos=(200,70))
        self.rankstat1.SetFont(font2)
        self.rankstat2=wx.StaticText(self, id=wx.ID_ANY, pos=(510,70))
        self.rankstat2.SetFont(font2)

class fpmp(wx.Panel):#主要污染物分页
    def __init__(self,parent):
        wx.Panel.__init__(self,parent,id=wx.ID_ANY)
        self.listbox=wx.ListBox(self,id=wx.ID_ANY,size=(100,150),pos=(10,10),choices=fpmkeys,style=wx.LB_SINGLE,name='Choose Pollutant')
        font1 = wx.Font(14, wx.ROMAN, wx.ITALIC, wx.NORMAL)
        font2 = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        self.mptitle = wx.StaticText(self, id=wx.ID_ANY, pos=(170, 30))
        self.mp = wx.StaticText(self, id=wx.ID_ANY, pos=(200, 70))
        self.mptitle.SetFont(font1)
        self.mp.SetFont(font2)
        self.mptitle.SetLabel('Main Pollutant')


class fpmapp(wx.App):#主循环，未加入其他功能
    def __init__(self,parent):
        wx.App.__init__(self,parent)

if __name__ == '__main__':
    FPMapp=fpmapp(None)
    FPMframe=Mainframe(None)

    FPMframe.Show()

    FPMapp.MainLoop()




