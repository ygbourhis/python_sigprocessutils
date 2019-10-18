# Signal processing utilities for audio

This is an audio research project.

Provided is a script to downsample 32 bits audio files to 16 or even 8 bits,
but instead of simply truncating to a lower bit definition, the LSB is pulse
width modulated by error integration, so that after DAC conversion we still
get a resolution higher to the number of bits.
The issue is that we generate noise with an LSB amplitude which sounds like
correlated white noise. However this noise has only an LSB peak to peak
amplitude which is really low
(inaudible on 16 bits, comparable to an analog tape hiss on 8 bits).
In Theory you get an extra bit depth at SF/4 (SF = Sampling Frequency), and an
extra bit depth every time you divide the frequency by 2.
So in Theory with 44.1 KHz recording with a 32 bits source downsampled to
16 bits, you have 16 bits precision at 22 KHz, 17 bits at 11 Khz, 18 bits at
5.5 Khz, etc... If I'm not mistaken (still needs to be benched).

The goal is to adapt high definition recordings to CD and to keep the max
possible resolution on the CD.
In Theory dither does the same, so this lib would be useless.
However this could allows reducing the dither level
(so the noise) and keep the precision (still needs to be benched).
The goal is to see if it's useless or if it does really add precision.

# TODO:
* Add unittest
* Add dither to decorrelate the noise.
* Add 24 bits support
* Add frequency downsampling (ex: 96 KHz -> 44.1 KHz)

# Install:

first install virtualenvwrapper:
* https://virtualenvwrapper.readthedocs.io/en/latest/install.html

Then:

    mkvirtualenv --python=/usr/bin/python3 python_sigprocessutils
    git clone git@github.com:ygbourhis/python_sigprocessutils.git
    cd python_sigprocessutils
    pip install -Ur requirements.txt
    pip install -e .

Before using in a shell do not forget to activate the virtualenv:

    workon python_sigprocessutils

# Script usage:

    audio_down_sample -i input_file.wav -o output_file.wav -b 16

Or:

    audio_down_sample -i input_file.wav -o output_file.wav -b 8

Or:

    audio_down_sample -i input_file.wav -o output_file.wav -b 8 --verbose

# Library usage examples to downsample a Wave file with python code:

    faded = wave.open("Alan_Walker_-_Faded.wav")
    downsample = wave.open("downsample_integrated.wav", "w")
    downsample.setparams((2, 1, 44100, 0, 'NONE', 'not compressed'))

    integrator_r = Integrator()
    integrator_l = Integrator()
    downsample_l = DownSamplingLSBIntegration(integrator_l)
    downsample_r = DownSamplingLSBIntegration(integrator_r)

    nb_frames = faded.getnframes()
    for i in range(nb_frames):
        paked_input = faded.readframes(1)
        input_g, input_d = struct.unpack('<hh', paked_input)
        output_g = downsample_l.transfert(input_g/256) + 128
        output_d = downsample_r.transfert(input_d/256) + 128
        print(input_g, ':', output_g, '|', input_d, ':', output_d)
        packed_output_g = struct.pack('B', output_g)
        packed_output_d = struct.pack('B', output_d)
        downsample.writeframes(packed_output_g)
        downsample.writeframes(packed_output_d)

OR:

    for i in range(nb_frames):
        paked_input = faded.readframes(1)
        input_g, input_d = struct.unpack('<hh', paked_input)
        output_g = downsample_l.transfert(input_g/256) + 128
        output_d = downsample_r.transfert(input_d/256) + 128
        print(input_g, ':', output_g, '|', input_d, ':', output_d)
        packed_output = struct.pack('<BB', output_g, output_d)
        downsample.writeframesraw(packed_output)

OR:

    downsample.setnframes(2)
    for i in range(nb_frames):
        paked_input = faded.readframes(1)
        input_g, input_d = struct.unpack('<hh', paked_input)
        output_g = downsample_l.transfert(input_g/256) + 128
        output_d = downsample_r.transfert(input_d/256) + 128
        print(input_g, ':', output_g, '|', input_d, ':', output_d)
        packed_output = struct.pack('<BB', output_g, output_d)
        downsample.writeframes(packed_output)

    downsample.close()
    faded.close()

# Useful Links:

* http://www.bravegnu.org/blog/python-wave.html
* https://github.com/sole/snippets/blob/master/audio/generate_noise_test_python/script.py
* http://soledadpenades.com/2009/10/29/fastest-way-to-generate-wav-files-in-python-using-the-wave-module/
* https://soledadpenades.com/posts/2009/fastest-way-to-generate-wav-files-in-python-using-the-wave-module/
* http://fsincere.free.fr/isn/python/cours_python_ch9.php
* https://www.cameronmacleod.com/blog/reading-wave-python
