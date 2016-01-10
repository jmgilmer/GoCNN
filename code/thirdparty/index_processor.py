#!/usr/bin/python
#
# Copyright Hugh Perkins 2015 hughperkins at gmail
#
# This Source Code Form is subject to the terms of the Mozilla Public License, 
# v. 2.0. If a copy of the MPL was not distributed with this file, You can 
# obtain one at http://mozilla.org/MPL/2.0/.

# simply manages downloading the main index.html page, and storing the contents in datastructures...

from __future__ import print_function, unicode_literals, division, absolute_import
from os import path, sys
sys.path.append( path.dirname(path.abspath(__file__)) + '/thirdparty/future/src' )
from builtins import ( bytes, dict, int, list, object, range, str, ascii, chr,
   hex, input, next, oct, open, pow, round, super, filter, map, zip )
from future.standard_library import install_aliases
install_aliases()

import sys, os, time
import urllib
import multiprocessing

sKgsUrl = 'http://u-go.net/gamerecords/'
urls = []
fileInfos = [] # dict of: url, filename, numGames

def downloadPage( url ):
    fp = urllib.urlopen(url)
    data = unicode( fp.read() )
    fp.close()
    return data

def load_index( dataDirectory ):
    global sKgsUrl, urls, fileInfos
    try:
        indexpagefile = open( 'cached_indexpage.html', 'r' )
        indexpagecontents = indexpagefile.read()
        indexpagefile.close()
        print('reading index page from cache')
#        import zip_urls.py
    except:
        #print('no cached_indexpage.py found')
        print('downloading index page...')
        indexpagecontents = downloadPage( sKgsUrl )
        print( indexpagecontents )
        print( type( indexpagecontents ) )
        indexpagefile = open( 'cached_indexpage.~html', 'w')
        indexpagefile.write( indexpagecontents )
        indexpagefile.close()
        os.rename( dataDirectory + 'cached_indexpage.html' )
#    print page
    splitpage = indexpagecontents.split('<a href="')
    urls = []
    for downloadUrlBit in splitpage:
        if downloadUrlBit.startswith( "http://" ):
            downloadUrl = downloadUrlBit.split('">Download')[0]
            if downloadUrl.endswith('.zip'):
                urls.append( downloadUrl )
    for url in urls:
        filename = os.path.basename( url )
        splitFilename = filename.split('-')
        numGamesString = splitFilename[len(splitFilename)-2]
        numGames = int( numGamesString )
        print( filename + ' ' + str( numGames ) )
        fileInfos.append( { 'url': url, 'filename': filename, 'numGames': numGames } )

def get_fileInfos( dataDirectory ):
    global fileInfos
    if len( fileInfos ) == 0:
        load_index( dataDirectory )
    return fileInfos

def get_urls( dataDirectory ):
    global urls
    if len( urls ) == 0:
        load_index( dataDirectory )
    return urls

def go( dataDirectory ):
    global fileInfos
    load_index( dataDirectory )
    for fileinfo in fileInfos:
        print( fileinfo['filename'] + ' ' + str( fileinfo['numGames'] ) )

if __name__ == '__main__':
    sTargetDirectory = 'data'
    if len(sys.argv) == 2:
        sTargetDirectory = sys.argv[1]
    go(sTargetDirectory)

