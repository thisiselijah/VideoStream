from tkinter import *
import tkinter.messagebox

tkinter.messagebox
from tkinter import messagebox

tkinter.messagebox
from PIL import Image, ImageTk
import socket, threading, sys, traceback, os
import platform
import cv2
import os

from RtpPacket import RtpPacket
CACHE_FILE_NAME = "cache-"
CACHE_FILE_EXT = ".jpg"


class Client:
    SETUP_STR = 'SETUP'
    PLAY_STR = 'PLAY'
    PAUSE_STR = 'PAUSE'
    TEARDOWN_STR = 'TEARDOWN'
    INIT = 0
    READY = 1
    PLAYING = 2
    state = INIT

    SETUP = 0
    PLAY = 1
    PAUSE = 2
    TEARDOWN = 3

    RTSP_VER = "RTSP/1.0"
    TRANSPORT = "RTP/UDP"

    # Initiation..
    def __init__(self, master, serveraddr, serverport, rtpport, filename):
        self.master = master
        self.master.protocol("WM_DELETE_WINDOW", self.handler)
        self.user_os = platform.system()
        self.scale = 1.0
        self.speed = ['x0.5', 'x0.75', 'x1.0', 'x1.25', 'x1.5']
        self.createWidgets()

        self.serverAddr = serveraddr
        self.serverPort = int(serverport)
        self.rtpPort = int(rtpport)
        self.fileName = filename
        self.rtspSeq = 0
        self.sessionId = 0
        self.requestSent = -1
        self.teardownAcked = 0
        self.connectToServer()
        self.frameNbr = 0

        #若為mp4檔 則將mp4轉為mjpeg
        if  self.check_mjpeg_exists():
            self.update_filename_extension()
        else:
            self.convert()
            self.update_filename_extension()

    def update_filename_extension(self):
        #將檔名轉為mjpeg
        base, ext = os.path.splitext(self.fileName)
        if ext.lower() == '.mp4':
            self.fileName = f"{base}.mjpeg"

    def check_mjpeg_exists(self):
        #判斷mjpeg是否存在
        base_name = os.path.splitext(self.fileName)[0]  #取得檔名(不包括擴展名)
        folder_path = os.path.dirname(self.fileName)
        mjpeg_filename = f"{base_name}.mjpeg"

        return os.path.exists(mjpeg_filename)

    def createWidgets(self):
        """Build GUI."""
        # Create Setup button

        self.setup = Button(self.master, width=20, padx=3, pady=3)
        self.setup["text"] = "Setup"
        self.setup["command"] = self.setupMovie
        self.setup.grid(row=1, column=0, padx=2, pady=2)

        # Create Play button
        self.start = Button(self.master, width=20, padx=3, pady=3)
        self.start["text"] = "Play"
        self.start["command"] = self.playMovie
        self.start.grid(row=1, column=1, padx=2, pady=2)

        # Create Pause button
        self.pause = Button(self.master, width=20, padx=3, pady=3)
        self.pause["text"] = "Pause"
        self.pause["command"] = self.pauseMovie
        self.pause.grid(row=1, column=2, padx=2, pady=2)

        # Create Teardown button
        self.teardown = Button(self.master, width=20, padx=3, pady=3)
        self.teardown["text"] = "Teardown"
        self.teardown["command"] = self.exitClient
        self.teardown.grid(row=1, column=3, padx=2, pady=2)

        # Create a label to display the movie
        self.label = Label(self.master, height=19)
        self.label.grid(row=0, column=0, columnspan=4, sticky=W + E + N + S, padx=5, pady=5)
        # print("User's operating system:", user_os_string)

        if str(self.user_os) == "Windows":
            self.menu_0 = Menu(self.master)
            self.menu_1 = Menu(self.menu_0)
            self.var = StringVar(value="")
            for element in self.speed:
                if element == 'x1.0':
                    self.var.set(element)
                self.menu_1.add_radiobutton(label=element, variable=self.var, value=element, command=self.playSpeed)
            self.menu_0.add_cascade(label='Speed', menu=self.menu_1)
            self.master.config(menu=self.menu_0)
        else:
            self.menubar = Menu(self.master)
            self.menu_0 = Menu(self.menubar)
            self.menu_1 = Menu(self.menu_0)
            self.var = StringVar(value="")
            for element in self.speed:
                if element == 'x1.0':
                    self.var.set(element)
                self.menu_1.add_radiobutton(label=element, variable=self.var, value=element, command=self.playSpeed)
            self.menu_0.add_cascade(label='Speed', menu=self.menu_1)
            self.menubar.add_cascade(label='Option', menu=self.menu_0)
            self.master.config(menu=self.menubar)

# Width: 896, Height: 356

    def setupMovie(self):
        """Setup button handler."""
        if self.state == self.INIT:
            self.sendRtspRequest(self.SETUP)

    def exitClient(self):
        """Teardown button handler."""
        self.sendRtspRequest(self.TEARDOWN)
        self.master.destroy()  # Close the gui window
        os.remove(CACHE_FILE_NAME + str(self.sessionId) + CACHE_FILE_EXT)  # Delete the cache image from video

    def pauseMovie(self):
        """Pause button handler."""
        if self.state == self.PLAYING:
            self.sendRtspRequest(self.PAUSE)

    def playMovie(self):
        """Play button handler."""
        if self.state == self.READY:
            # Create a new thread to listen for RTP packets
            threading.Thread(target=self.listenRtp).start()
            self.playEvent = threading.Event()
            self.playEvent.clear()
            self.sendRtspRequest(self.PLAY)

    def playSpeed(self):
        origin = self.scale

        ps = self.var.get()
        scale_dict = {
            'x0.5': 0.5,
            'x0.75': 0.75,
            'x1.0': 1.0,
            'x1.25': 1.25,
            'x1.5': 1.5
        }
        if origin != scale_dict.get(ps, 1.0):
            self.scale = scale_dict.get(ps, 1.0)

        if self.state == self.READY:
            pass
        elif self.state == self.PLAYING:
            try:
                self.sendRtspRequest(self.PAUSE)
                self.state = self.READY
                self.sendRtspRequest(self.PLAY)
                print(ps)
                print(self.scale)
            except Exception as e:
                print(f"Error in playSpeed: {e}")

    def listenRtp(self):
        """Listen for RTP packets."""
        while True:
            try:
                print("LISTENING...")
                data = self.rtpSocket.recv(204800) #default 20480
                if data:
                    rtpPacket = RtpPacket()
                    rtpPacket.decode(data)

                    currFrameNbr = rtpPacket.seqNum()
                    print("CURRENT SEQUENCE NUM: " + str(currFrameNbr))

                    if currFrameNbr > self.frameNbr:  # Discard the late packet
                        self.frameNbr = currFrameNbr
                        self.updateMovie(self.writeFrame(rtpPacket.getPayload()))
                
            except:
                # Stop listening upon requesting PAUSE or TEARDOWN
                if self.playEvent.isSet():
                    break

                # Upon receiving ACK for TEARDOWN request,
                # close the RTP socket
                if self.teardownAcked == 1:
                    self.rtpSocket.shutdown(socket.SHUT_RDWR)
                    self.rtpSocket.close()
                    break

    def writeFrame(self, data):
        """Write the received frame to a temp image file. Return the image file."""
        cachename = CACHE_FILE_NAME + str(self.sessionId) + CACHE_FILE_EXT
        file = open(cachename, "wb")
        file.write(data)
        file.close()

        return cachename

    def updateMovie(self, imageFile):
        """Update the image file as video frame in the GUI."""
        photo = ImageTk.PhotoImage(Image.open(imageFile))
        self.label.configure(image=photo, height=288)
        self.label.image = photo

    def connectToServer(self):
        """Connect to the Server. Start a new RTSP/TCP session."""
        self.rtspSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.rtspSocket.connect((self.serverAddr, self.serverPort))
        except:
            messagebox.showwarning('Connection Failed', 'Connection to \'%s\' failed.' % self.serverAddr)

    def sendRtspRequest(self, requestCode):
        """Send RTSP request to the server."""
        # -------------
        # TO COMPLETE
        # -------------

        # Setup request
        if requestCode == self.SETUP and self.state == self.INIT:
            threading.Thread(target=self.recvRtspReply).start()
            # Update RTSP sequence number.
            self.rtspSeq += 1
            # Write the RTSP request to be sent.
            request = "SETUP " + self.fileName + " RTSP/1.0" + "\nCseq: " + str(
                self.rtspSeq) + "\nTransport: RTP/UDP; dest_port: " + str(self.rtpPort)

            # Keep track of the sent request.
            self.requestSent = self.SETUP

        # Play request
        elif requestCode == self.PLAY and self.state == self.READY:

            # Update RTSP sequence number.
            self.rtspSeq += 1

            # Write the RTSP request to be sent.
            request = "PLAY " + self.fileName + " RTSP/1.0" + "\nCseq: " + str(self.rtspSeq) + "\nScale: " + str(
                self.scale) + "\nTransport: RTP/UDP; dest_port: " + str(self.rtpPort)
            # request = "PLAY "+ self.fileName + " RTSP/1.0"+ "\nCseq: "+str(self.rtspSeq) +"\nTransport: RTP/UDP; dest_port: "+str(self.rtpPort)
            # Keep track of the sent request.
            self.requestSent = self.PLAY

        # Pause request
        elif requestCode == self.PAUSE and self.state == self.PLAYING:

            # Update RTSP sequence number.
            self.rtspSeq += 1

            # Write the RTSP request to be sent.
            request = "PAUSE " + self.fileName + " RTSP/1.0" + "\nCseq: " + str(
                self.rtspSeq) + "\nTransport: RTP/UDP; dest_port: " + str(self.rtpPort)

            # Keep track of the sent request.
            self.requestSent = self.PAUSE

        # Teardown request
        elif requestCode == self.TEARDOWN and not self.state == self.INIT:

            # Update RTSP sequence number.
            self.rtspSeq += 1

            # Write the RTSP request to be sent.
            request = "TEARDOWN " + self.fileName + " RTSP/1.0" + "\nCseq: " + str(
                self.rtspSeq) + "\nTransport: RTP/UDP; dest_port: " + str(self.rtpPort)

            # Keep track of the sent request.
            self.requestSent = self.TEARDOWN
        else:
            return
        print(self.state)
        # Send the RTSP request using rtspSocket.
        self.rtspSocket.send(request.encode('utf-8'))  # rtspSocket在connectToServer中是Socket的物件
        print('\nData sent:\n' + request)

    def recvRtspReply(self):
        """Receive RTSP reply from the server."""
        while True:
            reply = self.rtspSocket.recv(1024)

            if reply:
                self.parseRtspReply(reply)

            # Close the RTSP socket upon requesting Teardown
            if self.requestSent == self.TEARDOWN:
                self.rtspSocket.shutdown(socket.SHUT_RDWR)
                self.rtspSocket.close()
                break

    def parseRtspReply(self, data):
        """Parse the RTSP reply from the server."""
        lines = data.decode().split('\n')
        seqNum = int(lines[1].split(' ')[1])

        # Process only if the server reply's sequence number is the same as the request's
        if seqNum == self.rtspSeq:
            session = int(lines[2].split(' ')[1])
            # New RTSP session ID
            if self.sessionId == 0:
                self.sessionId = session

            # Process only if the session ID is the same
            if self.sessionId == session:
                if int(lines[0].split(' ')[1]) == 200:
                    if self.requestSent == self.SETUP:
                        # -------------
                        # TO COMPLETE
                        # -------------

                        # Update RTSP state.
                        self.state = self.READY

                        # Open RTP port.
                        self.openRtpPort()
                    elif self.requestSent == self.PLAY:
                        self.state = self.PLAYING
                    elif self.requestSent == self.PAUSE:
                        self.state = self.READY
                        # The play thread exits. A new thread is created on resume.
                        self.playEvent.set()
                    elif self.requestSent == self.TEARDOWN:
                        self.state = self.INIT

                        # Flag the teardownAcked to close the socket.
                        self.teardownAcked = 1

    def openRtpPort(self):
        """Open RTP socket binded to a specified port."""

        # -------------
        # TO COMPLETE
        # -------------

        # Create a new datagram socket to receive RTP packets from the server
        self.rtpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Set the timeout value of the socket to 0.5sec
        self.rtpSocket.settimeout(0.5)

        try:
            # Bind the socket to the address using the RTP port given by the client user.
            self.state = self.READY
            self.rtpSocket.bind(('', self.rtpPort))
        except:
            messagebox.showwarning('Unable to Bind', 'Unable to bind PORT=%d' % self.rtpPort)

    def handler(self):
        """Handler on explicitly closing the GUI window."""
        self.pauseMovie()
        if messagebox.askokcancel("Quit?", "Are you sure you want to quit?"):
            self.exitClient()
        else:  # When the user presses cancel, resume playing.
            self.playMovie()

    def convert(self):
        input_file = self.fileName

        # 獲取文件名（不包括擴展名）
        base_name = os.path.splitext(input_file)[0]

        # 生成输出文件路徑，將擴展名替換為 .mjpeg
        output_file = f'{base_name}.mjpeg'

        # 打開输入影片文件
        cap = cv2.VideoCapture(input_file)

        if not cap.isOpened():
            print(f"無法打開輸入文件 {input_file}")
            exit()

        # 獲取影片的宽度、高度和帧率
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)

        # 檢查影片属性是否讀取成功
        if frame_width == 0 or frame_height == 0 or fps == 0:
            print("無法讀取影片属性")
            cap.release()
            exit()

        # 定義 MJPEG 編碼和創建 VideoWriter 對象
        fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        out = cv2.VideoWriter(output_file, fourcc, fps, (frame_width, frame_height))

        if not out.isOpened():
            print(f"無法建立输出文件 {output_file}")
            cap.release()
            exit()

        # 逐帧讀取並寫入输出文件
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            out.write(frame)