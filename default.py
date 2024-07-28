import sys
import xbmcplugin
import xbmcgui
import xbmcaddon
import urllib.request
import urllib.parse
import json
import os
import time

addon = xbmcaddon.Addon()
addonname = addon.getAddonInfo('name')
data_id = "F-C0032-001"  # 資料編號
cache_file = xbmc.translatePath("special://temp/weather_cache.json")
cache_expiry = 3600  # 1 hour

def get_url(**kwargs):
    return sys.argv[0] + '?' + urllib.parse.urlencode(kwargs)

def fetch_weather(api_key, format):
    url = f"https://opendata.cwb.gov.tw/fileapi/v1/opendataapi/{data_id}?Authorization={api_key}&format={format}"
    response = urllib.request.urlopen(url)
    data = response.read().decode()
    if format.lower() == "json":
        return json.loads(data)
    return data

def get_weather(api_key, location, format):
    if os.path.exists(cache_file):
        cache_mtime = os.path.getmtime(cache_file)
        if time.time() - cache_mtime < cache_expiry:
            with open(cache_file, 'r') as f:
                return json.load(f)
    data = fetch_weather(api_key, format)
    with open(cache_file, 'w') as f:
        json.dump(data, f)
    for loc in data['records']['location']:
        if loc['locationName'] == location:
            return loc
    return None

def list_weather():
    xbmcplugin.setPluginCategory(int(sys.argv[1]), 'Weather')
    xbmcplugin.setContent(int(sys.argv[1]), 'videos')
    api_key = addon.getSetting('api_key')
    location = addon.getSetting('location')
    format = addon.getSetting('format')
    if not api_key:
        xbmcgui.Dialog().notification("Error", "API Key is missing", xbmcgui.NOTIFICATION_ERROR, 5000)
        return
    weather_info = get_weather(api_key, location, format)
    if weather_info:
        item = xbmcgui.ListItem(label=location)
        xbmcplugin.addDirectoryItem(int(sys.argv[1]), get_url(action='show', location=location), item, isFolder=False)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

def show_weather(location):
    api_key = addon.getSetting('api_key')
    format = addon.getSetting('format')
    if not api_key:
        xbmcgui.Dialog().notification("Error", "API Key is missing", xbmcgui.NOTIFICATION_ERROR, 5000)
        return
    weather_info = get_weather(api_key, location, format)
    if weather_info:
        for element in weather_info['weatherElement']:
            xbmcgui.Dialog().notification(element['elementName'], element['time'][0]['parameter']['parameterName'], xbmcgui.NOTIFICATION_INFO, 5000)

if __name__ == '__main__':
    params = urllib.parse.parse_qs(sys.argv[2][1:])
    if 'action' in params and params['action'][0] == 'show':
        show_weather(params['location'][0])
    else:
        list_weather()