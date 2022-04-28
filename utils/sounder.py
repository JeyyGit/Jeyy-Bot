from glob import glob
from io import BytesIO
from pathlib import Path
from pydub import AudioSegment
from jishaku.functools import executor_function

paths = [(p, Path(p).name.split('.')) for p in glob('./audio/sounder/*')]
audios = {name: AudioSegment.from_file(path, fmt) for path, (name, fmt) in paths}
audios['delay'] = AudioSegment.silent(500)

class Sounder:
	def __init__(self):
		self.sound = None
		self.position = 0
		self.sounds = []

	@executor_function
	def init(self):
		self.sound = AudioSegment.silent(15000)

	@executor_function
	def append_sound(self, sound, times=1, octaves=0):
		audio = audios[sound]

		if octaves:
			octaves *= 0.1

			new_sample_rate = int(audio.frame_rate * (2.0 ** octaves))
			audio = audio._spawn(audio.raw_data, overrides={'frame_rate': new_sample_rate})

		self.sound = self.sound.overlay(audio, self.position*500, times=times)
		self.position += times
		self.sounds.append(sound)

	@executor_function
	def add_multiple(self, *sounds):
		audio = [audios.get(sound) for sound in sounds]

		for a in audio:
			self.sound.overlay(a, self.position*500)

		self.position += 1
		self.sounds.append(sounds)

	@executor_function
	def export(self):
		self.remove_leading_silence()

		buf = BytesIO()
		self.sound.export(buf, 'mp3')
		return buf
	
	def detect_leading_silence(self, sound):
		trim_ms = 0
		silence_threshold = -30.0
		chunk_size = 10

		assert chunk_size > 0
		while sound[trim_ms:trim_ms+chunk_size].dBFS < silence_threshold and trim_ms < len(sound):
			trim_ms += chunk_size

		return trim_ms

	def remove_leading_silence(self):
		ends = self.detect_leading_silence(self.sound.reverse())
		self.sound = self.sound[:ends+500]

	def count_sound(self):
		return self.position - 1
		
		


		
			
			