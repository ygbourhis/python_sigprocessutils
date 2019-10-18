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
