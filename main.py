import time
import StellarPlayer
import math
import json
import os
import sys
import requests

class rmysplugin(StellarPlayer.IStellarPlayerPlugin):
    def __init__(self,player:StellarPlayer.IStellarPlayer):
        super().__init__(player)
        self.configjson = ''
        self.medias = []
        self.pageindex = 0
        self.pagenumbers = 0
        self.cur_page = ''
        self.max_page = ''
        self.pg = ''
        self.wd = ''
        self.source = []
        self.allmovidesdata = {}
    
    def start(self):
        super().start()
        self.configjson = 'source.json'
        down_url = "https://cdn.jsdelivr.net/gh/Garefield/stellar-rmys@main/source.json"
        r = requests.get(down_url) 
        result = r.status_code
        if result == 200:
            with open(self.configjson,'wb') as f:
                f.write(r.content)
            self.loadSource()
    
    def loadSource(self):
        self.loadSourceFile(self.configjson)
        displaynum = min(len(self.source),20)
        self.medias = []
        for i in range(displaynum):
            self.medias.append(self.source[i])
        self.pageindex = 1
        self.pagenumbers = len(self.source) // 20
        if self.pagenumbers * 20 < len(self.source):
            self.pagenumbers = self.pagenumbers + 1
        self.cur_page = '第' + str(self.pageindex) + '页'
        self.max_page = '共' + str(self.pagenumbers) + '页'   

      
    def loadSourceFile(self,file):
        file = open(file, "rb")
        fileJson = json.loads(file.read())
        print(len(fileJson))
        for item in fileJson:
            newitem = {'title':item['name'],'fullname':item['fullname'],'picture':item['pic_url'],'info':item['detail'],'url':item['magnet']}
            print(newitem)
            self.source.append(newitem)
        file.close()    
    
    def show(self):
        controls = self.makeLayout()
        self.doModal('main',800,700,'',controls)        
    
    def makeLayout(self):
        mediagrid_layout = [
            [
                {
                    'group': [
                        {'type':'image','name':'picture', '@click':'on_grid_click'},
                        {'type':'link','name':'title','textColor':'#ff7f00','fontSize':15,'height':0.15, '@click':'on_grid_click'}
                    ],
                    'dir':'vertical'
                }
            ]
        ]
        controls = [
            {'type':'space','height':5},
            {'type':'grid','name':'mediagrid','itemlayout':mediagrid_layout,'value':self.medias,'separator':True,'itemheight':240,'itemwidth':150},
            {'group':
                [
                    {'type':'space'},
                    {'group':
                        [
                            {'type':'label','name':'cur_page',':value':'cur_page'},
                            {'type':'link','name':'首页','@click':'onClickFirstPage'},
                            {'type':'link','name':'上一页','@click':'onClickFormerPage'},
                            {'type':'link','name':'下一页','@click':'onClickNextPage'},
                            {'type':'link','name':'末页','@click':'onClickLastPage'},
                            {'type':'label','name':'max_page',':value':'max_page'},
                        ]
                        ,'width':0.7
                    },
                    {'type':'space'}
                ]
                ,'height':30
            },
            {'type':'space','height':5}
        ]
        return controls
            
        
    def on_grid_click(self, page, listControl, item, itemControl):
        mediainfo = self.medias[item]
        self.createMediaFrame(mediainfo)
        
    def createMediaFrame(self,mediainfo):
        medianame = mediainfo['title']
        self.allmovidesdata[medianame] = mediainfo['url']
        controls = [
            {'type':'space','height':5},
            {'group':[
                    {'type':'image','name':'mediapicture', 'value':mediainfo['picture'],'width':0.45},
                    {'group':[
                            {'type':'label','name':'medianame','textColor':'#ff7f00','fontSize':15,'value':mediainfo['fullname'],'height':40},
                            {'type':'label','name':'info','textColor':'#005555','value':mediainfo['info'],'height':1.0,'vAlign':'top'}
                        ],
                        'dir':'vertical',
                        'width':0.75
                    }
                ],
                'width':1.0,
                'height':350
            },
            {'group':[
                    {'type':'space','width':20},
                    {'type':'link','name':'下载','width':30,'@click':'onDownClick'}, 
                    {'type':'space','width':15},
                    {'type':'link','name':'播放','width':30,'@click':'onPlayClick'}
                ]
            }
        ]
        result,control = self.doModal(mediainfo['title'],650,400,'',controls)

    def onDownClick(self, pageId, control, *args):
        url = self.allmovidesdata[pageId]
        self.player.download(url)
    
    def onPlayClick(self, pageId, control, *args):
        url = self.allmovidesdata[pageId]
        self.player.play(url)

    def loadPageData(self):
        maxnum = len(self.source)
        if (self.pageindex - 1) * 20 > maxnum:
            return
        self.medias = []
        startnum = (self.pageindex - 1) * 20
        endnum = self.pageindex * 20
        endnum = min(maxnum,endnum)
        print(startnum)
        print(endnum)
        for i in range(startnum,endnum):
            self.medias.append(self.source[i])
        self.cur_page = '第' + str(self.pageindex) + '页'
        self.player.updateControlValue('main','mediagrid',self.medias)
       
    def onClickFirstPage(self, *args):
        self.pageindex = 1
        self.loading()
        self.loadPageData()
        self.loading(True)
        
    def onClickFormerPage(self, *args):
        if self.pageindex == 1:
            return
        self.pageindex = self.pageindex - 1;
        self.loading()
        self.loadPageData()
        self.loading(True)
    
    def onClickNextPage(self, *args):
        if self.pageindex >= self.pagenumbers:
            return
        self.pageindex = self.pageindex + 1
        self.loading()
        self.loadPageData()
        self.loading(True)
        
    def onClickLastPage(self, *args):
        self.pageindex = self.max_page
        self.loading()
        self.loadPageData()
        self.loading(True)
        
    def loading(self, stopLoading = False):
        if hasattr(self.player,'loadingAnimation'):
            self.player.loadingAnimation('main', stop=stopLoading)
        
def newPlugin(player:StellarPlayer.IStellarPlayer,*arg):
    plugin = rmysplugin(player)
    return plugin

def destroyPlugin(plugin:StellarPlayer.IStellarPlayerPlugin):
    plugin.stop()