from __future__ import division


class Integrator(object):

    offset = 0
    init = None
    output = None

    def __init__(self, offset=0, init=None):
        self.reset(offset, init)

    def integrate(self, value):
        self.output += value - self.offset
        return self.output

    def reset(self, offset=None, init=None):
        if offset is not None:
            self.offset = offset
        if init is not None:
            self.init = init
        else:
            self.init = self.offset

        self.output = self.init


class DownSamplingLSBIntegration(object):
    """Donw sample a floating point signal to integer signal

    The LSB error is integrated in order to modulate the LSB so that the mean
    value of it's modulation reconstructs the lost values which are inferior
    to what the LSB can give (sort of an authomatic dither except that the
    noise will be correlated).
    """

    offset = 0
    rounded_offset = 0
    coef = 1
    output = None

    def __init__(self, integrator=None, offset=0, coef=1):
        self.offset = offset
        self.rounded_offset = int(round(self.offset))
        self.coef = coef
        self.output = self.rounded_offset
        if integrator:
            self.integrator = integrator
        else:
            self.integrator = Integrator(-self.offset, self.offset)

    def transfert(self, value):
        v1 = (value * self.coef) - self.output
        v2 = self.integrator.integrate(v1)
        self.output = int(round(v2))
        return self.output

    def reset(self, offset=None, coef=None):
        if offset is not None:
            self.offset = offset
            self.rounded_offset = int(round(self.offset))
        if coef is not None:
            self.coef = coef
        self.output = self.rounded_offset
        self.integrator.reset(-self.offset, self.offset)

# http://www.bravegnu.org/blog/python-wave.html
# https://github.com/sole/snippets/blob/master/audio/generate_noise_test_python/script.py
# http://soledadpenades.com/2009/10/29/fastest-way-to-generate-wav-files-in-python-using-the-wave-module/
# https://soledadpenades.com/posts/2009/fastest-way-to-generate-wav-files-in-python-using-the-wave-module/
# http://fsincere.free.fr/isn/python/cours_python_ch9.php
# https://www.cameronmacleod.com/blog/reading-wave-python

# faded = wave.open("Alan_Walker_-_Faded.wav")
# downsample = wave.open("downsample_integrated.wav", "w")
# downsample.setparams((2, 1, 44100, 0, 'NONE', 'not compressed'))

# integrator_r = Integrator()
# integrator_l = Integrator()
# downsample_l = DownSamplingLSBIntegration(integrator_l)
# downsample_r = DownSamplingLSBIntegration(integrator_r)

# nb_frames = faded.getnframes()
# for i in xrange(nb_frames):
    # paked_input = faded.readframes(1)
    # input_g, input_d = struct.unpack('<hh', paked_input)
    # output_g = downsample_l.transfert(input_g/256) + 128
    # output_d = downsample_r.transfert(input_d/256) + 128
    # print input_g, ':', output_g, '|', input_d, ':', output_d
    # packed_output_g = struct.pack('B', output_g)
    # packed_output_d = struct.pack('B', output_d)
    # downsample.writeframes(packed_output_g)
    # downsample.writeframes(packed_output_d)

# OR:

# for i in xrange(nb_frames):
    # paked_input = faded.readframes(1)
    # input_g, input_d = struct.unpack('<hh', paked_input)
    # output_g = downsample_l.transfert(input_g/256) + 128
    # output_d = downsample_r.transfert(input_d/256) + 128
    # print input_g, ':', output_g, '|', input_d, ':', output_d
    # packed_output = struct.pack('<BB', output_g, output_d)
    # downsample.writeframesraw(packed_output)

# OR

# downsample.setnframes(2)
# for i in xrange(nb_frames):
    # paked_input = faded.readframes(1)
    # input_g, input_d = struct.unpack('<hh', paked_input)
    # output_g = downsample_l.transfert(input_g/256) + 128
    # output_d = downsample_r.transfert(input_d/256) + 128
    # print input_g, ':', output_g, '|', input_d, ':', output_d
    # packed_output = struct.pack('<BB', output_g, output_d)
    # downsample.writeframes(packed_output)

# downsample.close()
# faded.close()
