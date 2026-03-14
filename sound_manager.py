# sound_manager.py — Simple sound effect manager using pygame's built-in sound generation

import pygame
import math
import numpy as np

class SoundManager:
    """
    Simple procedural sound effect manager.
    Generates basic sound effects without requiring external audio files.
    """
    def __init__(self, enabled=True):
        self.enabled = enabled
        self.volume = 0.8
        self.sounds = {}
        if enabled:
            try:
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=2048)
                self._generate_sounds()
            except:
                self.enabled = False
                print("Sound system not available, running in silent mode")
    
    def _generate_tone(self, frequency, duration, volume=0.5):
        """Generate a simple sine wave tone"""
        if not self.enabled:
            return None
        try:
            sample_rate = 44100
            n_samples = int(duration * sample_rate)
            t = np.linspace(0, duration, n_samples, False)
            
            # Generate sine wave with envelope
            wave = np.sin(2 * np.pi * frequency * t)
            envelope = np.exp(-3 * t / duration)  # Decay envelope
            wave = wave * envelope * volume * 32767
            
            # Stereo
            stereo_wave = np.column_stack((wave, wave)).astype(np.int16)
            return pygame.sndarray.make_sound(stereo_wave)
        except:
            return None
    
    def _generate_noise(self, duration, volume=0.3):
        """Generate white noise burst for impacts"""
        if not self.enabled:
            return None
        try:
            sample_rate = 44100
            n_samples = int(duration * sample_rate)
            t = np.linspace(0, duration, n_samples, False)
            
            # White noise with decay
            noise = np.random.uniform(-1, 1, n_samples)
            envelope = np.exp(-8 * t / duration)
            wave = noise * envelope * volume * 32767
            
            stereo_wave = np.column_stack((wave, wave)).astype(np.int16)
            return pygame.sndarray.make_sound(stereo_wave)
        except:
            return None
    
    def _generate_sounds(self):
        """Generate all game sound effects"""
        # Jump sound - rising pitch
        self.sounds['jump'] = self._generate_tone(300, 0.15, 0.8)
        
        # Ghost toggle - ethereal sound
        self.sounds['ghost_on'] = self._generate_tone(600, 0.3, 0.7)
        self.sounds['ghost_off'] = self._generate_tone(400, 0.25, 0.7)
        
        # Death - harsh noise
        self.sounds['death'] = self._generate_noise(0.4, 1.0)
        
        # Lever - click sound
        self.sounds['lever'] = self._generate_tone(800, 0.1, 0.8)
        
        # Gate - low rumble
        self.sounds['gate'] = self._generate_tone(100, 0.5, 0.6)
        
        # Plate activated
        self.sounds['plate'] = self._generate_tone(500, 0.2, 0.7)
        
        # Checkpoint
        self.sounds['checkpoint'] = self._generate_tone(700, 0.25, 0.8)
        
        # Exit reached
        self.sounds['exit'] = self._generate_tone(800, 0.4, 0.8)
        
        # Walk sound - short click
        self.sounds['walk'] = self._generate_tone(200, 0.08, 0.6)
        
        # Wall pass - phasing sound
        self.sounds['wall_pass'] = self._generate_tone(400, 0.2, 0.5)
    
    def play(self, sound_name):
        """Play a sound effect"""
        if not self.enabled or sound_name not in self.sounds:
            return
        sound = self.sounds.get(sound_name)
        if sound:
            try:
                sound.set_volume(self.volume)
                sound.play()
            except:
                pass
    
    def set_volume(self, volume):
        """Set global volume (0.0 to 1.0)"""
        self.volume = max(0.0, min(1.0, volume))
    
    def toggle(self):
        """Toggle sound on/off"""
        self.enabled = not self.enabled
        return self.enabled
