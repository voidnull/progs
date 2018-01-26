import BeautifulSoup
import requests
import os
import eyed3
import eyed3.id3

BASEDIR=os.path.expanduser("~/Music")


class MP3Cleaner:

    def clean(self,filename):
        mp3=eyed3.load(filename)

        for fid in [id3.frames.COMMENT_FID,LYRICS_FID,OBJECT_FID]:
            if mp3.tag.frame_set[fid]:
                del mp3.tag.frame_set[fid]

class StarMusiq:
    def downloadFile(self,url,dir=None):
        filename = url.split('/')[-1]
        filename=filename.replace('-VmusiQ.Com','').replace('-NewTamilHits.Com','')
        print 'Downloading : ',filename
        if dir:
            filename = dir + '/' + filename

        r = requests.get(url, stream=True)
        with open(filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024): 
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)
                    f.flush()
        return filename

    
    def getSongs(self,id):
        r=requests.get('http://www.starmusiq.com/tamil_movie_songs_free_download.asp?MovieId=' + str(id))
        b=BeautifulSoup.BeautifulSoup(r.text)
        songs=b.findAll(lambda(x): x.name=='a' and x.text=='Download')
    
        title=b.title.text
        title=title[0:title.find('&nbsp;')]

        if title==None or len(title)==0:
            title='Unknown Album'
        
        dir=BASEDIR + '/' + title
        if not os.access(dir, os.R_OK):
            os.mkdir(dir)

        print 'Downloading ',len(songs) ,' songs from : ',title
        
        for song in songs:
            url=song['href']
            self.downloadFile(url,dir)
