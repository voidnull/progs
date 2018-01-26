#!/usr/bin/env python
import os
import eyed3
import sys
import logging
logging.getLogger("eyed3").setLevel(logging.ERROR)

def stripStarMusiq(data):
    if data == None : return None
    for item in ['5starmusiq','starmusiq','vmusiq','123musiq','musiq','clicktamil']:
        idx = data.lower().find(item)
        if idx >= 0: break

    if idx == -1 : return data

    # find the last -
    hidx = data.rfind('-',0,idx)
    if hidx == -1:
        hidx = data.rfind('[',0,idx)
    idx = hidx if hidx >= 0 else idx
    
    if idx == -1 :
        print 'unable to find hypen in', data
        return data

    return data[0:idx].strip()

def processFile(filename):
    modded = False
    if not filename.endswith('.mp3'):
        print 'file not an mp3 [{}]'.format(filename)
        return modded

    mp3 = eyed3.load(filename)

    eyed3.id3.genres[197]=u'Tamil'
    eyed3.id3.genres[u'tamil']=197

    eyed3.id3.genres[198]=u'Hindi'
    eyed3.id3.genres[u'hindi']=198


    # go through the tags directly
    for k,frames in mp3.tag.frame_set.iteritems():
        for n in range(0, len(frames)):
            try:
                d = frames[n].__getattribute__('text')
                stripd = stripStarMusiq(d)
                #print d!=stripd, k, stripd, d
                if stripd != d:
                    frames[n].text = stripd
                    modded = True
            except Exception, e:
                #print e
                pass

    data = stripStarMusiq(mp3.tag.title)
    if data != mp3.tag.title:
        modded = True
        mp3.tag.title = data

    data = stripStarMusiq(mp3.tag.album)
    if data != mp3.tag.album:
        modded = True
        mp3.tag.album = data

    data = stripStarMusiq(mp3.tag.artist)
    if data != mp3.tag.artist:
        modded = True
        mp3.tag.artist = data

    data = stripStarMusiq(mp3.tag.album_artist)
    if data != mp3.tag.album_artist:
        modded = True
        mp3.tag.album_artist = data

    if mp3.tag.genre:
        data = stripStarMusiq(mp3.tag.genre.name)
        if data != mp3.tag.genre.name:
            #print mp3.tag.genre.name, data
            modded = True
            mp3.tag.genre.name = data

    if mp3.tag.non_std_genre:
        data = stripStarMusiq(mp3.tag.non_std_genre.name)
        if data != mp3.tag.non_std_genre.name:
            #print mp3.tag.non_std_genre.name, data
            modded = True
            mp3.tag.non_std_genre.name = data

    # comments
    for comment in mp3.tag.comments:
        if comment:
            if len(comment.text) != 0:
                comment.text = u''
                modded = True

    if modded:
        mp3.tag.save()

    newdata = stripStarMusiq(filename)
    if newdata != filename:
        #rename
        os.rename(filename, newdata+".mp3")
        modded=True

    return modded


def processFiles(files):
    count = 0
    for filename in files:
        if os.path.isfile(filename):
            count += 1
            try:
                ret = processFile(filename)
                print '{} : {} : {}'.format(count, ret, filename)
            except:
                print 'unable to process : {}'.format(filename)

        elif os.path.isdir(filename):
            for filetuple in os.walk(filename):
                for f in filetuple[2]:
                    if not f.endswith('.mp3') or f.startswith('.') : continue
                    count+=1
                    fname = '{}/{}'.format(filetuple[0],f)
                    try:
                        ret = processFile(fname)
                        print '{} : {} : {}'.format(count, ret, fname)
                    except:
                        print 'unable to process : {}'.format(fname)

###### main function ####

#print sys.argv
processFiles(sys.argv[1:])
