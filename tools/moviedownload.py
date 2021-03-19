#!/usr/bin/env python3
import m3u8
import argparse
import requests
import traceback
import time
import os
import sys
import subprocess
import threading
import concurrent.futures
import zlib
import pickle

class State:
    def __init__(self):
        self.filename = '.dls' # download state
        self.data = {}
        try:
            self.data= pickle.load(open(self.filename,'rb'))
        except:
            pass

    def get(self, key):
        return self.data.get(key, None)

    def put(self, key, value):
        self.data[key] = value
        pickle.dump(self.data, open(self.filename,'wb'))

    def remove(self, key):
        if key in self.data:
            del self.data[key] 
            pickle.dump(self.data, open(self.filename,'wb'))
            return True
        return False

def simplefilehash(f):
    return '{}:{}'.format(zlib.crc32(open(f,'rb').read()), zlib.crc32(str.encode(f)))

class M3U8Downloader:
    def __init__(self, args):
        self.options = args 
        self.playlist = m3u8.load(self.options.url)
        print('Files: {}, Segments: {}'.format(len(self.playlist.files), len(self.playlist.segments)))
        print('Duration : {}'.format(self.strTime(self.getTotalTime())))
        self.name = 'movie'
        self.error = None
        self.failedcount = 0
        self.state = State()
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=self.options.concurrency)
        
    def getTSFileName(self):
        return '{}.ts'.format(self.name)
        
    def getMovieFileName(self):
        return '{}.mp4'.format(self.name)
        
    def getTotalTime(self):
        return sum([s.duration for s in self.playlist.segments])
        
    def strTime(self, seconds):
        seconds = int(seconds)
        h=int(seconds/3600)
        m=int((seconds-(h*3600))/60)
        s=seconds - h*3600 - m*60
        return '{}.{:02}.{:02}'.format(h,m,s)
        
    def go(self):
        st = time.asctime()
        t = 0
            
        if self.playlist.base_uri == '':
            print('local file .. not downloading')
        else:
            self.download()

        if not self.validate() :
            print('Validation failes - Not Stitching/Converting')
            return False
        
        self.stitch()
        self.convert()
        et = time.asctime()
        
        print('start: {}'.format(st))
        print('  end: {}'.format(et))
        
        # remove all ts files
        for f in self.playlist.files:
            os.remove(f)
            
        os.remove(self.getTSFileName())
        os.system('stty sane')
        return True
        
    def verifyTS(self, f):
        # check cache
        cachekey = '{}:verified'.format(simplefilehash(f))
        if self.state.get(cachekey) == True:
            # already verified
            return True
        tempfile = 'null-{}.ts'.format(threading.get_ident())
        out=subprocess.run(['ffmpeg', '-y', '-i', f, '-v', 'error', tempfile], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        success = (out.stderr.find(str.encode('error')) == -1)
        self.state.put(cachekey, success)
        os.remove(tempfile)
        return success
        
    def validate(self):
        if self.options.debug:
            t = 0
            for seg in self.playlist.segments:
                f = seg.get_path_from_uri()
                t += seg.duration
                print('{} : {} '.format(self.strTime(t), f))
            
        success = True
        n = 0
        totalFiles = len(self.playlist.files)
        
        if self.failedcount > 0 :
            print('failed: {} , last error: {}'.format(self.failedcount, self.error))
            success = False
        
        for f in self.playlist.files:
            n += 1
            print('\r Validating File [{} of {}] ({:.2f}%) : {} '.format( n, totalFiles, n*100/totalFiles, f), end='');
            if not os.path.isfile(f):
                print('unable to locate file:' + f, flush=True)
                success = False
            else:
                if self.options.validation and not self.verifyTS(f):
                    print('verification failed : ' + f, flush=True)
                    success = False
        return success
        
    def stitch(self):
        print();
        totalFiles = len(self.playlist.files)
        with open(self.getTSFileName() , 'wb') as tsfile:
            st = time.time()
            n = 0
            for f in self.playlist.files:
                et = time.time()
                n += 1
                print('\r{}'.format(' '*80), end='')
                print('\r[{}] : Stitching File [{} of {}] ({:.2f}%) : {} '.format(self.strTime(et-st), n, totalFiles, (n-1)*100/totalFiles, f), end='');
                if not os.path.isfile(f):
                    raise Exception('Unable to find file : ' + f)
                tsfile.write(open(f, 'rb').read())
        print('File Stitching Complete')

    def convert(self):
        cmd = 'ffmpeg -y -i {} -acodec copy -vcodec copy {}'.format(self.getTSFileName(), self.getMovieFileName())
        print('converting to {}'.format(self.getMovieFileName()))
        os.system(cmd)
        
    def download(self):
        print();
        totalFiles = len(self.playlist.files)
        st = time.time()
        future = {self.executor.submit(self.downloadSegment, n): n for n in range(totalFiles)}

        for f in concurrent.futures.as_completed(future):
            n = future[f]
            try:
                data = f.result()
            except Exception as e:
                traceback.print_exc(file=sys.stdout)
                print('{} generated an exception: {}'.format(self.playlist.files[n], e))
        et = time.time()    
        print('\nDownload Complete :-  {} '.format(self.strTime(et-st)))
        self.executor.shutdown()

    def downloadSegment(self, n):
        f = self.playlist.files[n]
        totalFiles = len(self.playlist.files)
        st = time.time()
                
        if not os.path.isfile(f):
            r = requests.get(self.playlist.base_uri + f)
            if r.ok:
                open(f, 'wb').write(r.content)
                if not self.verifyTS(f):
                    os.remove(f)
                    self.error = 'unable to verify [{}]'.format(f)
                    self.failedcount += 1
            else:
                self.error = 'unable to fetch [{}] : [{}:{}]'.format(f, r.status_code, r.reason)
                self.failedcount += 1
        et = time.time()
        print('[{}] : File [{} of {}] ({:.2f}%) : {} '.format(self.strTime(et-st), n, totalFiles, n*100/totalFiles, f), flush=True)
        return int(et-st)

class DummyArgs:
    def __init__(self):
        self.url = None
        self.concurrency = 5
        self.debug = False
        self.validation = True

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Download movie from m3u8')
    parser.add_argument('url', nargs='?', default=None)
    parser.add_argument('--concurrency','-c', type=int, default=5)
    parser.add_argument('--debug', action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument('--validation', action=argparse.BooleanOptionalAction, default=True)

    args = parser.parse_args()
    #print(args)
    if args.url is None:
        print('please specify an m3u8 file !!')
        sys.exit(0)

    downloader = M3U8Downloader(args)
    downloader.go()