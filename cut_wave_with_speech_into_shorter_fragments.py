#!/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy as np
from vad_sohn import vad
from fbe_vad_sohn import fbe, load_wav
from noise_tracking_hendriks import NoiseTracking

class CutIntoShorterFragments:

    def __init__(self, sampling_rate : int = 16000, min_fragment_length : int = 7, max_fragment_length : int = 20, min_silence_length_in_frames : int = 3, frame : int = 320):

        self.sampling_rate = sampling_rate
        self.min_fragment_length = min_fragment_length
        self.max_fragment_length = max_fragment_length
        self.min_silence_length_in_frames
        self.frame = frame
        self.v = vad(frame=self.frame)
        self.nt = NoiseTracking(frame=self.frame)
        self.noisy_fbe = fbe(frame=self.frame)

    def get_fragments(input_samples : np.ndarray):

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

            noise_psd = self.nd.get_noise_psd()

            if self.v.vad(noise_psd) < 0.5:

                silent_frame = True

                fragment_length += self.frame/self.sampling_rate

            else:

                silent_frame = False

            if not silence_flag and silent_frame:

                silence_flag = True

                silence_beginning = start

            if silence_flag and not silent_frame:

                silen_flag = False

                silence_end = start

                last_silence = (silence_beginning, silence_end)

                # compute cut point

                if (last_silence[1] - last_silence[0])//self.frame >= self.min_silence_length_in_frames:

                    cut_point = (last_silence[1]+last_silence[0])//self.frame

                if fragment_length >= self.min_fragment_length:

                    fragment = input_samples[prev_cut_point:cut_point]

                    print(f"created fragment length {len(fragment)}")

                    output_list_of_fragments.append(fragment)

                    prev_cut_point = cut_point

                    fragment_length = 0

        return output_list_of_fragments

if __name__ == "__main__":

   speech, sr, target_sampling_rate = load_wav('German_Wikipedia_Otto_Hahn_audio_48kHz.wav')

   print(f"sampling rate {sr}")
