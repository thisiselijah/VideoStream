import sys
from tkinter import Tk
from Client import Client

if __name__ == "__main__":
	try:
		#serverAddr = sys.argv[1]
		#serverPort = sys.argv[2]
		#rtpPort = sys.argv[3]
		fileName = sys.argv[1]	
	except:
		print ("[Usage: ClientLauncher.py Server_name Server_port RTP_port Video_file]\n")	
	
	root = Tk()
	root.geometry("896x356")

	# Create a new client
	app = Client(root, 'localhost', '65535', '1024', fileName)
	app.master.title("RTPClient")
	root.update_idletasks()
	# print(f"Window size - Width: {root.winfo_width()}, Height: {root.winfo_height()}")
	# print(f"Button position - X: {app.teardown.winfo_x()}, Y: {app.teardown.winfo_y()}")

	root.mainloop()
	