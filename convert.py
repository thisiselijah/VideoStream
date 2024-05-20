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
