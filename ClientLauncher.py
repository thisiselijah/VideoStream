import sys
from tkinter import Tk
from Client import Client

if __name__ == "__main__":
	try:
		serverAddr = sys.argv[1]
		serverPort = sys.argv[2]
		rtpPort = sys.argv[3]
		fileName = sys.argv[4]	
	except:
		print("[Usage: ClientLauncher.py Server_name Server_port RTP_port Video_file]\n")	
	
	root = Tk()
	
	# Create a new client 172.20.10.3
	app = Client(root, "172.19.1.211", "65535", "65535", "movie.Mjpeg")
	app.master.title("RTPClient")




	root.mainloop()
	