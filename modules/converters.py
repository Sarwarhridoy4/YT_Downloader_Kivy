import ffmpeg

def convert_to_mp3(input_path, output_path):
    try:
        stream = ffmpeg.input(input_path)
        stream = ffmpeg.output(stream, output_path, format='mp3', audio_bitrate='192k')
        ffmpeg.run(stream)
    except Exception as e:
        print("Error converting to MP3:", e) 