import youtube_dl
from apiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
import requests
import re
from google_images_download import google_images_download  
import cv2
import os
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw 
import debug
import subprocess
import sys
import glob
# creating object 
frameRate = int(sys.argv[1])
response = google_images_download.googleimagesdownload()
urls = open("urls.txt","r").read()
urls = urls.split("\n")
cacheIndex = -1
DEVELOPER_KEY = "AIzaSyAW2lp5N25YckKfhawMukjzzGntTq4BMEQ"
subs = []
lengthVideos = []
timeStamps = []
Subtitles = []
cacheIndex = 0
mainList = []
Songs = []
fontsize = int(sys.argv[2])
def loadimages(folder,extenstion):
    images = []
    for name in glob.glob(str(folder)+'/*'+str(extenstion)):
        images.append(name)

    return images

Images = loadimages("Images",".jpg")
def downloadMp3(urls,dev_key):

	for i in range(len(urls)):
		ydl_opts = {'outtmpl': 'songs/'+str(i)+"."'mp3',"writesubtitles": True, "writeautomaticsub": True,'format': 'bestaudio/best','postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '320',}],}
		with youtube_dl.YoutubeDL(ydl_opts) as ydl:
			ydl.download([urls[i]])

			res = ydl.extract_info(urls[i])
			lengthVideos.append(res['duration'])

			subs.append(res['requested_subtitles']['en']['url'])

def downloadSubs(subs):

	for i in range(len(subs)):
		


		url = subs[i]
		r = requests.get(url, allow_redirects=True)

		open("subs/"+str(i), 'wb').write(r.content)



def cleanSubs(subs):
	
	mainArr = []
	for i in range(len(subs)):
		f = open("subs/"+str(i),"r").read()
		f = f.split("\n")
		f = f[4:len(f)-1]
		
		text = []
		arr = []
		for j in range(len(f)):

			if(f[j]==""):
				text.append(arr)
				arr = []
			else:
				arr.append(f[j])
		mainArr.append(text)
	for i in range(len(mainArr)):
		subtitles = []
		timestamps = []
		for j in range(len(mainArr[i])):
			startend = mainArr[i][j][0].split("-->")

			startend = [startend[0],startend[1].split(" ")[1]]
			
			timestamps.append(startend)
			mainArr[i][j] = mainArr[i][j][1:]
			for k in range(len(mainArr[i][j])):
				mainArr[i][j][k] = re.sub(r"♪", "", mainArr[i][j][k])

			subtitles.append(mainArr[i][j])
		timeStamps.append(timestamps)
		Subtitles.append(subtitles)

	# for i in range(len(timeStamps)):
	# 	for j in range(len(timeStamps[i])):
	# 		print(timeStamps[i][j])
	# 		print(Subtitles[i][j])
	# 		print(" ")
	# 	print(" ")
def addTextPIL(image,sub):
	pixelsize = fontsize*(96/72)
	img = Image.open(image)
	width, height = img.size
	font_fname = 'Helvetica 400.ttf'
	
	font = ImageFont.truetype(font_fname, fontsize)

	bg_colour = (255, 255, 255)
	width = 20
	height = int(height/2)-int(height/6)


	draw = ImageDraw.Draw(img)
	for i in range(len(sub)):
		draw.text((width,height), sub[i], font=font, fill='rgb(255, 255, 255)')
		height+=150


	global cacheIndex
	cacheIndex +=1
	img.save("cache/"+str(cacheIndex)+".jpg")
	return "cache/"+str(cacheIndex)+".jpg"
def addText(image,sub):

	pixelsize = fontsize*(96/72)
	img = Image.open(image)
	width, height = img.size
	img = cv2.imread(image)
	
	width = 20
	height = int(height/2)-int(height/6)


	font                   = cv2.FONT_HERSHEY_SIMPLEX
	bottomLeftCornerOfText = (width,height)
	fontScale              = 3
	fontColor              = (255,255,255)
	lineType               = 4
	for i in range(len(sub)):
		cv2.putText(img,sub[i], bottomLeftCornerOfText, font, int(fontScale),fontColor,int(lineType))
		bottomLeftCornerOfText = (width,height+150)


	global cacheIndex
	cacheIndex +=1
	cv2.imwrite("cache/"+str(cacheIndex)+".jpg", img)

	cv2.waitKey(0)
	return "cache/"+str(cacheIndex)+".jpg"

def createLyrics(Images,timeStamps,Subtitles,frameRate):
	
	for i in range(len(timeStamps)):
		timestamps = timeStamps[i]
		subtitles = Subtitles[i]

		images = Images[i]
		currentList = []
		index = 0
		frameNum = 0
		ratio = 1/frameRate
		# debug.dprint(lengthVideos[i])
		videoFrames = lengthVideos[i]*frameRate
		for j in range(len(timestamps)):
			startT = timestamps[j][0]
			endT = timestamps[j][1]
			startTA = startT.split(":")
			endTA = endT.split(":")

			timestamps[j][0] = 60*int(startTA[0])+60*int(startTA[1])+float(startTA[2])
			timestamps[j][1] = 60*int(endTA[0])+60*int(endTA[1])+float(endTA[2])
		
		while index < len(timestamps):
			print(str(frameNum)+" out of "+str(videoFrames),end="\r")
			if(frameNum*ratio>= timestamps[index][0] and frameNum*ratio<=timestamps[index][1]):

				filename = addTextPIL(images,subtitles[index])
				
				frameNum+=1
				currentList.append(filename)

			elif(frameNum*ratio<=timestamps[index][0]):
				# debug.dprint([frameNum*ratio,timestamps[index][0],index])
				frameNum+=1
				currentList.append(images)


			elif(frameNum*ratio>=timestamps[index][1]):
				
				frameNum+=1
				currentList.append(images)
				index+=1
		for k in range(videoFrames-frameNum):
			currentList.append(images)
	mainList.append(currentList)
def createVideo(mainlist,songs,frameRate):
	for i in range(len(mainlist)):
		

		img = mainlist[i]
		f = open("temp.txt", "a")
		for j in range(len(mainlist[i])):
			f.write("file "+str(mainlist[i][j])+"\n")
		f.close()
		subprocess.call("ffmpeg -f concat -r "+str(frameRate)+" -i ./temp.txt videos/"+str(i)+".mp4",shell=True)
		subprocess.call('ffmpeg -i videos/'+str(i)+'.mp4 -i songs/'+str(i)+'.mp3 -c copy -c:a aac  -map 0:v:0 -map 1:a:0 results/'+str(i)+'.mp4',shell=True)
		subprocess.call('rm cache/*',shell=True)









downloadMp3(urls,DEVELOPER_KEY)
# print(lengthVideos)

downloadSubs(subs)
cleanSubs(subs)
createLyrics(Images,timeStamps,Subtitles,frameRate)
Songs = loadimages("songs",".mp3")
createVideo(mainList,Songs,frameRate)

