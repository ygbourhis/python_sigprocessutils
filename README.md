# Signal processing utilities for audio

Script to downsample 32 bits audio files to 16 or even 8 bits, but instead
of simply truncating to a lower bit definition, the LSB is pulse width
modulated by error integration, so that after DAC conversion we still get a
resolution higher to the number of bits.
The issue is that we generate noise with an LSB amplitude which sounds like
correlated white noise. However this noise been on the LSB it is really low
(inaudible on 16 bits, comparable to an analog tape hiss on 8 bits).


# TODO:
* Add unittest
* Add dither to decorrelate the noise.
* Add 24 bits support
* Add frequency downsampling (ex: 96 KHz -> 44.1 KHz)


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
