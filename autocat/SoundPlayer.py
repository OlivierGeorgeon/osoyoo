import pyglet

SOUND_STARTUP = 'R5.wav'
SOUND_CLEAR = 'R3.wav'
SOUND_NEAR_HOME = 'R4.wav'
SOUND_PUSH = 'tiny_cute.wav'
SOUND_MESSAGE = 'chirp.wav'
SOUND_FLOOR = 'cyberpunk3.wav'
SOUND_IMPACT = 'cute_beep1.wav'
SOUND_SURPRISE = 'chirp3.mp3'


class SoundPlayer:
    _initialized = 0
    _sounds = {}

    @classmethod
    def initialize(cls):
        """Load all the sounds"""
        if not cls._initialized:
            # Try to load sounds (it may not work on all platforms)
            try:
                cls._sounds[SOUND_STARTUP] = pyglet.media.load(f'autocat/Assets/{SOUND_STARTUP}', streaming=False)
                cls._sounds[SOUND_CLEAR] = pyglet.media.load(f'autocat/Assets/{SOUND_CLEAR}', streaming=False)
                cls._sounds[SOUND_NEAR_HOME] = pyglet.media.load(f'autocat/Assets/{SOUND_NEAR_HOME}', streaming=False)
                cls._sounds[SOUND_PUSH] = pyglet.media.load(f'autocat/Assets/{SOUND_PUSH}', streaming=False)
                cls._sounds[SOUND_MESSAGE] = pyglet.media.load(f'autocat/Assets/{SOUND_MESSAGE}', streaming=False)
                cls._sounds[SOUND_FLOOR] = pyglet.media.load(f'autocat/Assets/{SOUND_FLOOR}', streaming=False)
                cls._sounds[SOUND_IMPACT] = pyglet.media.load(f'autocat/Assets/{SOUND_IMPACT}', streaming=False)
                cls._sounds[SOUND_SURPRISE] = pyglet.media.load(f'autocat/Assets/{SOUND_SURPRISE}', streaming=False)
                cls._initialized = 2
            except pyglet.media.codecs.wave.WAVEDecodeException as e:
                print("Error loading sound files", e)
                cls._initialized = 1

    @classmethod
    def play(cls, name):
        """Play the sound"""
        if cls._initialized == 0:
            cls.initialize()
        if cls._initialized == 2:
            cls._sounds.get(name).play()

    # @classmethod
    # def load_sound(cls, name, filepath):
    #     if not cls._initialized:
    #         cls.initialize()
    #     if not os.path.exists(filepath):
    #         raise FileNotFoundError(f"Sound file {filepath} not found")
    #     cls._sounds[name] = pygame.mixer.Sound(filepath)

    # @classmethod
    # def stop_sound(cls, name):
    #     if not cls._initialized:
    #         cls.initialize()
    #     sound = cls._sounds.get(name)
    #     if sound:
    #         sound.stop()
    #     else:
    #         raise ValueError(f"Sound {name} not loaded")


# # Example usage:
# if __name__ == "__main__":
#     SoundPlayer.initialize()
#     SoundPlayer.play(SOUND_STARTUP)
