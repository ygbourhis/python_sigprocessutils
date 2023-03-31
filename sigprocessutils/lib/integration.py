from __future__ import division
import logging

LOG = logging.getLogger(__name__)

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
    to what the LSB can give (sort of an automatic dither except that the
    noise will be correlated).
    """

    offset = 0
    rounded_offset = 0
    coef = 1
    output = None
    min = None
    max = None

    def __init__(self, integrator=None, offset=0, coef=1, min_value=None, max_value=None):
        self.offset = offset
        self.rounded_offset = int(round(self.offset))
        self.coef = coef
        self.output = self.rounded_offset
        if integrator:
            self.integrator = integrator
        else:
            self.integrator = Integrator(-self.offset, self.offset)
        self.set_min_max(min_value, max_value)

    def transfer(self, value):
        self.output = int(round(
            self.integrator.integrate(
                (value * self.coef) - self.output
            )
        ))
        if self.min is not None and self.min > self.output:
            LOG.warning("Low Clipping during integration : %s", self.output)
            self.output = self.min
        elif self.max is not None and self.max < self.output:
            LOG.warning("High Clipping during integration : %s", self.output)
            self.output = self.max
        return self.output

    def reset(self, offset=None, coef=None):
        if offset is not None:
            self.offset = offset
            self.rounded_offset = int(round(self.offset))
        if coef is not None:
            self.coef = coef
        self.output = self.rounded_offset
        self.integrator.reset(-self.offset, self.offset)

    def set_min_max(self, min_value=None, max_value=None):
        self.min = min_value
        self.max = max_value
