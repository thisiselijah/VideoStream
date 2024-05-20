"""import ffmpeg

# Input and output file paths
input_file = 'spongebob.mpeg'
output_file = 'output.Mjpeg'

# Convert MPEG to MJPEG
try:
	(
		ffmpeg
		.input(input_file)
		.output(output_file, vcodec='mjpeg')
		.run(overwrite_output=True)
	)
	print(f"Conversion successful: {output_file}")
except ffmpeg.Error as e:
	print(f"Error: {e.stderr.decode()}")"""
class VideoStream:
	def __init__(self, filename):
		self.filename = filename
		try:
			self.file = open(filename, 'rb')
		except:
			raise IOError
	def getData(self):
		framelength = self.getFrameLength()
		framelength = int(framelength)
		data = self.file.read(framelength)
		return data
	
	def getFrameLength(self):
		"""Get the length of the next frame."""
		try:
			framelength = self.file.read(5)
			framelength = int(framelength)
			return framelength
		except:
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


if __name__ == "__main__":
	video = VideoStream('output.Mjpeg')
	
	print(video.getData())