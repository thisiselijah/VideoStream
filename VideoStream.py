class VideoStream:
	def __init__(self, filename):
		self.filename = filename
		try:
			self.file = open('./data/'+filename, 'rb')
		except:
			raise IOError

		self.frameNum = 0
	def getFrameLength(self):
		"""Get the length of the next frame."""
		while True:
			byte = self.file.read(1)
			if not byte:
				return -1  # End of file
			if byte == b'\xff':
				next_byte = self.file.read(1)
				if next_byte == b'\xd8':  # Found SOI
					start_position = self.file.tell() - 2
					while True:
						byte = self.file.read(1)
						if not byte:
							return -1  # End of file
						if byte == b'\xff':
							next_byte = self.file.read(1)
							if next_byte == b'\xd9':  # Found EOI
								end_position = self.file.tell()
								return end_position - start_position
   

	def nextFrame(self):
		"""Get next frame."""
		 # Get the framelength from the first 5 bits
		try:
			data = self.file.read(5)
			if data: 
				"""print(data)"""
				framelength = int(data)			
				# Read the current frame
				data = self.file.read(framelength)
				self.frameNum += 1
			"""else:
				print('data error')"""
		except:
			framelength = self.getFrameLength()
			framelength = int(framelength)
			data = self.file.read(framelength)
			self.frameNum += 1
		return data
		
	def frameNbr(self):
		"""Get frame number."""
		return self.frameNum
	
	