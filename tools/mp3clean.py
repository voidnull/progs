#!/usr/bin/env python3
import os
import eyed3
import sys
import logging
import traceback
import argparse
logging.getLogger("eyed3").setLevel(logging.ERROR)

def stripStarMusiq(d):        
    if d == None : return None
    idx = len(d)
    for suffix in ['5starmusiq','starmusiq','starmusiq.fun','starmusiq.top','vmusiq','123musiq','musiq','clicktamil','maango','www', 'Feel The Difference','Original CD']:
        pos = d.lower().find(suffix.lower())
        if pos >= 0 :
            idx = min(idx, pos)
    logging.debug('{}:{}'.format(idx, d))
    if idx == -1 : return d
    # find the last --->
    hidx = d.rfind('-',0,idx)
    if hidx == -1:
        hidx = d.rfind('[',0,idx)
    idx = hidx if hidx >= 0 else idx

    if idx == -1 :
        logging.debug('unable to find hypen in {}'.format(d))
        return d
    logging.debug('{} ---> {}'.format(d,d[0:idx].strip()))
    return d[0:idx].strip()
        
        

def processFile(filename):
    modded = False
    if not filename.endswith('.mp3'):
        logging.error('file not an mp3 [{}]'.format(filename))
        return modded

    mp3 = eyed3.load(filename)

    eyed3.id3.genres[197]=u'Tamil'
    eyed3.id3.genres[u'tamil']=197

    eyed3.id3.genres[198]=u'Hindi'
    eyed3.id3.genres[u'hindi']=198


    # go through the tags directly
    for k,frames in mp3.tag.frame_set.items():
        for n in range(0, len(frames)):
            for attr in ['text','url']:
                try:
                    if attr not in dir(frames[n]):
                        continue
                    if attr == 'text':
                        d = frames[n].text
                    else:
                        d = frames[n].url
                    stripd = stripStarMusiq(d)
                    logging.debug('{} - {} - {} - {} - {}'.format(d!=stripd, k, stripd, d, type(frames[n])))
                    if stripd != d:
                        if attr == 'text':
                            frames[n]._text = stripd
                        else:
                            frames[n].url  = stripd
                        modded = True
                except Exception as e:
                    logging.debug(e)
                    #traceback.print_exc();

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
            logging.debug(mp3.tag.genre.name, data)
            modded = True
            mp3.tag.genre.name = data

    if mp3.tag.non_std_genre:
        data = stripStarMusiq(mp3.tag.non_std_genre.name)
        if data != mp3.tag.non_std_genre.name:
            logging.debug(mp3.tag.non_std_genre.name, data)
            modded = True
            mp3.tag.non_std_genre.name = data

    # comments
    for comment in mp3.tag.comments:
        if comment:
            if len(comment.text) != 0:
                comment.text = u''
                modded = True

    if modded:
        logging.debug('saving file')
        mp3.tag.save()

    newfilename = stripStarMusiq(filename)
    if newfilename != filename:
        #rename
        logging.debug('renaming file')
        os.rename(filename, newfilename+".mp3")
        modded=True

    return modded


def processFiles(files):
    count = 0
    for filename in files:
        if os.path.isfile(filename):
            count += 1
            try:
                ret = processFile(filename)
                logging.info('{} :{}: {}'.format(count, '*' if ret else ' ', filename))
            except Exception as e:
                logging.debug(e)
                logging.warning('unable to process : {}'.format(filename))

        elif os.path.isdir(filename):
            for filetuple in os.walk(filename):
                for f in filetuple[2]:
                    if not f.endswith('.mp3') or f.startswith('.') : continue
                    count+=1
                    fname = '{}/{}'.format(filetuple[0],f)
                    try:
                        ret = processFile(fname)
                        logging.info('{} :{}: {}'.format(count, '*' if ret else ' ', fname))
                    except Exception as e:
                        logging.debug(e)
                        logging.warning('unable to process : {}'.format(fname))

###### main function ####

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='MP3 Cleaner')
    parser.add_argument('files', nargs='*', default=None)
    parser.add_argument('-d', '--debug', action=argparse.BooleanOptionalAction, default=False)
    args = parser.parse_args()

    loglevel = logging.INFO
    if args.debug:
        loglevel = logging.DEBUG

    logging.basicConfig(level=loglevel, format="%(levelname)s: %(message)s")
    processFiles(args.files)
