#!/usr/bin/env python3
"""
Quick test script to verify alarm sound works
"""
import pygame
import numpy as np
import time

print("Testing alarm sound system...")
print("Initializing pygame mixer...")

pygame.mixer.init()

# Generate a beep sound
sample_rate = 22050
frequency = 440  # A4 note
duration = 2  # seconds

print(f"Generating {frequency}Hz beep for {duration} seconds...")

samples = int(sample_rate * duration)
wave = np.sin(2 * np.pi * frequency * np.linspace(0, duration, samples))

# Convert to 16-bit integer
wave = (wave * 32767).astype(np.int16)

# Create stereo sound
stereo_wave = np.column_stack((wave, wave))

# Play sound
print("Playing sound...")
sound = pygame.sndarray.make_sound(stereo_wave)
sound.play()
pygame.time.wait(duration * 1000)

print("✅ Sound test completed successfully!")
