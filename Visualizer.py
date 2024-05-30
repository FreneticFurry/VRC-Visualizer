import psutil
import time
import os
import traceback
import sounddevice as sd
import numpy as np
from pythonosc import udp_client
import threading

client = udp_client.SimpleUDPClient("127.0.0.1", 9000)

print("~{Simple Audio Visualizer By: Frenetic Furry!}~") # if you decide to edit this code &/ or redist i just kindly ask to be credited somewheres in it :3
print("ty for using &/ or even supporting <3")

class AudioVisualizer:
    def __init__(self):
        # Settings!
        self.visual = "_" # this is what is used as a visual for well... visualizing audio
        self.client = udp_client.SimpleUDPClient("127.0.0.1", 9000) # VRChat OSC port (but maybe you wanna change it to something else for other reasons)
        self.smooth = 0.8 # smoothness of the visualizer :D
        self.audiothreshold = 0.2 # this determines the audio threshold (recommended values from 0-1 anything more or lower is unnecessary imo)
        self.micinput = "CABLE Output (VB-Audio Virtual Cable)" # rename this! it only accepts MIC inputs afaik because i cannot figure out any methods of getting output devices :P
        self.previous_values = [1 + i for i in range(10)] # change range(10) to determine how many visualizer connections (recommended 10 and below due to vrchats size limit!)
        self.previous_freq_values = [] # not a setting...
        # end of la settings :P

    def find_device_id(self, micinput):
        mics = sd.query_devices()
        for i, device in enumerate(mics):
            if device["name"] == micinput:
                return i
        return None

    def callback(self, indata, frames, time, status):
        if status:
            print(f"Error: {status}")
            return

        freq_spectrum = np.fft.fft(indata.flatten())
        freq_magnitudes = np.abs(freq_spectrum)

        self.freq_buffer = self.smooth * np.max(freq_magnitudes) + (1 - self.smooth) * getattr(self, "freq_buffer", 0)

        result = self.freq_buffer * self.audiothreshold
        normalized_result = np.clip(result / 0.99, 0.00, 0.99)
        bar_length = int(np.ceil(np.max(normalized_result) * 50))
        bar = self.visual * bar_length

        freq_value = round(np.max(normalized_result), 2)
        self.client.send_message("/avatar/parameters/LowHighF", freq_value)

        for i, prev_value in enumerate(self.previous_values):
            param_name = f"/avatar/parameters/LowHighF{i + 1}"
            if len(self.previous_freq_values) >= prev_value:
                self.client.send_message(param_name, round(self.previous_freq_values[-prev_value], 2))

        self.previous_freq_values.append(freq_value)
        self.previous_freq_values = self.previous_freq_values[-max(self.previous_values):]

        print(bar.ljust(50), end='\r', flush=True)

    def audio_visualizer(self):
        try:
            device_id = self.find_device_id(self.micinput)

            if device_id is not None:
                with sd.InputStream(device=device_id, channels=1, callback=self.callback, samplerate=10000):
                    sd.sleep(-1)
            else:
                print(f"Error: either '{self.micinput}' doesnt exist or '{self.micinput}' cannot be found! please ensure the name is exact & is a mic input.")
        except Exception as emongus:
            print("!!!", emongus, traceback.format_exc())

try:
    if __name__ == "__main__":
        visualizer = AudioVisualizer()
        visualizer.audio_visualizer()

except Exception as emongus:
    print("!!!", emongus, traceback.format_exc())

# made to be easily readable for new users that might be looking to make python code! sometimes learning is by editing and seeing what does what :D
