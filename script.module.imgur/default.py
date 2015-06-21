#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Aw motherfuckin breadcrumbs, oh YISS!
#  _
# (_)_ __ ___   __ _ _   _ _ __ 
# | | '_ ` _ \ / _` | | | | '__|
# | | | | | | | (_| | |_| | |   
# |_|_| |_| |_|\__, |\__,_|_|   
#              |___/  
# 
# Author: Andre Oosthuizen
# Date: 2015-06-14
#
import sys
import math
import datetime
import ImageFont
import xbmc
import xbmcaddon
import xbmcgui
from lib.imgurpython import GalleryNavigator

ACTION_MOVE_LEFT = 1
ACTION_MOVE_RIGHT = 2
ACTION_MOVE_UP = 3
ACTION_MOVE_DOWN = 4
ACTION_PAGE_UP = 5
ACTION_PAGE_DOWN = 6
ACTION_PARENT_DIR = 9
ACTION_PREVIOUS_MENU = 10
ACTION_MOUSE_WHEEL_UP = 104
ACTION_MOUSE_WHEEL_DOWN = 105

LAYOUT_PADDING = 10
LAYOUT_LEFT_LIST_WIDTH = 630
LAYOUT_LEFT_FIRST_LABEL_ID = 104
LAYOUT_LEFT_LAST_LABEL_ID = 130
LAYOUT_RIGHT_LIST_WIDTH = 610
LAYOUT_RIGHT_FIRST_LABEL_ID = 201
LAYOUT_RIGHT_LAST_LABEL_ID = 220

addon = xbmcaddon.Addon(id='script.module.imgur')
galleryNavigator = GalleryNavigator()

def init():
    xbmc.log('init()', xbmc.LOGDEBUG)
    if len(sys.argv) == 3:
        section = sys.argv[1]
        itemId = sys.argv[2]
        galleryNavigator.init(section, itemId)
    else:
        section = 'hot'
        galleryNavigator.init(section)
    
class ImgurViewer(xbmcgui.WindowXML):
    
    def onInit(self):
        xbmcgui.WindowXML.onInit(self)
        self.initLeft()
        self.initRight()
        
    def initLeft(self):
        galleryItem = galleryNavigator.item()
        
        y = LAYOUT_PADDING
        y = self.setLabelControl(101, galleryItem.title, y, font='font14', multiline=False)
        
        line2 = datetime.datetime.fromtimestamp(galleryItem.datetime).strftime('%a, %b %d at %H:%M')
        if galleryItem.account_url is not None:
            line2 = "by " + galleryItem.account_url + " - " + line2
        y = self.setLabelControl(102, line2, y, font='font12', multiline=False)
        
        lblTitleId = LAYOUT_LEFT_FIRST_LABEL_ID
        imgControlId = lblTitleId + 1
        lblDescId = imgControlId + 1
        if (galleryItem.is_album):
            y = self.setLabelControl(103, galleryItem.description, y)
            for albumImage in galleryItem.images:
                if lblDescId > LAYOUT_LEFT_LAST_LABEL_ID:
                    break
                y = self.setLabelControl(lblTitleId, albumImage['title'], y)
                lblTitleId = lblTitleId + 3
                y = self.setImageControl(imgControlId, albumImage['id'], albumImage['link'], albumImage['width'], albumImage['height'], y)
                imgControlId = imgControlId + 3
                y = self.setLabelControl(lblDescId, albumImage['description'], y)
                lblDescId = lblDescId + 3
        else:
            y = self.setImageControl(imgControlId, galleryItem.id, galleryItem.link, galleryItem.width, galleryItem.height, y)
            y = self.setLabelControl(lblDescId, galleryItem.description, y)
    
    def initRight(self):
        galleryItem = galleryNavigator.item()
        y = LAYOUT_PADDING
        y = self.setLabelControl(200, str(galleryItem.comment_count)+' comments sorted by best', y, padding=LAYOUT_PADDING * 2)
        
        #y = y + 5
        
        lblAuthorId = LAYOUT_RIGHT_FIRST_LABEL_ID
        lblCommentId = lblAuthorId + 1
        authorPadding = LAYOUT_PADDING / 2
        commentPadding = LAYOUT_PADDING + authorPadding
        for comment in galleryItem.comment_preview:
            if lblCommentId > LAYOUT_RIGHT_LAST_LABEL_ID:
                break
            authorLine = comment['author'] + ' : ' + str(comment['points']) + ' points'
            y = self.setLabelControl(lblAuthorId, authorLine, y, font='font12', padding=authorPadding, multiline=False)
            lblAuthorId = lblAuthorId + 2
            y = self.setLabelControl(lblCommentId, comment['comment'], y, padding=commentPadding)
            lblCommentId = lblCommentId + 2
        
    def onAction(self, action):
        if action == ACTION_PREVIOUS_MENU:
            self.close()
        if action == ACTION_PARENT_DIR:
            self.removeControl(self.strAction)
        if (action == ACTION_PAGE_UP or action == ACTION_MOUSE_WHEEL_UP or action == ACTION_MOVE_UP):
            self.scroll(50)
        if (action == ACTION_PAGE_DOWN or action == ACTION_MOUSE_WHEEL_DOWN or action == ACTION_MOVE_DOWN):
            self.scroll(-50)
        if (action == ACTION_MOVE_RIGHT):
            self.next()
        if (action == ACTION_MOVE_LEFT):
            self.previous()
            
    def scroll(self, amount):
        for controlId in range(101, LAYOUT_LEFT_LAST_LABEL_ID):
            x = self.getControl(controlId).getX();
            y = self.getControl(controlId).getY();
            if (controlId == 101 and amount > 0 and y == LAYOUT_PADDING):
                return
            self.getControl(controlId).setPosition(x, y + amount);
        
    def setLabelControl(self, controlId, label, y, font='font13', padding=LAYOUT_PADDING, multiline=True):
        if (label is not None):
            x = self.getControl(controlId).getX()
            width = self.getControl(controlId).getWidth()
            self.getControl(controlId).setLabel(label.encode('utf-8'))
            self.getControl(controlId).setPosition(x, y)
            self.getControl(controlId).setVisible(True)
            height = self.calculateLabelHeight(label, width, font, multiline)
            xbmc.log('setLabelControl controlId='+str(controlId)+', label='+label.encode('utf-8')+', x='+str(x)+', y='+str(y)+', height='+str(height)+', padding='+str(padding), xbmc.LOGDEBUG)
            y = y + height + padding
        else:
            xbmc.log('setLabelControl controlId='+str(controlId)+', visible=FALSE', xbmc.LOGDEBUG)
            self.getControl(controlId).setVisible(False)
        return y
    
    def calculateLabelHeight(self, text, width, font, multiline):
        fontSize = 20
        if (font == 'font12'):
            fontSize = 17
        if (font == 'font13'):
            fontSize = 20
        if (font == 'font14'):
            fontSize = 22
        fontPath = xbmc.translatePath(addon.getAddonInfo('path')+'/resources/skins/Default/fonts/Roboto-Regular.ttf')
        font = ImageFont.truetype (fontPath, fontSize)
        extent = font.getsize(text.encode('utf-8'))
        textWidth = extent[0]
        textHeight = extent[1] + 1
        newlines = text.count('\n')
        if ((textWidth < width and newlines == 0) or (multiline == False)):
            return textHeight
        estLines = int(math.ceil(textWidth / float(width)))
        #estLines = int(math.ceil(len(text) / float(68)))
        height = (estLines + newlines) * (textHeight)
        return height
        
    def setImageControl(self, controlId, imageId, link, width, height, y, maxWidth=LAYOUT_LEFT_LIST_WIDTH):
        imgUrl = 'http://i.imgur.com/'+imageId+'h.'+link[-3:]
        self.getControl(controlId).setImage(imgUrl)
        x = LAYOUT_PADDING
        if (width > maxWidth):
            height = int(float(height) / float(width) * float(maxWidth))
            width = maxWidth
        else:
            x = x + int(float(maxWidth - width) / float(2))
        self.getControl(controlId).setWidth(width)
        self.getControl(controlId).setHeight(height)
        self.getControl(controlId).setPosition(x, y)
        self.getControl(controlId).setVisible(True)
        xbmc.log('setImageControl controlId='+str(controlId)+', imgUrl='+str(imgUrl)+', x='+str(x)+', y='+str(y)+', width='+str(width)+', height='+str(height), xbmc.LOGDEBUG)
        y = y + height + LAYOUT_PADDING
        return y
    
    def redraw(self):
        for controlId in range(101, LAYOUT_LEFT_LAST_LABEL_ID):
            self.getControl(controlId).setVisible(False)
        for controlId in range(LAYOUT_RIGHT_FIRST_LABEL_ID, LAYOUT_RIGHT_LAST_LABEL_ID):
            self.getControl(controlId).setVisible(False)
        self.onInit()
        
    def next(self):
        xbmc.executebuiltin('ActivateWindow(busydialog)')
        galleryItem = galleryNavigator.next()
        if (galleryItem is not None):
            self.redraw()
        else:
            self.close()
        xbmc.executebuiltin('Dialog.Close(busydialog)')
        
    def previous(self):
        xbmc.executebuiltin('ActivateWindow(busydialog)')
        galleryItem = galleryNavigator.previous()
        if (galleryItem is not None):
            self.redraw()
        else:
            self.close()
        xbmc.executebuiltin('Dialog.Close(busydialog)')
    
    
    
#  Banana for scale
#  _
# //\
# V  \
# \  \_
#   \,'.`-.
#    |\ `. `.       
#    ( \  `. `-.                        _,.-:\
#     \ \   `.  `-._             __..--' ,-';/
#      \ `.   `-.   `-..___..---'   _.--' ,'/
#       `. `.    `-._        __..--'    ,' /
#         `. `-_     ``--..''       _.-' ,'
#           `-_ `-.___        __,--'   ,'
#              `-.__  `----"""    __.-'
#                   `--..____..--'
#

xbmc.executebuiltin('ActivateWindow(busydialog)')
init()
addonPath = xbmc.translatePath(addon.getAddonInfo('path'))
imgurViewer = ImgurViewer('scriptImgurViewer.xml', addonPath)
xbmc.executebuiltin('Dialog.Close(busydialog)')
imgurViewer.doModal()
del imgurViewer
