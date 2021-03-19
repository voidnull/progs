!!!TOOLS!!!
============

Thread Analyzer
===============
	-	Does a GDB backtrace of all threads and analyzes the data
	-	Finds which threads are `active,sleeping,waiting`

USD to INR
===========
	-	Get friendly INR/USD exchange rates from x-rates.com
	-	Gets the last 10 daily rates, sorts them and picks the median

Downloader Dependencies
=======================
	-	Python3 -  `pip3 install selenium requests m3u8`
	-	Brew/Apps : `brew install chromedriver ffmpeg`

Movie Downloader
================
	-	Given an URL of an `m3u8` playlist , downloads the segments, verifies the segments and stitches them to a new `MP4`
	-	By default does `5` parallel downloads
	-	Maintains download state so that it can continue if interrupted
	-	Usage : `moviedownloader.py http://.../index.m3u8`
	
MyFlixer Downloader
===================
	-	Usage: `myflixer.py <myflixer.to movie page url>`
	-	Uses selenium to automate a Chrome based browser to identify the m3u8 and subtitle file
	-	Downloads English subtitles and the movie using `moviedownloader`

