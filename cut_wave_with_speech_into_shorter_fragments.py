#!/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy as np
from vad_sohn import vad
from fbe_vad_sohn import fbe, load_wav, save_wav
from noise_tracking_hendriks import NoiseTracking
from typing import List
import matplotlib.pyplot as plt
import sys
import os

class CutIntoShorterFragments:

    """Construtor creating the cutter class object

    :param sampling_rate: sampling rate of the file to process
    :type sampling_rate: int
    :param min_fragment_length: minimal fragment length in seconds
    :type min_fragment_length: int
    :param min_silence_length_in_frames: minimal silence length in frames to allow cutting
    :type min_silence_length_in_frames: int
    :param frame: frame length in samples
    :type frame: int
    """

    def __init__(self, sampling_rate : int = 16000, min_fragment_length : int = 7,  min_silence_length_in_frames : int = 3, frame : int = 320):

        self.sampling_rate = sampling_rate
        self.min_fragment_length = min_fragment_length
        self.min_silence_length_in_frames = min_silence_length_in_frames
        self.frame = frame
        self.v = vad(frame=self.frame)
        self.nt = NoiseTracking(frame=self.frame)
        self.noisy_fbe = fbe(frame=self.frame)
        self.start = True
        self.fragments_ready = False

    def get_fragments(self, input_samples : np.ndarray) -> List[np.ndarray]:
        """Actual method for cutting out short fragments from a long recording

        :param input_samples: samples of the input recording, the samples have to be at sampling_rate, no check provided
        :type input_samples: np.ndarray
        :returns: a list of np.ndarrays containing cutted off fragments
        :rtype: List[np.ndarray]
        """

        start = 0

        output_list_of_fragments = []

        silence_flag = False

        silent_frame = False

        prev_cut_point = 0

        fragment_length = 0

        while start + self.frame < len(input_samples):

            fs = input_samples[start:start+self.frame]

            self.noisy_fbe.set_frm(fs)

            noisy_psd = self.noisy_fbe.psd()

            self.nt.noisePowRunning(noisy_psd)

            noise_psd = self.nt.get_noise_psd()

            sprb = self.v.vad(noisy_psd, noise_psd)

            #  print(f"current frame speech presence probability {sprb}")

            #  plt.plot(fs)
#
            #  plt.show()


            #  input('press enter ...')

            if  sprb < 0.5:

                silent_frame = True

            else:

                silent_frame = False

                fragment_length += self.frame/self.sampling_rate

                #  print(f"current fragment length {fragment_length}")

                #  input('press enter non silent frame found ...')

            if not silence_flag and silent_frame:

                silence_flag = True

                silence_beginning = start

            if silence_flag and not silent_frame:

                silence_flag = False

                silence_end = start

                last_silence = (silence_beginning, silence_end)

                # compute cut point

                if (last_silence[1] - last_silence[0])//self.frame >= self.min_silence_length_in_frames:

                    cut_point = np.uint32(np.round(0.5*(last_silence[1]+last_silence[0])))

                    if self.start:

                        prev_cut_point = cut_point

                        self.start = False

                    if fragment_length >= self.min_fragment_length:

                        fragment = input_samples[prev_cut_point:cut_point]

                        print(f"created fragment length {len(fragment)/self.sampling_rate}")

                        #  plt.plot(fragment)
                        #  plt.show()

                        output_list_of_fragments.append(fragment)

                        prev_cut_point = cut_point

                        fragment_length = 0

            start += self.frame

            #  print(f"start = {start}")

        self.fragments = output_list_of_fragments

        self.fragments_ready = True

        return output_list_of_fragments

    def save_fragments(self, folder : str, name_prefix : str):
        """Saves fragments into files in the folder. The names for the fragments are created according to convention: name_prefix + <consecutive number of the fragment with appropriate number of leading zeros>

        :param folder:
        :type folder: str
        :param name_prefix:
        :type name_prefix: str
        """



        if not self.fragments_ready:

            print(f"WARNING run first the get_fragments method to create fragments")

            sys.exit(1)


        num_of_fragments = len(self.fragments) 

        num_zeros = len(list(str(num_of_fragments)))

        fill_zeros = ''.join(['0']*num_zeros) 

        for i in range(num_of_fragments):

            fragments_num = str(i)

            zeros_fragments_num = list(fill_zeros)

            zeros_fragments_num[-len(fragments_num):] = list(fragments_num)

            zeros_fragments_num_str = ''.join(zeros_fragments_num)

            print(os.path.join(folder, name_prefix+zeros_fragments_num_str +'.wav'))

            save_wav(self.fragments[i], 16000, os.path.join(folder, name_prefix+zeros_fragments_num_str +'.wav'))

if __name__ == "__main__":

    speech, sr, target_sampling_rate = load_wav('German_Wikipedia_Otto_Hahn_audio_16kHz.wav')

    print(f"sampling rate {sr}")

    c = CutIntoShorterFragments(frame=320,min_fragment_length=2, min_silence_length_in_frames=15)

    fragments = c.get_fragments(speech)

    c.save_fragments('./output/','German_Wikipedia_Otto_Hahn_audio_16kHz_num')



