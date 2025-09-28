import pygame
import math
import colorsys
import pyaudio 
import numpy as np
import threading
import time

class SoundReactiveSphere:
    def __init__(self):
        pygame.init()
        
        self.width, self.height = 800, 600
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Sound-Reactive Rainbow Sphere")
        
        self.center_x, self.center_y = self.width // 2, self.height // 2
        self.base_radius = 100
        self.radius = self.base_radius
        
        self.hue = 0.0
        self.volume = 0.0
        self.beat_detected = False
        
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Audio setup
        self.chunk = 1024
        self.sample_rate = 44100
        self.p = pyaudio.PyAudio()
        
        try:
            self.stream = self.p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk
            )
            self.audio_active = True
            print("🎤 Microphone connected! Make some noise!")
        except:
            print("⚠️  No microphone found - running in visual-only mode")
            self.audio_active = False
        
        # Start audio processing thread
        if self.audio_active:
            self.audio_thread = threading.Thread(target=self.process_audio)
            self.audio_thread.daemon = True
            self.audio_thread.start()
    
    def process_audio(self):
        volume_history = []
        
        while self.running:
            try:
                data = self.stream.read(self.chunk, exception_on_overflow=False)
                audio_data = np.frombuffer(data, dtype=np.int16)
                
                # Calculate volume (RMS) with safety checks
                if len(audio_data) > 0:
                    mean_square = np.mean(audio_data.astype(np.float64)**2)
                    if mean_square >= 0 and not np.isnan(mean_square):
                        rms = np.sqrt(mean_square)
                        self.volume = min(rms / 3000.0, 1.0)  # Normalize to 0-1
                    else:
                        self.volume = 0.0
                else:
                    self.volume = 0.0
                
                # Beat detection - simple version
                volume_history.append(self.volume)
                if len(volume_history) > 10:
                    volume_history.pop(0)
                
                if len(volume_history) > 5:
                    recent_avg = np.mean(volume_history[-3:])
                    older_avg = np.mean(volume_history[:-3])
                    
                    if recent_avg > older_avg * 1.5 and self.volume > 0.3:
                        self.beat_detected = True
                    else:
                        self.beat_detected = False
                
            except:
                pass
            
            time.sleep(0.01)
    
    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            
            self.update()
            self.draw()
            self.clock.tick(60)
        
        self.cleanup()
    
    def update(self):
        # Time-based animation
        time_factor = pygame.time.get_ticks() / 1000.0
        
        if self.audio_active:
            # Sound-reactive radius with safety checks
            volume_pulse = max(0, min(self.volume * 100, 100))  # Clamp between 0-100
            beat_boost = 50 if self.beat_detected else 0
            base_pulse = 20 * math.sin(time_factor * 2)
            
            # Ensure I never get NaN values
            if np.isnan(volume_pulse) or np.isinf(volume_pulse):
                volume_pulse = 0
            
            self.radius = int(self.base_radius + volume_pulse + beat_boost + base_pulse)
            
            # Sound-reactive color speed with safety
            color_speed = 1 + max(0, min(self.volume * 5, 10))  # Clamp between 1-11
            if np.isnan(color_speed) or np.isinf(color_speed):
                color_speed = 1
                
            self.hue = (self.hue + color_speed) % 360
            
            # Beat detection affects color
            if self.beat_detected:
                self.hue = (self.hue + 30) % 360  # Jump hue on beat
        else:
            # Fallback animation without sound
            self.radius = int(self.base_radius + 20 * math.sin(time_factor * 2))
            self.hue = (self.hue + 2) % 360
    
    def draw(self):
        self.screen.fill((0, 0, 0))
        
        # Convert HSV to RGB
        if self.audio_active and self.beat_detected:
            # Brighter, more saturated on beats
            saturation = 1.0
            value = 1.0
        else:
            saturation = 0.8
            value = 0.9
        
        r, g, b = colorsys.hsv_to_rgb(self.hue / 360.0, saturation, value)
        color = [int(r * 255), int(g * 255), int(b * 255)]
        
        # Draw main sphere
        pygame.draw.circle(self.screen, color, (self.center_x, self.center_y), self.radius)
        
        # Draw volume indicator rings
        if self.audio_active and self.volume > 0.1:
            ring_radius = self.radius + 20
            ring_thickness = max(1, int(self.volume * 10))
            pygame.draw.circle(self.screen, color, (self.center_x, self.center_y), ring_radius, ring_thickness)
        
        # Draw beat flash
        if self.audio_active and self.beat_detected:
            flash_radius = self.radius + 40
            flash_color = [255, 255, 255]  # White flash
            pygame.draw.circle(self.screen, flash_color, (self.center_x, self.center_y), flash_radius, 5)
        
        # Draw volume meter
        if self.audio_active:
            meter_height = int(self.volume * 200)
            meter_rect = pygame.Rect(50, self.height - 50 - meter_height, 20, meter_height)
            pygame.draw.rect(self.screen, color, meter_rect)
            
            # Meter border
            border_rect = pygame.Rect(50, self.height - 250, 20, 200)
            pygame.draw.rect(self.screen, (100, 100, 100), border_rect, 2)
        
        pygame.display.flip()
    
    def cleanup(self):
        if self.audio_active:
            self.stream.stop_stream()
            self.stream.close()
            self.p.terminate()
        pygame.quit()

if __name__ == "__main__":
    sphere = SoundReactiveSphere()
    sphere.run()
