#!/usr/bin/env python3
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as conditions
import time
import argparse
import sys
import os
import requests
import logging
import re

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
#print(sys.path)
import moviedownload

class MyflixerMovieInfo:
    def __init__(self):
        options = Options()
        options.binary_location = '/Applications/Brave Browser.app/Contents/MacOS/Brave Browser'
        options.headless = True;
        driver_path = '/usr/local/bin/chromedriver'
        self.driver = webdriver.Chrome(options = options, executable_path = driver_path)
        
    def __del__(self):
        self.driver.close();
        
    def wait_for_tag(self, tagname, timeout = 10):
        element = None
        try:
            element = WebDriverWait(self.driver, timeout).until(
                    conditions.presence_of_element_located((By.TAG_NAME, tagname)))
        except:
            pass
        return element

    def wait_for_id(self, itemid, timeout = 10):
        element = None
        try:
            element = WebDriverWait(self.driver, timeout).until(
                    conditions.presence_of_element_located((By.ID, itemid)))
        except:
            pass
        return element

    def get_movie_info(self, moviepath):
        basename = moviepath[1+moviepath.rfind('/'):]
        moviepath = 'https://myflixer.to/watch-movie/{}'.format(basename)
        try:
            print('Will fetch : {}'.format(moviepath))
            self.driver.get(moviepath)

            for n in range(10):
                time.sleep(1)
                e = self.wait_for_id('iframe-embed')
                if e is not None and e.get_attribute('src').find('vidcloud') >=0 :
                    break;
                print (e)
    
            a=self.driver.find_element_by_css_selector('h2 a[href*="/{}"]'.format(basename))
            title='movie'
            if a:
                title = a.get_property('text')

            vu=self.driver.find_element_by_id('iframe-embed').get_attribute('src')
            print('Will fetch : {}'.format(vu))

            self.driver.get(vu)
            for n in range(10):
                time.sleep(1)
                print(self.driver.current_url)
                e = self.wait_for_tag('video')
                if e is not None:
                    break


            subs = self.driver.execute_script('return tracks')
            src = self.driver.execute_script('return sources')
            vfile = src[0]['file']
            subfile=None

            for s in subs:
                if s['label'].find('English') >= 0:
                    subfile = s['file']
                    break
                    
            if subfile is None:
                print('English sub not found')
                print(subs)
                    
            # check for 1080
            pos = vfile.rfind('/720/index.m3u8')
            if pos >= 0:
                v1080 = vfile[:pos] + '/1080/index.m3u8'
                try:
                    requests.head(v1080, timeout = 5)
                    vfile = v1080
                except:
                    pass

            return  {
                'video' : vfile,
                'subtitle' : subfile,
                'title' : title
            }
        finally:
            pass
            
    def vtt_to_srt(self, vttfile):
        lines = []
        srtname = vttfile[:-4] + '.srt'

        with open(vttfile,'r') as f:
            lines = f.readlines()

        srtfile = open(srtname, 'w')
        timeblock = False
        count = 0

        for line in lines:
            if not timeblock and ' --> ' in line:
                timeblock = True
                count += 1
                srtfile.write('{}\n'.format(count))
            
            line = re.sub(r"(\d\d:\d\d:\d\d).(\d\d\d) --> (\d\d:\d\d:\d\d).(\d\d\d)(?:[ \-\w]+:[\w\%\d:]+)*\n", r"\1,\2 --> \3,\4\n", line)
            line = re.sub(r"(\d\d:\d\d).(\d\d\d) --> (\d\d:\d\d).(\d\d\d)(?:[ \-\w]+:[\w\%\d:]+)*\n", r"00:\1,\2 --> 00:\3,\4\n", line)
            line = re.sub(r"(\d\d).(\d\d\d) --> (\d\d).(\d\d\d)(?:[ \-\w]+:[\w\%\d:]+)*\n", r"00:00:\1,\2 --> 00:00:\3,\4\n", line)
            line = re.sub(r"WEBVTT\n", "", line)
            line = re.sub(r"Kind:[ \-\w]+\n", "", line)
            line = re.sub(r"Language:[ \-\w]+\n", "", line)
            line = re.sub(r"<c[.\w\d]*>", "", line)
            line = re.sub(r"</c>", "", line)
            line = re.sub(r"<\d\d:\d\d:\d\d.\d\d\d>", "", line)
            line = re.sub(r"::[\-\w]+\([\-.\w\d]+\)[ ]*{[.,:;\(\) \-\w\d]+\n }\n", "", line)
            line = re.sub(r"Style:\n##\n", "", line)
        
            if timeblock:
                srtfile.write(line)
    
            if line == '\n':
                timeblock = False
    
        srtfile.write('\n')
        srtfile.close()
        
    def downloadSubtitle(self, name, path):
        print('Downloading subtitles for : {}'.format(name))
        r = requests.get(path)
        fname = name + path[path.rfind('.'):]
        if r.ok:
            with open(fname, 'wb') as f:
                f.write(r.content)
                
        self.vtt_to_srt(fname)
            
    def downloadMovie(self, name, path):
        print('Downloading movie : {}'.format(name))
        args = moviedownload.DummyArgs()
        args.url = path
        
        downloader = moviedownload.M3U8Downloader(args)
        ret = downloader.go()
        if ret:
            os.rename('movie.mp4' , name + '.mp4')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Download movie from Myflixer')
    parser.add_argument('url', nargs='?', default=None)
    parser.add_argument('--sub', action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument('--movie', action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument('-d', '--debug', action=argparse.BooleanOptionalAction, default=False)
    
    # eg path = 'https://myflixer.to/watch-movie/harry-potter-and-the-prisoner-of-azkaban-19594'

    args = parser.parse_args()
    
    loglevel = logging.INFO
    if args.debug:
        loglevel = logging.DEBUG

    logging.basicConfig(level=loglevel, format="%(levelname)s: %(message)s")
    
    if args.url is None:
        print('please specify a movie url !!')
        sys.exit(0)
    
    fetcher = MyflixerMovieInfo()
    data = fetcher.get_movie_info(args.url)
    print('Name  : {}'.format(data['title']))
    print('Subs  : {}'.format(data['subtitle']))
    print('Video : {}'.format(data['video']))
    
    if data['subtitle'] and args.sub:
        fetcher.downloadSubtitle(data['title'], data['subtitle'])
        
    if data['video'] and args.movie:
        fetcher.downloadMovie(data['title'], data['video'])