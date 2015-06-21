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
import xbmc
import xbmcgui
from .client import ImgurClient
from .helpers import error

CLIENT_ID = '716f6289bf2413c'
CLIENT_SECRET = 'fdb0ba64d591f639907bc78ab2a926fedf05ce84'
    
class GalleryNavigator():
    
    _client = None
    _section = None
    _itemId = None
    _galleryItem = None
    _galleryItems = None
    
    def __init__(self):
        self._client = ImgurClient(CLIENT_ID, CLIENT_SECRET)
        
    def init(self, section, itemId=None):
        xbmc.log('GalleryNavigator.init(): itemId='+str(itemId)+' section='+str(section))
        self._itemId = itemId
        self._section = section
        if (itemId is None):
            self._itemId = self.getNextItemId()
        self.loadItem()
        
    def loadItem(self):
        xbmc.log('GalleryNavigator.loadItem(): '+str(self._itemId))
        if (self._itemId is None):
            self._galleryItem = None
            return
        try:
            self._galleryItem = self._client.gallery_item(self._itemId)
            return self._galleryItem
        except error.ImgurClientError as e:
            xbmcgui.Dialog().notification("Unable to fetch gallery item", 'Code ' + str(e.status_code) + ": " + e.error_message, xbmcgui.NOTIFICATION_ERROR)  # @UndefinedVariable
            xbmc.log('Error ' + str(e.status_code) + ': ' + e.error_message, xbmc.LOGERROR)
        except error.ImgurClientRateLimitError as e:
            xbmcgui.Dialog().notification("Rate limit error", 'Code ' + str(e.status_code) + ": " + e.error_message, xbmcgui.NOTIFICATION_ERROR)  # @UndefinedVariable
            xbmc.log('Error ' + str(e.status_code) + ': ' + e.error_message, xbmc.LOGERROR)
            
    def loadGallery(self):
        xbmc.log('GalleryNavigator.loadGallery()')
        try:
            self._galleryItems = self._client.gallery(section=self._section, sort='time', page=0, window='day', show_viral=True)
        except error.ImgurClientError as e:
            xbmcgui.Dialog().notification("Unable to fetch gallery item", 'Code ' + str(e.status_code) + ": " + e.error_message, xbmcgui.NOTIFICATION_ERROR)  # @UndefinedVariable
            xbmc.log('Error ' + str(e.status_code) + ': ' + e.error_message, xbmc.LOGERROR)
        except error.ImgurClientRateLimitError as e:
            xbmcgui.Dialog().notification("Rate limit error", 'Code ' + str(e.status_code) + ": " + e.error_message, xbmcgui.NOTIFICATION_ERROR)  # @UndefinedVariable
            xbmc.log('Error ' + str(e.status_code) + ': ' + e.error_message, xbmc.LOGERROR)
    
    def item(self):
        return self._galleryItem
    
    def next(self):
        xbmc.log('GalleryNavigator.next()')
        self._itemId = self.getNextItemId()
        self.loadItem()
        return self._galleryItem
    
    def previous(self):
        self._itemId = self.getPreviousItemId()
        self.loadItem()
        return self._galleryItem
            
    def getNextItemId(self):
        xbmc.log('GalleryNavigator.getNextItemId()')
        if (self._galleryItems is None):
            self.loadGallery();
        if (self._itemId is None):
            return self._galleryItems[0].id
        found = False
        for item in self._galleryItems:
            if (found == True):
                return item.id
            if (item.id == self._itemId):
                found = True
        return None
            
    def getPreviousItemId(self):
        xbmc.log('GalleryNavigator.getPreviousItemId()')
        if (self._galleryItems is None):
            self.loadGallery();
        previousId = None
        for item in self._galleryItems:
            if (item.id == self._itemId):
                return previousId
            previousId = item.id
        return None
