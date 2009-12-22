from Tkinter import *
from tkMessageBox import askokcancel,showwarning
import tkSimpleDialog,tkColorChooser
import sys,os,codecs
import urllib2
from urllib2 import HTTPError
import twitter
import webbrowser
import re,threading
import Queue,time,random

class Status_Bar(Frame):
	def __init__ (self, Master):
		Frame.__init__(self, Master)
		self.label = Label(self,font=("Helvetica", 12),
						justify=CENTER, fg="Black")
		self.label.grid(columnspan=40,rowspan=1)
	def Set(self, Format, *args):
		self.label.config(text=Format % args)
		self.label.update_idletasks()
	def SetColor(self, Color):
		self.label.config(bg=Color)
		self.label.update_idletasks()
	def Clear(self):
		self.label.config(text="")
		self.label.update_idletasks()

class Twitter():
	def __init__(self,user,psw,run):
		self.API = twitter.Api(username = user, password = psw)
		self.friends = []
		self.followers = []
		self.statuses = []
		self.friendsStatuses = []
		self.friendsCount = 0
		self.followersCount = 0
		self.statusesCount = 0
		self.screanName = ""
		self.userID = user
		self.password = psw
		self.running = run
		self.lastStatusID = None
		self.userObject = None
		self.newUser = 1
		self.olddir = os.getcwd()
	def GetFriends(self):
		return self.API.GetFriends()
	def GetFriendsOrg(self):
		return self.API.GetFriends()
	def FindUser(self,name):
		for user in self.friends:
			if user.screen_name == name:
				return user
		return None
	def GetUser(self,username):
		return self.API.GetUser(username) 
	def GetUserTimeline(self):
		return self.API.GetUserTimeline()
	def GetUsersTimeline(self,user):
		return self.API.GetUserTimeline(user)
	def GetFollowers(self):
		return self.API.GetFollowers()
	def PostTwitt(self,text):
		status = self.API.PostUpdate(text)
		return status
	def GetUserInformation(self):
		del self.friends[:]
		del self.followers[:]
		del self.statuses[:]
		del self.friendsStatuses[:]
		try:
			self.userObject = self.GetUser(self.userID)
			self.friends = self.API.GetFriends()
			self.followers = self.API.GetFollowers()
#			self.statuses = self.API.GetUserTimeline(self.userID,count=100)
#			self.friendsStatuses = self.API.GetFriendsTimeline(self.userID,count=100)
#			self.lastStatusID = self.friendsStatuses[0].GetId()
			self.friendsCount = self.userObject.GetFriendsCount()
			self.followersCount = self.userObject.GetFollowersCount()
			self.statusesCount = self.userObject.GetStatusesCount()
		except HTTPError,e:
			showwarning("Authentication Error!","Login Error")
	def GetFollowers(self):
		return self.followers
	def GetFollowersCount(self,user=None):
		if user:
			return user.GetFollowersCount()
		else:
			return self.followersCount
	def GetFriendsCount(self,user=None):
		if user:
			return user.GetFriendsCount()
		else:
			return self.friendsCount
	def GetFriendsTimeline(self):
		return self.friendsStatuses
	def GetFriendsTimelineOrg(self,since=None):
		return self.API.GetFriendsTimeline(self.userID,count=100,since_id=since)
	def GetStatuses(self):
		return self.statuses
	def GetSentDM(self,since=None):
		return self.API.GetSentDirectMessages(since_id=since)
	def GetDM(self,since=None):
		return self.API.GetDirectMessages(since_id=since)
	def PostDM(self,user,text):
		return self.API.PostDirectMessage(user,text)
	def GetProfileTextColor(self,user=None):
		if user:
			return self.user.GetProfileTextColor()
		else:
			return self.userObject.GetProfileTextColor()
	def GetProfileBackgroundColor(self,user=None):
		if user:
			return user.GetProfileBackgroundColor()
		else:
			return self.userObject.GetProfileBackgroundColor()
	def GetUserReplies(self,since=None):
		return self.API.GetReplies(since_id=since)
	def GetPublicTimeline(self,since=None):
		return self.API.GetPublicTimeline(since_id=since)
	def GetUserFavorites(self):
		return self.API.GetFavorites()
	def Unfollow(self,user):
		self.API.DestroyFriendship(user)
	def Follow(self,user):
		self.API.CreateFriendship(user)
	def GetUserObject(self):
		return self.userObject
	def Worker(self):
		while self.running:
			time.sleep(rand.random() * 0.3)
			self.friendsStatuses = self.GetFriendsTimelineOrg(since=self.lastStatusID)		
			try:
				if len(self.friendsStatuses) != 0:
					print "self.friendsStatuses", len(self.friendsStatuses)
					queue.put(self.friendsStatuses)
					self.lastStatusID = self.friendsStatuses[0].id
			except IndexError:
				pass
			except urllib2.HTTPError,e:
				return -1,e
				pass
			except urllib2.URLError,e:
				return -1,e
	def interval2str(self,secs) :
		secs = int(secs)
		if secs < 60 :
			return str(secs) + " seconds ago"
		mins = int(secs / 60)
		secs = secs % 60
		if mins < 60 :
			return str(mins) + " mins " + str(secs) + " secs ago"
		hours = int(mins / 60)
		mins = mins % 60
		if (secs > 30) : mins += 1
		return str(hours) + " hours " + str(mins) + " mins ago"
		now = time.time()
	def SaveToFile(self,twits,filename=None):
		date = time.gmtime()
		newdir = self.olddir + "/" + self.userID
		if not os.path.isdir(newdir):
			 os.mkdir(self.userID)
		os.chdir(newdir)
		if date[1] / 10 != 0:
			month = str(date[1])
		else:
			month = "0" + str(date[1])
		if date[2] / 10 != 0:
			day = str(date[2])
		else:
			day = "0" + str(date[2])
		filename = str(date[0]) + month + day + ".csv"
		try:
			fp = codecs.open(filename,encoding='utf-8',mode="w")
			for k,v in twits.items():
				if "\n" in v[1]:
					b = v[1].replace("\n",";;.;;")
				else:
					b = v[1]
				fp.write(v[0] + ",,.,," + b + ",,.,," + str(v[2]) + "\n")
			fp.close()
			fp = open("last.txt","w")
			fp.write(self.userID + "," + str(self.lastStatusID))
			fp.close()
			os.chdir(self.olddir)
		except IOError,e:
			os.chdir(self.olddir)
			return -1,"IOError file save error"
		return 1
	def OpenFileToDic(self,filename=None):
		try:
			dict = {}
			i = 0
			if filename == None:
				newdir = self.olddir + "/" + self.userID
				if not os.path.isdir(newdir):
					return -1,"no file for this user is created"
				os.chdir(newdir)
				date = time.gmtime()
				if date[1] / 10 != 0:
					month = str(date[1])
				else:
					month = "0" + str(date[1])
				if date[2] / 10 != 0:
					day = str(date[2])
				else:
					day = "0" + str(date[2])
				filename = str(date[0]) + month + day + ".csv"
			fp = codecs.open(filename, encoding='utf-8', mode="r")
			for line in fp:
				name,text,ti = line.split(",,.,,")
				text = text.replace(";;.;;","\n")
				dict[i] = (name,text,long(ti))
				i += 1
		except IOError,e:
			os.chdir(self.olddir)
			return -1
		except ValueError,e:
			os.chdir(olddir)
			return -1
		except WindowsError:
			return -1
		os.chdir(self.olddir)
		return dict
	def SetLastStatusIDFromFile(self):
		try:
			newdir = self.olddir + "/" + self.userID
			if os.path.isdir(newdir):	
				os.chdir(newdir)		
				fp = open("last.txt","r")
				line = fp.readline()
				username,laststatus = line.split(",")
				fp.close()
				self.lastStatusID = long(laststatus)
				self.newUser = 0
				os.chdir(self.olddir)
			else:
				self.lastStatusID = None
		except IOError:
			self.lastStatusID = None
	def findURL(self,txt) :
		urlfinders = [
            re.compile("([0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}|(((news|telnet|nttp|file|http|ftp|https)://)|(www|ftp)[-A-Za-z0-9]*\\.)[-A-Za-z0-9\\.]+)(:[0-9]*)?/[-A-Za-z0-9_\\$\\.\\+\\!\\*,;:@&=\\?/~\\#\\%]*[^]'\\.}>\\),\\\"]"),
            re.compile("([0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}|(((news|telnet|nttp|file|http|ftp|https)://)|(www|ftp)[-A-Za-z0-9]*\\.)[-A-Za-z0-9\\.]+)(:[0-9]*)?"),
            re.compile("[#@][-A-Za-z0-9_]+")
        ]
		match = None
		for finder in urlfinders :
			newmatch = finder.search(txt)
			if not newmatch :
				continue
			if not match or newmatch.start() < match.start() :
				match = newmatch
		if not match :
			return -1, -1
		return match.start(), match.end()
	def SavePublicToFile(self,twits,lastStatusID):
		date = time.gmtime()
		if date[1] / 10 != 0:
			month = str(date[1])
		else:
			month = "0" + str(date[1])
		if date[2] / 10 != 0:
			day = str(date[2])
		else:
			day = "0" + str(date[2])
		filename = "public-" + str(date[0]) + month + day + ".csv"
		try:
			fp = codecs.open(filename,encoding='utf-8',mode="w")
			for k,v in twits.items():
				if "\n" in v[1]:
					b = v[1].replace("\n",";;.;;")
				else:
					b = v[1]
				fp.write(v[0] + ",,.,," + b + ",,.,," + str(v[2]) + "\n")
			fp.close()
			fp = open("last.txt","w")
			fp.write(self.userID + "," + str(lastStatusID))
			fp.close()
		except IOError,e:
			return -1,"IOError file save error"
		return 1
	def OpenPublicToDic(self,filename=None):
		try:
			dict = {}
			i = 0
			if filename == None:
				date = time.gmtime()
				if date[1] / 10 != 0:
					month = str(date[1])
				else:
					month = "0" + str(date[1])
				if date[2] / 10 != 0:
					day = str(date[2])
				else:
					day = "0" + str(date[2])
				filename = "public-" + str(date[0]) + month + day + ".csv"
			fp = codecs.open(filename,encoding='utf-8',mode="r")
			for line in fp:
				name,text,ti = line.split(",,.,,")
				text = text.replace(";;.;;","\n")
				dict[i] = (name,text,long(ti))
				i += 1
			fp.close()
			fp = open("last.txt","r")
			line = fp.readline()
			username,laststatus = line.split(",")
			fp.close()
		except IOError,e:
			os.chdir(self.olddir)
			return -1,None
		except ValueError,e:
			os.chdir(self.olddir)
			return -1,None
		except WindowsError:
			return -1,None
		return dict,laststatus

class FriendPanel(Frame):
		def __init__(self,name):
			Frame.__init__(self)
			global TWAPI
			self.urlfinders = [
							re.compile("([0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}|(((news|telnet|nttp|file|http|ftp|https)://)|(www|ftp)[-A-Za-z0-9]*\\.)[-A-Za-z0-9\\.]+)(:[0-9]*)?/[-A-Za-z0-9_\\$\\.\\+\\!\\*,;:@&=\\?/~\\#\\%]*[^]'\\.}>\\),\\\"]"),
							re.compile("([0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}|(((news|telnet|nttp|file|http|ftp|https)://)|(www|ftp)[-A-Za-z0-9]*\\.)[-A-Za-z0-9\\.]+)(:[0-9]*)?"),
							re.compile("[#@][-A-Za-z0-9_]+")]

			self.user = TWAPI.GetUser(name)
			self.friendsCount = TWAPI.GetFriendsCount(self.user)
			self.followersCount = TWAPI.GetFollowersCount(self.user) 
			self.statuses = TWAPI.GetUsersTimeline(name)
			self.statusesCount = len(self.statuses)
			self.MakeFriendPanel(self.user.screen_name)
		def MakeFriendPanel(self,name):
			self.FriendWindow = Toplevel()
			self.FriendWindow.bind("<Return>", self.OnTwitt2)
			self.FriendWindow.protocol("WM_DELETE_WINDOW", self.FriendWindow.destroy)
			self.FriendWindow.title("Twitter Activity for " + name)
			self.InfoBox = Message(self.FriendWindow,text="",fg="Black",
							font=("Helvetica",12), cursor="X_cursor")
			self.InfoBox.grid(row=0,column=0,rowspan=3,columnspan=10, sticky=E+W)
			
			self.TwittVS = Scrollbar(self.FriendWindow)			
			self.TwittBox = Text(self.FriendWindow,yscrollcommand=self.TwittVS.set)
			self.TwittBox.config(fg="black")
			self.TwittBox.config(wrap=WORD)

		# Prepare for URLs
			self.TwittBox.tag_config("a", background="#C8C8C8", foreground="black",underline=1,font=("Helvetica",11,"bold"))
			self.TwittBox.tag_config("b", foreground="black",font=("Helvetica",10))
			self.TwittBox.tag_config("c", foreground="black",font=("Helvetica",10))
			self.TwittBox.tag_config('link', foreground="blue",underline=1,font=("Helvetica",10))
			self.TwittBox.tag_bind("link", "<Enter>", self.show_hand_cursor)
			self.TwittBox.tag_bind("link", "<Leave>", self.show_arrow_cursor)
			self.TwittBox.tag_config('atname',foreground="blue",underline=1,font=("Helvetica",10))
			self.TwittBox.tag_config('sharp',foreground="blue",underline=1,font=("Helvetica",10))
			self.TwittBox.tag_bind("link", "<Enter>", self.show_hand_cursor)
			self.TwittBox.tag_bind("link", "<Leave>", self.show_arrow_cursor)
			self.TwittBox.tag_bind("atname", "<Enter>", self.show_hand_cursor)
			self.TwittBox.tag_bind("atname", "<Leave>", self.show_arrow_cursor)

			self.TwittBox.grid(row=0,column=10,rowspan=15,columnspan=80, sticky=E+W+N+S)
			self.TwittVS.grid(row=0,column=90,rowspan=15, sticky=N+S+W)
			self.TwittVS.config(command=self.TwittBox.yview)
			
			self.UnfollowButton = Button(self.FriendWindow,text="Unfollow",
								command=self.OnUnfollow)
			self.UnfollowButton.grid(row=6,column=1,sticky=W)
			self.TweetLabel = Label(self.FriendWindow,font=("Helvetica", 12),text="Tweet: ")
			self.TweetLabel.grid(row=16,column=8)
			self.TweetEntry = Entry(self.FriendWindow,
								font=("Helvetica",12), cursor="X_cursor")
			self.TweetEntry.insert(0,"@" + name + " ") 
			self.TweetEntry.bind("<Key>", self.Handle_Tweet_Counter)
			self.TweetEntry.focus_force()
			self.TweetEntry.grid(row=16,column=10,columnspan= 85, sticky=E+W)
		
			self.TweetButton = Button(self.FriendWindow,text="Tweet!",
								command=self.OnTwitt)
			self.TweetButton.grid(row=16,column= 95,sticky=W)
			self.TweetCounterLabel = Status_Bar(self.FriendWindow)
			self.TweetCounterLabel.Clear()
			self.TweetCounterLabel.Set("%s","140")
			self.TweetCounterLabel.grid(row=16,column=95 + 10,sticky=W)

			self.FriendWindow.geometry('800x310+350+70')
			self.FriendWindow.columnconfigure(11,weight=1)
			self.FriendWindow.rowconfigure(0,weight=1)
			self.FriendWindow.rowconfigure(1,weight=1)
			self.Initialize()
		def Handle_TwittBox_Extraction(self,event):
			self.TwittIndex = self.TwittBox.curselection()
			self.TwittName = self.TwittBox.get(self.TwittIndex)
		def InsertToTwittBox(self,Item,format):
			self.TwittBox.insert(END , Item,format)
		def InsertTweet(self,regex, tweet):
			global TWAPI
			msg = tweet
			while True:
				lstart, lend = TWAPI.findURL(msg)
				if lstart < 0 :   # No more links
					self.TwittBox.insert(END, msg)
					break
				# Found a link. Linkify it
				self.TwittBox.insert(END, msg[0:lstart])
				link = msg[lstart:lend]
				if link[0] == "@":
					self.TwittBox.insert(END, link, ('atname', link))
					self.TwittBox.tag_bind(link, '<Button-1>',
									lambda e, url=link: FriendPanel(url))
				elif link[0] == "#":
					self.TwittBox.insert(END, link, ('sharp', link))
				else:
					self.TwittBox.insert(END, link, ('link', link))
					self.TwittBox.tag_bind(link, '<Button-1>',
							lambda e, url=link: webbrowser.open(url))
				msg = msg[lend:]
		def OnTwitt(self):
			twittText = self.TweetEntry.get()
			self.TweetEntry.delete(0,len(twittText))
			global TWAPI
			TWAPI.PostTwitt(twittText)
		def OnTwitt2(self,event):
			self.OnTwitt()
		def OnUnfollow(self):
			global TWAPI
			TWAPI.Unfollow(self.user.screen_name)
			self.UnfollowButton.config(state=DISABLED)
			self.update_idletasks()
		def Initialize(self):
			now = time.time()
			self.InfoBox.config(text= "Friends :" + 
					str(self.friendsCount) + "\nFollowers: " + 
					str(self.followersCount) + "\nStatus Count: " +
					str(self.statusesCount))
			self.InfoBox.update_idletasks()
			global TWAPI
			self.setBackgroundColor(TWAPI.GetProfileBackgroundColor(self.user))
			for Item in self.statuses:
				interval = TWAPI.interval2str(now - Item.created_at_in_seconds)
				self.InsertToTwittBox(interval + "\n","a")
				self.InsertTweet(self.urlfinders[0],Item.text)
				self.InsertToTwittBox("\n","c")
		def setBackgroundColor(self,color):
			self.FriendWindow.config(bg="#" + color)
			self.FriendWindow.config(highlightcolor="#" + color)
			self.InfoBox.config(bg="#" + color)
			self.TweetLabel.config(bg="#" + color)
			self.update_idletasks()
		@staticmethod
		def show_hand_cursor(event) :
			event.widget.configure(cursor="hand1")
		@staticmethod
		def show_arrow_cursor(event):
			event.widget.configure(cursor="arrow")
		def Handle_Tweet_Counter(self,event):
			size = len(self.TweetEntry.get())
			self.TweetCounterLabel.Set(str(140 - size))
class DirectMessage(Frame):
	def __init__(self):
		Frame.__init__(self)
		global TWAPI
		self.sentMsg = 1
		self.sentMsgList = TWAPI.GetSentDM(None)
		self.recMsgList = TWAPI.GetDM(None)
		self.followerList = TWAPI.GetFollowers()
		self.name = TWAPI.userObject.screen_name
		self.MakeWindow()
	def MakeWindow(self):
		self.DMWindow = Toplevel()
		self.DMWindow.bind("<Return>", self.OnPost)
		self.DMWindow.protocol("WM_DELETE_WINDOW", self.DMWindow.destroy)
		self.DMWindow.title("Direct Message for " + self.name)
		
		self.MsgLbl = Label(self.DMWindow,font=("Helvetica", 12),text="Msg: Sent to")
		self.MsgLbl.grid(row=0,column=0,sticky=E+W)
			
		self.UserLbl = Label(self.DMWindow,font=("Helvetica", 12),text="User List")
		self.UserLbl.grid(row=0,column=22,sticky=E+W)

		self.MsgListVS = Scrollbar(self.DMWindow)
		self.MsgList = Listbox(self.DMWindow,yscrollcommand=self.MsgListVS.set)
		self.MsgList.bind("<Double-1>", self.Handle_MsgList_Extraction)
		self.MsgList.grid(row=1,column=0,rowspan=15,columnspan=20, sticky=E+W+N+S)
		self.MsgListVS.grid(row=1,column=21,rowspan=15, sticky=N+S+W)		
		self.MsgListVS.config(command=self.MsgList.yview)
		
		self.FriendListVS = Scrollbar(self.DMWindow)
		self.FriendList = Listbox(self.DMWindow,yscrollcommand=self.FriendListVS.set)
		self.FriendList.bind("<Double-1>", self.Handle_FriendList_Extraction)
		self.FriendList.grid(row=1,column=22,rowspan=15,columnspan=20, sticky=E+W+N+S)
		self.FriendListVS.grid(row=1,column=43,rowspan=15, sticky=N+S+W)		
		self.FriendListVS.config(command=self.FriendList.yview)

		self.TwittVS = Scrollbar(self.DMWindow)			
		self.TwittBox = Text(self.DMWindow,yscrollcommand=self.TwittVS.set)
		self.TwittBox.tag_config("a", background="#C8C8C8", foreground="black",underline=1,font=("Helvetica",11,"bold"))
		self.TwittBox.tag_config("b", foreground="black",font=("Helvetica",10))
		self.TwittBox.tag_config("c", foreground="black",font=("Helvetica",10))
		self.TwittBox.config(fg="black")
		self.TwittBox.config(wrap=WORD)
		self.TwittBox.grid(row=1,column=44,rowspan=14,columnspan=40, sticky=E+W+N+S)	
		self.TwittVS.grid(row=1,column=85,rowspan=14, sticky=N+S+W)
		self.TwittVS.config(command=self.TwittBox.yview)				
		self.TweetEntry = Entry(self.DMWindow,fg="Black",
								font=("Helvetica",12), cursor="xterm")
		self.TweetEntry.focus_force()
		self.TweetEntry.grid(row=15,column=44,columnspan= 40, sticky=E+W)
		
		self.ToggeleButton = Button(self.DMWindow,text="Toggle",
								command=self.OnToggle,state=NORMAL)
		self.ToggeleButton.grid(row=16,column=4)
		self.PostButton = Button(self.DMWindow,text="Send",
								command=self.OnPost,state=NORMAL)
		self.PostButton.grid(row=16,column=40)
		self.DMWindow.columnconfigure(45,weight=1)
		self.DMWindow.rowconfigure(8,weight=1)
		self.initial()
	def initial(self):
		for Item in self.followerList:
			self.InsertToFriendList(Item.screen_name)
		for Item in self.sentMsgList:
			self.InsertToMsgList(Item.recipient_screen_name)
		color = TWAPI.userObject.profile_background_color
		color = "#" + color
		self.DMWindow.config(bg=color)
		self.MsgLbl.config(bg=color)
		self.UserLbl.config(bg=color)
		self.update_idletasks()				
	def OnPost(self):
		Index = self.FriendList.curselection()
		Name = self.FriendList.get(Index)
		text = self.TweetEntry.get()
		TWAPI.PostDM(Name, text)
		self.TweetEntry.delete(0, END)
		self.InsertToTwittBox("Sent successfully.",None)
		self.InsertToTwittBox("----------\n")
	def OnToggle(self):
		self.sentMsgList = TWAPI.GetSentDM(None)
		self.recMsgList = TWAPI.GetDM(None)
		self.MsgList.delete(0,self.MsgList.size())
		if self.sentMsg == 1:
			for Item in self.sentMsgList:
				self.InsertToMsgList(Item.recipient_screen_name)
			self.sentMsg = 0
			self.MsgLbl.config(text="Sent to:")
			self.update_idletasks()
		else:
			for Item in self.recMsgList:
				self.InsertToMsgList(Item.sender_screen_name)
			self.sentMsg = 1
			self.MsgLbl.config(text="Recieve from:")
			self.update_idletasks()			
	def Handle_FriendList_Extraction(self,event):
		Index = self.FriendList.curselection()
		Name = self.FriendList.get(Index)
		UserObj = TWAPI.GetUser(Name)
		self.InsertToTwittBox("Name: " + UserObj.name + "\n")
		self.InsertToTwittBox("Screan Name:" + UserObj.screen_name + "\n")
		self.InsertToTwittBox("Location: " + str(UserObj.location) + "\n")
		self.InsertToTwittBox("Description: " + str(UserObj.description) + "\n")
		self.InsertToTwittBox("URL: " + str(UserObj.url) + "\n")
		if UserObj.status != None:
			self.InsertToTwittBox("Status: " + str(UserObj.status.text) + "\n")
		self.InsertToTwittBox("Statuses Count: " + str(UserObj.statuses_count) + "\n")
		self.InsertToTwittBox("-------------------------\n")
	def Handle_MsgList_Extraction(self,event):
		Index = self.MsgList.curselection()
		Name = self.MsgList.get(Index)
		for Item in self.sentMsgList:
			if Item.recipient_screen_name == Name:
				self.InsertToTwittBox(Item.text + "\n")
				self.InsertToTwittBox(Item.created_at + "\n")
				self.InsertToTwittBox("Sender: " + Item.sender_screen_name + "\n")
				self.InsertToTwittBox("Reciever: " + Item.recipient_screen_name + "\n")
				self.InsertToTwittBox("----------\n")
		for Item in self.recMsgList:
			if Item.sender_screen_name == Name:
				self.InsertToTwittBox(Item.text + "\n")
				self.InsertToTwittBox(Item.created_at + "\n")
				self.InsertToTwittBox("Sender: " + Item.sender_screen_name + "\n")
				self.InsertToTwittBox("Reciever:" + Item.recipient_screen_name + "\n")
				self.InsertToTwittBox("----------\n")
	def InsertToFriendList(self,Item):
		self.FriendList.insert(END, Item)
		self.FriendList.update_idletasks()
	def InsertToMsgList(self,Item):
		self.MsgList.insert(END, Item)
		self.MsgList.update_idletasks()
	def InsertToTwittBox(self,text,format=None):
		self.TwittBox.insert(END , text,format)
		
class ControlPanel(Frame):
	def __init__(self,parent,main):
		Frame.__init__(self,parent)
		self.parent = parent
		self.main = main
		self.twitDic = {}
		self.twitDict = {}
		self.td= {}
		self.profileFlag = 0
		self.searchFlag = 0
		self.searchText = ""
		self.ficOld = 0
		self.focOld = 0
		self.firstTime = 1
		self.twitCount = 0
		self.bgOld = None
		self.statusOld = None
		self.friendOld = None
		self.friendNew = None
		self.popMenuUser = None
		self.columnSpanSize = 10
		self.lineNumber = 1
		self.urlfinders = [
			re.compile("([0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}|(((news|telnet|nttp|file|http|ftp|https)://)|(www|ftp)[-A-Za-z0-9]*\\.)[-A-Za-z0-9\\.]+)(:[0-9]*)?/[-A-Za-z0-9_\\$\\.\\+\\!\\*,;:@&=\\?/~\\#\\%]*[^]'\\.}>\\),\\\"]"),
			re.compile("([0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}|(((news|telnet|nttp|file|http|ftp|https)://)|(www|ftp)[-A-Za-z0-9]*\\.)[-A-Za-z0-9\\.]+)(:[0-9]*)?"),
			re.compile("[#@][-A-Za-z0-9_]+")]

		self.menubar = Menu(parent)
		self.filemenu = Menu(self.menubar, tearoff=0)
		self.filemenu.add_command(label="Log out", command=self.OnLogoutMnu)
		self.filemenu.add_command(label="Search", command=self.OnSearchMnu)
		self.filemenu.add_command(label="Find User", command=self.OnFindUserMnu)
		self.filemenu.add_command(label="Account Info", command=self.OnAccountInfoMnu)
		self.filemenu.add_separator()
		self.filemenu.add_command(label="Exit", command=self.OnExitMnu)
		self.menubar.add_cascade(label="File", menu=self.filemenu)
		self.viewmenu = Menu(self.menubar, tearoff=0)
		self.viewmenu.add_command(label="Home", command=self.OnHome)
		self.viewmenu.add_command(label="Profile", command=self.OnProfile)
		self.viewmenu.add_command(label="@Replies", command=self.OnReply)
		self.viewmenu.add_command(label="Favorites", command=self.OnFavorite)
		self.viewmenu.add_command(label="Public", command=self.OnPublic)
		self.menubar.add_cascade(label="View", menu=self.viewmenu)
		self.settingmenu = Menu(self.menubar, tearoff=0)
		self.settingmenu.add_command(label="Profile Colors", command=self.OnProfileColorMnu)
		self.settingmenu.add_command(label="Profile Info", command=self.OnProfileInfoMnu)
		self.menubar.add_cascade(label="Settings", menu=self.settingmenu)
		self.directmenu = Menu(self.menubar, tearoff=0)
		self.directmenu.add_command(label="Open", command=self.OnDMOpen)
		self.menubar.add_cascade(label="Direct Messages", menu=self.directmenu)
		self.aboutmenu = Menu(self.menubar, tearoff=0)
		self.aboutmenu.add_command(label="About", command=self.OnAboutMnu)
		self.menubar.add_cascade(label="Help", menu=self.aboutmenu)
		parent.config(menu=self.menubar)
		
		self.StatusLabel = Status_Bar(parent)
		self.StatusLabel.Clear()
		self.Data = "Status:"		
		self.StatusLabel.Set("%s",self.Data)
		self.StatusLabel.grid(row=0,column=0)
		
		self.bind("<Return>", self.OnTweet2)
		self.StatusLbl = Label(parent,font=("Helvetica", 12))
		self.StatusLbl.grid(row=0,column=1,columnspan= 20)

		self.FollowingButton = Button(parent,text="Following",
								command=self.OnFollowing)
		self.FollowingButton.grid(row=0,column=24)
		self.FollowingNumberLbl = Status_Bar(parent)
		self.FollowingNumberLbl.Clear()
		self.FollowingNumberLbl.grid(row=0,column=25)
		
		
		self.FollowersButton = Button(parent,text="Followers",
								command=self.OnFollower)
		self.FollowersButton.grid(row=1,column=24)
		self.FollowersNumberLbl = Status_Bar(parent)		
		self.FollowersNumberLbl.grid(row=1,column=25)
		
		self.TwittVS = Scrollbar(parent,takefocus=1)
		self.TwittVS.focus_force()
		self.TwittBox = Text(parent,yscrollcommand=self.TwittVS.set)
		self.TwittBox.config(fg="black")
		self.TwittBox.config(wrap=WORD)

		# Prepare for URLs
		self.TwittBox.tag_config("a", background="#C8C8C8", foreground="black",underline=1,font=("Helvetica",11,"bold"))
		self.TwittBox.tag_config("b", foreground="black",font=("Helvetica",10))
		self.TwittBox.tag_config("c", foreground="black",font=("Helvetica",10))
		self.TwittBox.tag_config('link', foreground="blue",underline=1,font=("Helvetica",10))
		self.TwittBox.tag_config('search',background="#FFFF00" ,font=("Helvetica",10))
		self.TwittBox.tag_config('atname',foreground="blue",underline=1,font=("Helvetica",10))
		self.TwittBox.tag_config('sharp',foreground="blue",underline=1,font=("Helvetica",10))
		self.TwittBox.tag_bind("link", "<Enter>", self.show_hand_cursor)
		self.TwittBox.tag_bind("link", "<Leave>", self.show_arrow_cursor)
		self.TwittBox.tag_bind("atname", "<Enter>", self.show_hand_cursor)
		self.TwittBox.tag_bind("atname", "<Leave>", self.show_arrow_cursor)


#		self.TwittBox.grid(row=5,column=0,rowspan=15,columnspan=self.columnSpanSize, sticky=E+W+N+S)
		self.TwittBox.grid(row=2,column=0,rowspan=15,columnspan = 10, sticky=W+S+N)
		self.TwittVS.grid(row=2,column=10 ,rowspan=15, sticky=S+W+N+E)
		self.TwittVS.config(command=self.TwittBox.yview)
		
		self.TwittVS2 = Scrollbar(parent,takefocus=1)
		self.TwittBox2 = Text(parent,yscrollcommand=self.TwittVS2.set)
		self.TwittBox2.config(fg="black")
		self.TwittBox2.config(wrap=WORD)
		
		# Prepare for URLs
		self.TwittBox2.tag_config("a", background="#C8C8C8", foreground="black",underline=1,font=("Helvetica",11,"bold"))
		self.TwittBox2.tag_config("b", foreground="black",font=("Helvetica",10))
		self.TwittBox2.tag_config("c", foreground="black",font=("Helvetica",10))
		self.TwittBox2.tag_config('link', foreground="blue",underline=1,font=("Helvetica",10))
		self.TwittBox2.tag_config('search',background="#FFFF00" ,font=("Helvetica",10))
		self.TwittBox2.tag_config('atname',foreground="blue",underline=1,font=("Helvetica",10))
		self.TwittBox2.tag_config('sharp',foreground="blue",underline=1,font=("Helvetica",10))
		self.TwittBox2.tag_bind("link", "<Enter>", self.show_hand_cursor)
		self.TwittBox2.tag_bind("link", "<Leave>", self.show_arrow_cursor)
		self.TwittBox2.tag_bind("atname", "<Enter>", self.show_hand_cursor)
		self.TwittBox2.tag_bind("atname", "<Leave>", self.show_arrow_cursor)


		self.TwittBox2.grid(row=2,column= 12 ,rowspan=15,columnspan = 10, sticky=E+W+S+N)
		self.TwittVS2.grid(row=2,column= 22, rowspan=15, sticky=S+W+N)
		self.TwittVS2.config(command=self.TwittBox2.yview)

		
		self.FriendListVS = Scrollbar(parent)
		self.FriendList = Listbox(parent, yscrollcommand=self.FriendListVS.set)
		self.FriendList.bind("<Double-1>", self.Handle_List_Extraction)
		self.FriendList.grid(row=5,column=24,rowspan=15,columnspan=10, sticky=E+W+N+S)
		
		self.FriendListVS.grid(row=5,column=34,rowspan=15, sticky=N+S+W)
		self.FriendListVS.config(command=self.FriendList.yview)
		self.TweetLabel = Status_Bar(parent)
		self.TweetLabel.Clear()
		self.TweetLabel.Set("%s","Tweet: ")
		self.TweetLabel.grid(row=21,column=0,sticky=W)
		self.TweetEntry = Entry(parent,fg="Black",
								font=("Helvetica",12), cursor="xterm")
		self.TweetEntry.focus_force()
		self.TweetEntry.grid(row=21,column=1,columnspan=22, sticky=E+W)
		self.TweetEntry.bind("<Key>", self.Handle_Tweet_Counter)
		self.TweetButton = Button(parent,text="Update",
								command=self.OnTweet,state=DISABLED)
		self.TweetButton.grid(row=21,column=24)
		self.TweetCounterLabel = Status_Bar(parent)
		self.TweetCounterLabel.Clear()
		self.TweetCounterLabel.Set("%s","140")
		self.TweetCounterLabel.grid(row=21,column=25,sticky=W)
		self.PopMenu = Menu(parent, tearoff=0)
		self.PopView = Menu(self.PopMenu, tearoff=0)
		self.PopMenu.add_command(label="Open...", command=self.OnOpenPopMenu)
		self.PopMenu.add_command(label="Reply", command=self.OnReplyPopMenu)
		self.PopMenu.add_command(label="Follow", command=self.OnFollowingPopMenu)
		self.PopMenu.add_command(label="Unfollow", command=self.OnUnFollowingPopMenu)
		parent.columnconfigure(8,weight=1)
		parent.columnconfigure(18,weight=1)
		parent.rowconfigure(8,weight=1)
	def Popup(self,event):
		self.PopMenu.post(event.x_root, event.y_root)
	def OnAboutMnu(self):
		self.AccountWindow = Toplevel()
		self.AccountWindow.geometry('+550+300')
		self.AccountWindow.bind("<Return>", self.OnFindUserBtn)
		self.AccountWindow.protocol("WM_DELETE_WINDOW", self.AccountWindow.destroy)
		self.AccountWindow.title("About ")
		
		self.AccountWindow.NameLbl = Label(self.AccountWindow,justify=RIGHT,text="by Khashayar Dehdashtinejad")
		self.AccountWindow.NameLbl.grid(row=1,column=0)
		self.AccountWindow.LoginButton = Button(self.AccountWindow,text="Close!",fg="Black",
												command=self.AccountWindow.destroy,default=ACTIVE)
		self.AccountWindow.LoginButton.grid(row=2,column=1,rowspan=2,columnspan= 8)
	def OnOpenPopMenu(self):
		FriendPanel(self.popMenuUser)
	def OnReplyPopMenu(self):
		self.TweetEntry.insert(0,"@" + self.popMenuUser)
	def OnFollowingPopMenu(self):
		TWAPI.Follow(self.popMenuUser)
		self.setStatusBox("You are following " + self.popMenuUser + "now.")
		self.ficOld += 1
		self.setFollowingCount(self.ficOld)
		self.friendOld = TWAPI.GetFriends()
		self.FriendList.delete(0, END)
		for Item in self.friendOld:
			self.InsertToFriendList(Item.screen_name)		
	def OnUnFollowingPopMenu(self):
		TWAPI.Unfollow(self.popMenuUser)
		self.setStatusBox("You are following " + self.popMenuUser + "now.")
		self.ficOld -= 1
		self.setFollowingCount(self.ficOld)	
		self.friendOld = TWAPI.GetFriends()
		self.FriendList.delete(0, END)
		for Item in self.friendOld:
			self.InsertToFriendList(Item.screen_name)			
	@staticmethod
	def show_hand_cursor(event) :
		event.widget.configure(cursor="hand1")
	@staticmethod
	def show_arrow_cursor(event):
		event.widget.configure(cursor="arrow")
	def OnReply(self):
		self.profileFlag = 3
		replies = TWAPI.GetUserReplies()
		td = {}
		twitDict = {}
		twitCount = 0
		for Item in replies:
			td[twitCount] = (Item.user.screen_name,Item.text,Item.created_at_in_seconds)
			twitCount += 1
		it = [(v[2],v[1],v[0], k) for k, v in td.items()]
		it.sort()
		it.reverse()
		iff=0
		for v2,v1,v0,k in it:
			twitDict[iff] = (v0,v1,v2)
			iff += 1
		self.TwittBox2.delete(1.0,END)
		now = time.time()
		for k,v in twitDict.items():
			interval = TWAPI.interval2str(now - v[2])
			self.InsertToTwittBoxGen(v[0] + ": \t\t" + interval + "\n","a",self.TwittBox2)
			self.InsertTweetGen(v[1],self.TwittBox2)
			self.InsertToTwittBoxGen("\n","c",self.TwittBox2)
	def OnFavorite(self):
		self.profileFlag = 4
		now = time.time()
		public = TWAPI.GetUserFavorites()
		td = {}
		twitDict = {}
		twitCount = 0
		for Item in public:
			td[twitCount] = (Item.user.screen_name,Item.text,Item.created_at_in_seconds)
			twitCount += 1
		it = [(v[2],v[1],v[0], k) for k, v in td.items()]
		it.sort()
		it.reverse()
		iff=0
		for v2,v1,v0,k in it:
			twitDict[iff] = (v0,v1,v2)
			iff += 1
		self.TwittBox2.delete(1.0,END)
		for k,v in twitDict.items():
			interval = TWAPI.interval2str(now - v[2])
			self.InsertToTwittBoxGen(v[0] + ": \t\t" + interval + "\n","a",self.TwittBox2)
			self.InsertTweetGen(v[1],self.TwittBox2)
			self.InsertToTwittBoxGen("\n","c",self.TwittBox2)
	def OnPublic(self):
		self.profileFlag = 5
		now = time.time()
		self.TwittBox2.delete(1.0,END)
		lastID=None
		td = {}
		twitCount = 0
		pb,lastID = TWAPI.OpenPublicToDic()
		if pb != -1 and lastID != None:
			public = TWAPI.GetPublicTimeline(since= int(lastID))
			td.update(pb)
			twitCount = len(pb.keys())
		else:
			public = TWAPI.GetPublicTimeline()
		
		twitDict = {}
		lastStatusID = public[0].id		
		for Item in public:
			td[twitCount] = (Item.user.screen_name,Item.text,Item.created_at_in_seconds)
			twitCount += 1
		it = [(v[2],v[1],v[0], k) for k, v in td.items()]
		it.sort()
		it.reverse()
		iff=0
		for v2,v1,v0,k in it:
			twitDict[iff] = (v0,v1,v2)
			iff += 1
		TWAPI.SavePublicToFile(twitDict, lastStatusID)
		for k,v in twitDict.items():
			interval = TWAPI.interval2str(now - v[2])
			self.InsertToTwittBoxGen(v[0] + ": \t\t" + interval + "\n","a",self.TwittBox2)
			self.InsertTweetGen(v[1],self.TwittBox2)
			self.InsertToTwittBoxGen("\n","c",self.TwittBox2)
	def Handle_Tweet_Counter(self,event):
		size = len(self.TweetEntry.get())
		self.TweetCounterLabel.Set(str(140 - size))
		if size > 0 and size < 141:
			self.TweetButton.config(state=NORMAL)
			self.TweetButton.update_idletasks()
		else:
			self.TweetButton.config(state=DISABLED)
			self.TweetButton.update_idletasks()
	def setFollowingCount(self,numb):
		self.FollowingNumberLbl.Set(str(numb))
	def setFollowersCount(self,numb):
		self.FollowersNumberLbl.Set(str(numb))
	def OnFollowing(self):
		print "Following"
	def Handle_List_Extraction(self,event):
		self.FriendIndex = self.FriendList.curselection()
		self.FriendName = self.FriendList.get(self.FriendIndex)
		self.FP = FriendPanel(self.FriendName)
	def InsertToFriendList(self,Item):
		self.FriendList.insert(END, Item)
		self.FriendList.update_idletasks()
	def Handle_TwittBox_Extraction(self,event):
		self.TwittIndex = self.TwittBox.curselection()
		self.TwittName = self.TwittBox.get(self.TwittIndex)
	def InsertToTwittBox(self,Item,format):
		self.TwittBox.insert(END , Item,format)
		self.lineNumber += 1
	def InsertToTwittBoxGen(self,Item,format,TextBox):
		TextBox.insert(END , Item,format)
	def InsertTweet(self,regex,tweet):
		TextGadget = self.TwittBox
		index = 0
		for match in re.finditer(regex, tweet):
			start, end = match.span()
			if index < start:
				TextGadget.insert(END, tweet[index:start],"b") # Regular text
			url = tweet[start:end] # <-- Alter this line
			TextGadget.insert(END, url, ("link", url))
			TextGadget.tag_bind(url, '<Button-1>',
							lambda e, url=url: webbrowser.open(url))
			index = end
		if index < len(tweet):
			TextGadget.insert(END, tweet[index:],"b") # Regular text
	def InsertTweetGen(self,tweet,TextBox):
		global TWAPI
		msg = tweet
		while True:
			lstart, lend = TWAPI.findURL(msg)
			if lstart < 0 :   # No more links
				TextBox.insert(END, msg)
				break
			# Found a link. Linkify it
			TextBox.insert(END, msg[0:lstart])
			link = msg[lstart:lend]
			if link[0] == "@":
				TextBox.insert(END, link, ('atname', link))
				TextBox.tag_bind(link, '<Button-1>',
									lambda e, url=link: FriendPanel(url))
				TextBox.tag_bind(link, '<Button-3>',
									lambda e, url=link: self.OnPopMenu(e,"FriendPanel",url))
			elif link[0] == "#":
				TextBox.insert(END, link, ('sharp', link))
			else:
				TextBox.insert(END, link, ('link', link))
				TextBox.tag_bind(link, '<Button-1>',
							lambda e, url=link: webbrowser.open(url))				
			msg = msg[lend:]
	def InsertTweetNew(self,tweet):
		global TWAPI
		msg = tweet
		while True:
			lstart, lend = TWAPI.findURL(msg)
			if lstart < 0 :   # No more links
				self.TwittBox.insert(END, msg)
				break
			# Found a link. Linkify it
			self.TwittBox.insert(END, msg[0:lstart])
			link = msg[lstart:lend]
			if link[0] == "@":
				self.TwittBox.insert(END, link, ('atname', link))
				self.TwittBox.tag_bind(link, '<Button-1>',
									lambda e, url=link: FriendPanel(url))
				self.TwittBox.tag_bind(link, '<Button-3>',
									lambda e, url=link: self.OnPopMenu(e,"FriendPanel",url))
			elif link[0] == "#":
				self.TwittBox.insert(END, link, ('sharp', link))
			else:
				self.TwittBox.insert(END, link, ('link', link))
				self.TwittBox.tag_bind(link, '<Button-1>',
							lambda e, url=link: webbrowser.open(url))				
			msg = msg[lend:]
	def OnPopMenu(self,event,method,item):
		self.popMenuUser = item.lstrip("@")
		username = self.popMenuUser.lower()
		flag = 0
		for Item in self.friendOld:
			if username == Item.screen_name.lower():
				flag = 1
		if flag == 1:
			self.PopMenu.entryconfigure(2,state=DISABLED)
			self.PopMenu.entryconfigure(3,state=ACTIVE)
		else:
			self.PopMenu.entryconfigure(3,state=DISABLED)
			self.PopMenu.entryconfigure(2,state=ACTIVE)
									
		self.PopMenu.post(event.x_root, event.y_root)
	def OnTweet2(self,event):
		self.OnTweet(self)
	def OnTweet(self):
		twittText = self.TweetEntry.get()
		if len(twittText) > 140:
			showwarning("Tweet's lenght Error","Your tweet's length is greater than 140 characters!")
			return -1,"length of tweet is greater than 140 characters"
		self.TweetEntry.delete(0,len(twittText))
		self.setStatusBox(twittText)
		global TWAPI
		TWAPI.PostTwitt(twittText)
	def OnRefresh(self):
		try:
			if self.firstTime == 1:
				self.firstTime = 0
				self.twitDic = {}
				self.twitDict = {}
				iff=0
				global TWAPI
				if not TWAPI.newUser:
					self.td = TWAPI.OpenFileToDic()
					if self.td != -1:
						it = [(v[2],v[1],v[0], k) for k, v in self.td.items()]
						it.sort()
						it.reverse()
						for v2,v1,v0,k in it:
							self.twitDict[iff] = (v0,v1,v2)
							iff += 1
						self.twitCount = iff - 1
						self.UpdateTimes()
					else:
						self.td = {}
				self.OnPublic()
				self.ficOld = TWAPI.GetFriendsCount()
				self.focOld = TWAPI.GetFollowersCount()
				self.bgOld = TWAPI.GetProfileBackgroundColor()
				self.setFollowingCount(self.ficOld)
				self.setFollowersCount(self.focOld)
				self.setBackgroundColor(self.bgOld)
				self.friendOld = TWAPI.GetFriends()
				self.aaa = len(self.friendOld)
				for Item in self.friendOld:
					self.InsertToFriendList(Item.screen_name)
				self.friendStatusesOld = queue.get(0)
				self.fsoc = len(self.friendStatusesOld)
				self.userStatusesOld = TWAPI.GetStatuses()
				self.usoc = len(TWAPI.GetStatuses())
			else:
				self.friendStatusesNew = queue.get(0)
				self.setStatusBox(str(len(self.friendStatusesNew)) + " new tweet(s) arrived.")
				for Item in self.friendStatusesNew:
					self.twitDic.setdefault(Item.user.screen_name,[]).append(Item.user.screen_name + ": " +
										Item.text + " - " + str(Item.created_at_in_seconds) + ".")					
					self.td[self.twitCount] = (Item.user.screen_name,Item.text,Item.created_at_in_seconds)
					self.twitCount += 1
				it = [(v[2],v[1],v[0], k) for k, v in self.td.items()]
				it.sort()
				it.reverse()
				iff=0
				for v2,v1,v0,k in it:
					self.twitDict[iff] = (v0,v1,v2)
					iff += 1
				self.UpdateTimes()	
				if self.profileFlag == 0:
					pass
				elif self.profileFlag == 1:
					self.OnProfile()
				elif self.searchFlag == 1: #profileflag == 2
					pass
				elif self.profileFlag == 3: #reply view
					pass
				elif self.profileFlag == 4: # favorite view
					pass
				elif self.profileFlag == 5: # public view
					self.OnPublic()		
		except urllib2.HTTPError,e:
			showwarning("Authentication Error!","Login Error2")
		except AttributeError,e:
			print e
			pass
		except IndexError,e:
			print e
			pass
		except Queue.Empty,e:
			self.fsoc = 0
			self.usoc = 0
			pass
	def UpdateTimes(self):
		self.TwittBox.delete(1.0,END)
		now = time.time()
		for k,v in self.twitDict.items():
			interval = TWAPI.interval2str(now - v[2])
			self.InsertToTwittBox(v[0] + ": \t\t" + interval + "\n","a")
			self.InsertTweetNew(v[1])
			self.InsertToTwittBox("\n","c")
	def setStatusBox(self,txt):
		self.StatusLbl.config(text=txt)
		self.StatusLbl.update_idletasks()
	def setBackgroundColor(self,color):
		self.parent.config(bg="#" + color)
		self.parent.config(highlightcolor="#" + color)
		self.StatusLbl.config(bg="#" + color)
		self.FollowersNumberLbl.SetColor("#" + color)
		self.StatusLabel.SetColor("#" + color)
		self.TweetLabel.SetColor("#" + color)
		self.FollowingNumberLbl.SetColor("#" + color)
		self.update_idletasks()
	def setTextColor(self):
		color = tkColorChooser.askcolor("#" + TWAPI.userObject.profile_text_color)
		color = color[1]
		self.TwittBox.config(fg=color)
		self.update_idletasks()
	def setStatusColor(self):
		color = tkColorChooser.askcolor("#" + TWAPI.userObject.profile_background_color)
		color = color[1]
		self.StatusLbl.config(bg=color)
		self.update_idletasks()
	def SetBgColor(self):
		color = tkColorChooser.askcolor("#" + TWAPI.userObject.profile_background_color)
		color = color[1]
		self.parent.config(bg=color)
		self.parent.config(highlightcolor=color)
		self.StatusLbl.config(bg=color)
		self.FollowersNumberLbl.SetColor(color)
		self.StatusLabel.SetColor(color)
		self.TweetLabel.SetColor(color)
		self.FollowingNumberLbl.SetColor(color)
		self.update_idletasks()		
	def OnSearch2(self,event):
		self.OnSearch()
	def OnSearch(self):
		self.searchFlag = 1
		self.profileFlag = 2
		resultList = []
		self.searchText = self.FindUserWindow.SearchEntry.get()
		self.FindUserWindow.destroy()
		self.TwittBox.delete(1.0,END)
		now = time.time()
		for k,v in self.twitDict.items():
			if re.search(self.searchText,v[1]) != None:
				interval = TWAPI.interval2str(now - v[2])
				self.InsertToTwittBox(v[0] + ": \t\t" + interval + "\n","a")
				index = 0
				regex= re.compile(self.searchText)
				for match in re.finditer(regex, v[1]):
					start, end = match.span()
					if index < start:
#						self.InsertTweet(self.urlfinders[0], v[1][index:start]) # Regular text
						self.InsertTweetNew(v[1][index:start]) # Regular text
						url = v[1][start:end] # <-- Alter this line
						self.TwittBox.insert(END, url, ("search", url))
						index = end
					elif index == start:
						url = v[1][start:end] # <-- Alter this line
						self.TwittBox.insert(END, url, ("search", url))
						index = end
				if index < len(v[1]):
#					self.InsertTweet(self.urlfinders[0], v[1][index:]) # Regular text
					self.InsertTweetNew(v[1][index:]) # Regular text
				self.InsertToTwittBox("\n","c")
	def OnProfile(self):
		self.profileFlag = 1
		public = TWAPI.GetUserTimeline()
		td = {}
		twitDict = {}
		twitCount = 0
		for Item in public:
			td[twitCount] = (Item.user.screen_name,Item.text,Item.created_at_in_seconds)
			twitCount += 1
		it = [(v[2],v[1],v[0], k) for k, v in td.items()]
		it.sort()
		it.reverse()
		iff=0
		for v2,v1,v0,k in it:
			twitDict[iff] = (v0,v1,v2)
			iff += 1
		self.TwittBox2.delete(1.0,END)
		now = time.time()
		for k,v in twitDict.items():
			interval = TWAPI.interval2str(now - v[2])
			self.InsertToTwittBoxGen(v[0] + ": \t\t" + interval + "\n","a",self.TwittBox2)
			self.InsertTweetGen(v[1],self.TwittBox2)
			self.InsertToTwittBoxGen("\n","c",self.TwittBox2)
	def OnHome(self):
		self.profileFlag = 0
		self.searchFlag = 0
		self.UpdateTimes()
	def OnFollower(self):
		global TWAPI
		self.FriendList.delete(0,self.FriendList.size())
		for Item in TWAPI.GetFollowers():
				self.InsertToFriendList(Item.screen_name)
	def OnFollowing(self):
		global TWAPI
		self.FriendList.delete(0,self.FriendList.size())
		self.friendOld = TWAPI.GetFriends()
		for Item in self.friendOld:
				self.InsertToFriendList(Item.screen_name)
	def OnFindUserMnu(self):
		self.FindUserWindow = Toplevel()
		self.FindUserWindow.geometry('+550+300')
		self.FindUserWindow.bind("<Return>", self.OnFindUserBtn)
		self.FindUserWindow.protocol("WM_DELETE_WINDOW", self.FindUserWindow.destroy)
		self.FindUserWindow.title("User Search...")
		self.FindUserWindow.WelcomeLbl = Label(self.FindUserWindow,font=("Helvetica", 12),text="User Search...",
						  					fg="Black")
		self.FindUserWindow.WelcomeLbl.grid(row=0,column=1)
		self.FindUserWindow.UsernameLabel = Status_Bar(self.FindUserWindow)
		self.FindUserWindow.UsernameLabel.Set("%s","Username: ")
		self.FindUserWindow.UsernameLabel.grid(row=1,column=0)
		self.FindUserWindow.UsernameEntry = Entry(self.FindUserWindow,fg="Black", bg="White",
												font=("Helvetica",12), cursor="X_cursor")
		self.FindUserWindow.UsernameEntry.focus_force()
		self.FindUserWindow.UsernameEntry.grid(row=1,column=1,rowspan=1,columnspan= 20, sticky=E+W)
		self.FindUserWindow.LoginButton = Button(self.FindUserWindow,text="Find!",fg="Black",
												command=self.OnFindUserBtn,default=ACTIVE)
		self.FindUserWindow.LoginButton.grid(row=3,column=1,rowspan=2,columnspan= 8)
	def OnFindUserBtn(self):
		self.FriendName = self.FindUserWindow.UsernameEntry.get()
		try:
			user = TWAPI.GetUser(self.FriendName)
			self.FP = FriendPanel(user.screen_name)
			self.FindUserWindow.destroy()
		except urllib2.HTTPError:
			showwarning("User Not Found!",self.FriendName + " is not found!")
	def OnSearchMnu(self):
		self.FindUserWindow = Toplevel()
		self.FindUserWindow.geometry('+550+300')
		self.FindUserWindow.bind("<Return>", self.OnSearch2)
		self.FindUserWindow.protocol("WM_DELETE_WINDOW", self.FindUserWindow.destroy)
		self.FindUserWindow.title("Twitt Search...")
		self.FindUserWindow.WelcomeLbl = Label(self.FindUserWindow,font=("Helvetica", 12),text="Twitt Search...",
						  					fg="Black")
		self.FindUserWindow.WelcomeLbl.grid(row=0,column=1)
		self.FindUserWindow.UsernameLabel = Status_Bar(self.FindUserWindow)
		self.FindUserWindow.UsernameLabel.Set("%s","Find: ")
		self.FindUserWindow.UsernameLabel.grid(row=1,column=0)
		self.FindUserWindow.SearchEntry = Entry(self.FindUserWindow,fg="Black", bg="White",
												font=("Helvetica",12), cursor="X_cursor")
		self.FindUserWindow.SearchEntry.focus_force()
		self.FindUserWindow.SearchEntry.grid(row=1,column=1,rowspan=1,columnspan= 20, sticky=E+W)
		self.FindUserWindow.FindButton = Button(self.FindUserWindow,text="Find!",fg="Black",
												command=self.OnSearch,default=ACTIVE)
		self.FindUserWindow.FindButton.grid(row=3,column=1,rowspan=2,columnspan= 8)
	def OnExitMnu(self):
		self.main.Quit()
	def OnLogoutMnu(self):
		Reply = askokcancel("Verify logout","Do you want to logout?")
		if Reply !=0:
			self.FriendList.delete(0,self.FriendList.size())
			self.TwittBox.delete(1.0,END)
			self.friendOld = None
			self.firstTime = 1
			self.twitDic = None
			self.profileFlag = 0
			self.bgOld = None
			self.statusOld = None
			self.friendOld = None
			self.friendNew = None
			self.ficOld = None
			self.focOld = None
			self.bgOld = None
			self.lineNumber = 1
			self.main.Logout()
	def OnAccountInfoMnu(self):
		user = TWAPI.GetUserObject()
		self.AccountWindow = Toplevel()
		self.AccountWindow.geometry('+550+300')
		self.AccountWindow.bind("<Return>", self.OnFindUserBtn)
		self.AccountWindow.protocol("WM_DELETE_WINDOW", self.AccountWindow.destroy)
		self.AccountWindow.title("User Account Information for " + user.screen_name)
		
		self.AccountWindow.NameLbl = Label(self.AccountWindow,justify=RIGHT,text="Name: ")
		self.AccountWindow.NameLbl.grid(row=1,column=0)
		self.AccountWindow.Name2Lbl = Label(self.AccountWindow,text=user.name,justify=RIGHT,relief=GROOVE)
		self.AccountWindow.Name2Lbl.grid(row=1,column=1)
		self.AccountWindow.LocationLbl = Label(self.AccountWindow,justify=RIGHT,text="Location: ")
		self.AccountWindow.LocationLbl.grid(row=2,column=0)
		self.AccountWindow.LocationLbl2 = Label(self.AccountWindow,text=user.location,justify=RIGHT,relief=GROOVE)
		self.AccountWindow.LocationLbl2.grid(row=2,column=1)
		self.AccountWindow.DescriptionLbl = Label(self.AccountWindow,text="Description: ",justify=RIGHT)
		self.AccountWindow.DescriptionLbl.grid(row=3,column=0)
		self.AccountWindow.DescriptionLbl2 = Label(self.AccountWindow,text=user.description,justify=RIGHT,relief=GROOVE)
		self.AccountWindow.DescriptionLbl2.grid(row=3,column=1)		
		self.AccountWindow.URLLbl = Label(self.AccountWindow,text="URL: ",justify=RIGHT)
		self.AccountWindow.URLLbl.grid(row=4,column=0)
		self.AccountWindow.URLLbl2 = Label(self.AccountWindow,text=user.url,justify=RIGHT,relief=GROOVE)
		self.AccountWindow.URLLbl2.grid(row=4,column=1)
		
		self.AccountWindow.LoginButton = Button(self.AccountWindow,text="Close!",fg="Black",
												command=self.AccountWindow.destroy,default=ACTIVE)
		self.AccountWindow.LoginButton.grid(row=5,column=1,rowspan=2,columnspan= 8)
	def OnProfileColorMnu(self):
		user = TWAPI.GetUserObject()
		self.ColorWindow = Toplevel()
		self.ColorWindow.geometry('+550+300')
		self.ColorWindow.bind("<Return>", self.OnFindUserBtn)
		self.ColorWindow.protocol("WM_DELETE_WINDOW", self.ColorWindow.destroy)
		self.ColorWindow.title("Chnage Colors ")
		
		self.ColorWindow.NameLbl = Label(self.ColorWindow,justify=RIGHT,text="Status Bar: ")
		self.ColorWindow.NameLbl.grid(row=1,column=0)
		self.ColorWindow.Name2Lbl = Button(self.ColorWindow,text="Choose Color",fg="Black",
												command=self.setStatusColor,default=ACTIVE)
		self.ColorWindow.Name2Lbl.grid(row=1,column=1)
		self.ColorWindow.LocationLbl = Label(self.ColorWindow,justify=RIGHT,text="Profile Background: ")
		self.ColorWindow.LocationLbl.grid(row=2,column=0)
		self.ColorWindow.LocationLbl2 = Button(self.ColorWindow,text="Choose Color",fg="Black",
												command=self.SetBgColor,default=ACTIVE)
		self.ColorWindow.LocationLbl2.grid(row=2,column=1)
		self.ColorWindow.DescriptionLbl = Label(self.ColorWindow,text="Text: ",justify=RIGHT)
		self.ColorWindow.DescriptionLbl.grid(row=3,column=0)
		self.ColorWindow.DescriptionLbl2 = Button(self.ColorWindow,text="Choose Color",fg="Black",
												command=self.setTextColor,default=ACTIVE)
		self.ColorWindow.DescriptionLbl2.grid(row=3,column=1)		
		
		self.ColorWindow.LoginButton = Button(self.ColorWindow,text="Close",fg="Black",
												command=self.ColorWindow.destroy,default=ACTIVE)
		self.ColorWindow.LoginButton.grid(row=5,column=1,rowspan=2,columnspan= 8)
	def OnProfileInfoMnu(self):
		self.ProfileWindow = Toplevel()
		self.ProfileWindow.geometry('+550+300')
		self.ProfileWindow.bind("<Return>", self.OnSubmitProfileInfo)
		self.ProfileWindow.protocol("WM_DELETE_WINDOW", self.ProfileWindow.destroy)
		self.ProfileWindow.title("User Information")

		self.ProfileWindow.nameLabel = Status_Bar(self.ProfileWindow)
		self.ProfileWindow.nameLabel.Set("%s","Real Name: ")
		self.ProfileWindow.nameLabel.grid(row=1,column=0)
		self.ProfileWindow.nameEntry = Entry(self.ProfileWindow,fg="Black", bg="White",
												font=("Helvetica",12), cursor="X_cursor")
		self.ProfileWindow.nameEntry.focus_force()
		self.ProfileWindow.nameEntry.grid(row=1,column=1,rowspan=1,columnspan= 20, sticky=E+W)
		
		self.ProfileWindow.bioLabel = Status_Bar(self.ProfileWindow)
		self.ProfileWindow.bioLabel.Set("%s","Bio: ")
		self.ProfileWindow.bioLabel.grid(row=2,column=0)
		self.ProfileWindow.bioEntry = Entry(self.ProfileWindow,fg="Black", bg="White",
												font=("Helvetica",12), cursor="X_cursor")
		self.ProfileWindow.bioEntry.grid(row=2,column=1,rowspan=1,columnspan= 20, sticky=E+W)
		self.ProfileWindow.locationLabel = Status_Bar(self.ProfileWindow)
		self.ProfileWindow.locationLabel.Set("%s","Location: ")
		self.ProfileWindow.locationLabel.grid(row=3,column=0)
		self.ProfileWindow.locationEntry = Entry(self.ProfileWindow,fg="Black", bg="White",
												font=("Helvetica",12), cursor="X_cursor")
		self.ProfileWindow.locationEntry.grid(row=3,column=1,rowspan=1,columnspan= 20, sticky=E+W)
		
		self.ProfileWindow.LoginButton = Button(self.ProfileWindow,text="Submit",fg="Black",
												command=self.OnSubmitProfileInfo,default=ACTIVE)
		self.ProfileWindow.LoginButton.grid(row=4,column=1,rowspan=2,columnspan= 8)
	def OnSubmitProfileInfo(self):
		name = self.ProfileWindow.nameEntry.get()
		location = self.ProfileWindow.locationEntry.get()
		bio = self.ProfileWindow.bioEntry.get()	
		self.ProfileWindow.destroy()
		if name != "":
			TWAPI.userObject.SetName(name)
		TWAPI.userObject.SetLocation(location)
		TWAPI.userObject.SetDescription(bio)	
	def OnDMOpen(self):
		self.DM = DirectMessage()
class Main():
		def __init__(self):
			self.user = None
			self.API = None
			self.timeID = None
			self.running = 1
			self.Root = Tk()
			self.Root.title("KimZ")
			self.Root.protocol("WM_DELETE_WINDOW", self.Quit)
			self.Root.geometry('880x310+350+70')
			self.Root.resizable(TRUE,TRUE)
			self.StopEvent = threading.Event()
			self.Panel = ControlPanel(self.Root,self)
			self.Panel.grid(sticky=N+S+E+W)
				
			self.Root.withdraw()
			self.LoginPanel()
			self.Root.mainloop()
		def LoginPanel(self):
			self.LoginWindow = Toplevel()
			self.LoginWindow.geometry('+550+300')
			self.LoginWindow.bind("<Return>", self.OnLogin2)
			self.LoginWindow.protocol("WM_DELETE_WINDOW", self.Quit)
			self.LoginWindow.title("Connect to Twitter...")
			self.LoginWindow.WelcomeLbl = Label(self.LoginWindow,font=("Helvetica", 12),text="Welcome to pyTweet",
						  fg="Black")
			self.LoginWindow.WelcomeLbl.grid(row=0,column=1)
			self.LoginWindow.UsernameLabel = Status_Bar(self.LoginWindow)
			self.LoginWindow.UsernameLabel.Set("%s","Username: ")
			self.LoginWindow.UsernameLabel.grid(row=1,column=0)
			self.LoginWindow.UsernameEntry = Entry(self.LoginWindow,fg="Black", bg="White",
								font=("Helvetica",12), cursor="xterm")
			self.LoginWindow.UsernameEntry.focus_force()
			self.LoginWindow.UsernameEntry.grid(row=1,column=1,rowspan=1,columnspan= 20, sticky=E+W)
			self.LoginWindow.PasswordLabel = Status_Bar(self.LoginWindow)
			self.LoginWindow.PasswordLabel.Set("%s","Password: ")
			self.LoginWindow.PasswordLabel.grid(row=2,column=0)
			self.LoginWindow.PasswordEntry = Entry(self.LoginWindow,show = "*", fg="Black", bg="White",
								font=("Helvetica",12), cursor="xterm")
			self.LoginWindow.PasswordEntry.grid(row=2,column=1,rowspan=1,columnspan= 20, sticky=E+W)
			self.LoginWindow.LoginButton = Button(self.LoginWindow,text="Login!",fg="Black",
								command=self.OnLogin,default=ACTIVE)
			self.LoginWindow.LoginButton.grid(row=3,column=1,rowspan=2,columnspan= 8)
		def OnLogin2(self,event):
			self.OnLogin()
		def OnLogin(self):
			try:	
				self.API = Twitter(self.LoginWindow.UsernameEntry.get(),self.LoginWindow.PasswordEntry.get(),self.running)
				self.user = self.API.GetFriendsOrg()
				if self.user != None:
					self.Root.title(self.LoginWindow.UsernameEntry.get() + " - KimZ")
					global TWAPI
					TWAPI = self.API
					TWAPI.SetLastStatusIDFromFile()
					TWAPI.GetUserInformation()
					self.t = threading.Thread(target=TWAPI.Worker)
					self.t.start()
					self.LoginWindow.destroy()
					self.Root.deiconify()
					self.InitializePanel()
				else :
					showwarning("Authentication Error!","Login Error, No friends")
			except urllib2.HTTPError:
				showwarning("Authentication Error!","Http Error!")
			except urllib2.URLError:
				showwarning("Authentication Error!","URL Error!")
			except ValueError,e:
				showwarning("Authentication Error!","Internet Connection Error!" + str(e))
		def InitializePanel(self):
			self.Panel.OnRefresh()
			if not self.running:
				import sys
				self.Root.destroy()
				self.Root.after_cancel(self.timeID)
				self.StopEvent.set()
				self.StopEvent.wait()
				sys.exit(1)
			self.timeID = self.Root.after(9000, self.InitializePanel)
		def Quit(self):
			Reply = askokcancel("Verify exit","Do you want to exit?")
			if Reply !=0:
				self.running = 0
				if self.timeID == None:
					self.Root.destroy()
				else:
					self.API.SaveToFile(self.Panel.twitDict)
					self.Root.after_cancel(self.timeID)
					self.StopEvent.set()
					self.StopEvent.wait()
					self.InitializePanel()
		def GetTWAPI(self):
			return self.API
		def Logout(self):
			self.API.SaveToFile(self.Panel.twitDict)
			self.Root.withdraw()
			self.StopEvent.set()
			self.StopEvent.wait()
			self.Root.after_cancel(self.timeID)
			del self.Panel
			del self.API
			del self.user
			TWAPI = None
			self.Panel = ControlPanel(self.Root,self)
			self.Panel.grid(sticky=N+S+E+W)
			self.Root.withdraw()
			self.LoginPanel()

if __name__ == '__main__':
	TWAPI = None
	rand = random.Random()
	queue = Queue.Queue()
	m = Main()
	
