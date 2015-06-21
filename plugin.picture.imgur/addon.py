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
import urllib
import urlparse
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import resources.lib.imgurpython.client as client
import resources.lib.imgurpython.helpers.error as error

baseUrl = sys.argv[0]
addonHandle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])

#TODO Settings
addon = xbmcaddon.Addon()
pageSizeSetting = addon.getSetting("per_page")

client_id = '716f6289bf2413c'
client_secret = 'fdb0ba64d591f639907bc78ab2a926fedf05ce84'
client = client.ImgurClient(client_id, client_secret)

def createUrl(query):
    return baseUrl + '?' + urllib.urlencode(query)

def renderMenu():
    url = createUrl({'mode': 'renderGallery', 'section': 'hot'})
    menuItem1 = xbmcgui.ListItem('Most Viral', iconImage='DefaultFolder.png')
    xbmcplugin.addDirectoryItem(handle=addonHandle, url=url, listitem=menuItem1, isFolder=True)

    url = createUrl({'mode': 'renderGallery', 'section': 'user'})
    menuItem2 = xbmcgui.ListItem('User Submitted', iconImage='DefaultFolder.png')
    xbmcplugin.addDirectoryItem(handle=addonHandle, url=url, listitem=menuItem2, isFolder=True)

    xbmcplugin.endOfDirectory(addonHandle)
    
def renderGallery(section, page):
    try:
        galleryItems = client.gallery(section=section, sort='time', page=page, window='day', show_viral=True)
        for galleryItem in galleryItems:
            url = createUrl({'mode': 'renderGalleryItem', 'section': section, 'itemId': galleryItem.id})
            thumbnail = None
            icon = None
            if galleryItem.is_album:
                thumbnail = 'http://i.imgur.com/' + galleryItem.cover + 'b.jpg'
                icon = 'http://i.imgur.com/' + galleryItem.cover + 's.jpg'
            else:
                thumbnail = 'http://i.imgur.com/' + galleryItem.id + 'b.jpg'
                icon = 'http://i.imgur.com/' + galleryItem.id + 's.jpg'
            
            li = xbmcgui.ListItem(label=galleryItem.title, label2=galleryItem.description, iconImage=icon, thumbnailImage=thumbnail)
            li.setMimeType('image/jpeg')
            xbmcplugin.addDirectoryItem(handle=addonHandle, url=url, listitem=li)
            
    except error.ImgurClientError as e:
        xbmcgui.Dialog().notification("Unable to fetch gallery", 'Code ' + e.status_code + ": " + e.error_message, xbmcgui.NOTIFICATION_ERROR)  # @UndefinedVariable
        xbmc.log('Error ' + e.status_code + ': ' + e.error_message, xbmc.LOGERROR)
    except error.ImgurClientRateLimitError as e:
        xbmcgui.Dialog().notification("Rate limit error", 'Code ' + e.status_code + ": " + e.error_message, xbmcgui.NOTIFICATION_ERROR)  # @UndefinedVariable
        xbmc.log('Error ' + e.status_code + ': ' + e.error_message, xbmc.LOGERROR)
 
    xbmcplugin.endOfDirectory(addonHandle)
    #Change to thumbnail mode
    xbmc.executebuiltin('Container.SetViewMode(500)')


#
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
mode = args.get('mode', None)
if mode is None:
    renderMenu()
elif mode[0] == 'renderGallery':
    section = args['section'][0]
    #TODO Add next page ListItem
    page = 0
    renderGallery(section=section, page=page)
elif mode[0] == 'renderGalleryItem':
    section = args['section'][0]
    itemId = args['itemId'][0]
    query = {'itemId': itemId, 'section': section}
    scriptUrl = 'special://home/addons/script.module.imgur/default.py'
    xbmc.executebuiltin("XBMC.RunScript("+scriptUrl+","+section+","+itemId+")")
    