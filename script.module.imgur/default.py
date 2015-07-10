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
ACTION_SELECT_ITEM = 7

LAYOUT_PADDING = 10
LAYOUT_LEFT_LIST_WIDTH = 630
LAYOUT_LEFT_FIRST_LABEL_ID = 104
LAYOUT_LEFT_LAST_LABEL_ID = 140
LAYOUT_LEFT_SCROLL_TOP_ID = 101
LAYOUT_LEFT_SCROLL_BOTTOM_ID = 144
LAYOUT_RIGHT_LIST_WIDTH = 610
LAYOUT_RIGHT_FIRST_LABEL_ID = 201
LAYOUT_RIGHT_LAST_LABEL_ID = 220

SCROLL_AMOUNT = 120

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
        y = self.setLabelControl(LAYOUT_LEFT_SCROLL_TOP_ID, galleryItem.title, y, font='font14', multiline=False)
        
        line2 = datetime.datetime.fromtimestamp(galleryItem.datetime).strftime('%a, %b %d at %H:%M')
        if galleryItem.account_url is not None:
            line2 = "by " + galleryItem.account_url + " - " + line2
        y = self.setLabelControl(102, line2, y, font='font12', multiline=False)
        
        lblTitleId = LAYOUT_LEFT_FIRST_LABEL_ID
        imgControlId = lblTitleId + 1
        imgOverlayId = imgControlId + 1
        lblDescId = imgOverlayId + 1
        if (galleryItem.is_album):
            y = self.setLabelControl(103, galleryItem.description, y)
            rowItems = 4
            for albumImage in galleryItem.images:
                if lblTitleId > LAYOUT_LEFT_LAST_LABEL_ID:
                    break
                y = self.setLabelControl(lblTitleId, albumImage['title'], y)
                lblTitleId = lblTitleId + rowItems
                
                y = self.setImageControl(imgControlId, albumImage['id'], albumImage['link'], albumImage['width'], albumImage['height'], y)
                self.overlayPlayButton(imgControlId, imgOverlayId, albumImage['animated'])
                imgControlId = imgControlId + rowItems
                imgOverlayId = imgOverlayId + rowItems
                
                y = self.setLabelControl(lblDescId, albumImage['description'], y)
                lblDescId = lblDescId + rowItems
        else:
            y = self.setImageControl(imgControlId, galleryItem.id, galleryItem.link, galleryItem.width, galleryItem.height, y)
            y = self.setLabelControl(lblDescId, galleryItem.description, y)
            self.overlayPlayButton(imgControlId, imgOverlayId, galleryItem.animated)
                
        y = self.setLabelControl(LAYOUT_LEFT_SCROLL_BOTTOM_ID, self.formatNumber(galleryItem.score)+' points, '+self.formatNumber(galleryItem.views)+' views', y)
        
        
    def initRight(self):
        galleryItem = galleryNavigator.item()
        y = LAYOUT_PADDING
        y = self.setLabelControl(200, self.formatNumber(galleryItem.comment_count)+' comments sorted by best', y, padding=LAYOUT_PADDING * 2)
        
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
            self.scroll(SCROLL_AMOUNT)
        if (action == ACTION_PAGE_DOWN or action == ACTION_MOUSE_WHEEL_DOWN or action == ACTION_MOVE_DOWN):
            self.scroll(-SCROLL_AMOUNT)
        if (action == ACTION_MOVE_RIGHT):
            self.next()
        if (action == ACTION_MOVE_LEFT):
            self.previous()
        if (action == ACTION_SELECT_ITEM):
            self.playAll();
        
    def scroll(self, amount):
        for controlId in range(LAYOUT_LEFT_SCROLL_TOP_ID, LAYOUT_LEFT_SCROLL_BOTTOM_ID + 1):
            x = self.getControl(controlId).getX();
            y = self.getControl(controlId).getY();
            if (controlId == LAYOUT_LEFT_SCROLL_TOP_ID and amount > 0 and y == LAYOUT_PADDING):
                return
            if (amount < 0):
                lastControl = self.getControl(LAYOUT_LEFT_SCROLL_BOTTOM_ID)
                if (lastControl.getY() + lastControl.getHeight() + LAYOUT_PADDING <= 720):
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
        height = (estLines + newlines) * (textHeight)
        return height
        
    def setImageControl(self, controlId, imageId, link, width, height, y, maxWidth=LAYOUT_LEFT_LIST_WIDTH):
        imgUrl = self.getImageUrl(imageId, link)
        self.getControl(controlId).setImage(imgUrl)
        x = LAYOUT_PADDING
        if (width > maxWidth):
            heightRatio = float(height) / float(width)
            height = int(heightRatio * float(maxWidth))
            width = maxWidth
        if (width < maxWidth):
            x = x + int(float(maxWidth - width) / float(2))
        self.getControl(controlId).setWidth(width)
        self.getControl(controlId).setHeight(height)
        self.getControl(controlId).setPosition(x, y)
        self.getControl(controlId).setVisible(True)
        xbmc.log('setImageControl controlId='+str(controlId)+', imgUrl='+str(imgUrl)+', x='+str(x)+', y='+str(y)+', width='+str(width)+', height='+str(height), xbmc.LOGDEBUG)
        y = y + height + LAYOUT_PADDING
        return y
    
    def redraw(self):
        for controlId in range(LAYOUT_LEFT_SCROLL_TOP_ID, LAYOUT_LEFT_SCROLL_BOTTOM_ID):
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
    
    def formatNumber(self, number):
        s = '%d' % number
        groups = []
        while s and s[-1].isdigit():
            groups.append(s[-3:])
            s = s[:-3]
        return s + ','.join(reversed(groups))
    
    def playAll(self):
        playIds = galleryNavigator.getPlayIds()
        if len(playIds) == 0:
            return
        playlist = xbmc.PlayList(1)
        playlist.clear()
        for playId in playIds: 
            title = galleryNavigator.item().title + ' - ' + str(1)
            listitem = xbmcgui.ListItem(title, thumbnailImage='http://i.imgur.com/' + playId + 'b.jpg') 
            playlist.add('http://i.imgur.com/' + playId + '.mp4', listitem)
        xbmc.Player().play(playlist)
    
    def getImageUrl(self, imageId, link):
        imageQualityOptions = {"320x320":"m", "640x640":"l", "1024x1024":"h"}
        imageQuality = imageQualityOptions[addon.getSetting('imageQuality')]
        imgUrl = 'http://i.imgur.com/'+imageId + imageQuality+'.'+link[-3:]
        return imgUrl
    
    def overlayPlayButton(self, imageControlId, overlayControlId, animated):
        overlayControl = self.getControl(overlayControlId)
        if (animated):
            imageControl = self.getControl(imageControlId)
            y = imageControl.getY() + (imageControl.getHeight() / 2) - (overlayControl.getHeight() / 2)
            x = (LAYOUT_LEFT_LIST_WIDTH / 2) - (overlayControl.getWidth() / 2)
            overlayControl.setPosition(x, y)
            overlayControl.setVisible(True)
        else:
            overlayControl.setVisible(False)

        
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
