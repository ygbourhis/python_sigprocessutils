import wave
from struct import pack as struct_pack
from struct import unpack as struct_unpack

# Bit size struct mapping:
# https://docs.python.org/3.6/library/struct.html#format-characters
STRUCT_FORMATS = {
    8: 'B',
    16: 'h',
    32: 'i',
    64: 'q',
}

SAMPLE_WIDTHS = {
    1: 'B',
    2: 'h',
    4: 'i',
}

BITS_WIDTHS = {
    8: 1,
    16: 2,
    32: 4,
}

WIDTH_BITS = {
    1: 8,
    2: 16,
    4: 32,
}


class WaveMixin(object):
    _filename = None
    _wfp = None

    def __init__(self, filename):
        self._filename = filename

    def close(self):
        self._wfp.close()

    def tell(self):
        return self._wfp.tell()

    @property
    def struct_fmt(self):
        return '<%d%s' % (self.nchannels, SAMPLE_WIDTHS[self.sampwidth])

    @property
    def wfp(self):
        return self._wfp

    @property
    def nchannels(self):
        return self._wfp.getnchannels()

    @property
    def sampwidth(self):
        return self._wfp.getsampwidth()

    @property
    def framerate(self):
        return self._wfp.getframerate()

    @property
    def nframes(self):
        return self._wfp.getnframes()

    @property
    def comptype(self):
        return self._wfp.getcomptype()

    @property
    def compname(self):
        return self._wfp.getcompname()

    @property
    def params(self):
        return self._wfp.getparams()


class WaveRead(WaveMixin):

    def __init__(self, filename):
        super(WaveRead, self).__init__(filename)
        self.open()

    def open(self):
        self._wfp = wave.open(self._filename)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def unpack_data(self, data):
        return struct_unpack(self.struct_fmt, data)

    def readframes(self, n):
        return self._wfp.readframes(n)

    def read_unpacked_frames(self, n):
        return self.unpack_data(self.readframes(n))

    def rewind(self):
        self._wfp.rewind()

    def setpos(self, pos):
        self._wfp.setpos(pos)


class WaveWrite(WaveMixin):

    def __init__(self, filename, params=None):
        super(WaveWrite, self).__init__(filename)
        self.open(params)

    def open(self, params=None):
        self._wfp = wave.open(self._filename, "w")
        if params:
            self.setparams(params)

    def setnchannels(self, n):
        self._wfp.setnchannels(n)

    def setsampwidth(self, n):
        self._wfp.setsampwidth(n)

    def setframerate(self, n):
        self._wfp.setframerate(n)

    def setcomptype(self, comptype, compname):
        self._wfp.setcomptype(comptype, compname)

    def setparams(self, params):
        self._wfp.setparams(params)

    def pack_data(self, *args):
        return struct_pack(self.struct_fmt, *args)

    def writeframesraw(self, data):
        self._wfp.writeframesraw(data)

    def writeframes(self, data):
        self._wfp.writeframes(data)

    def write_packedframes_raw(self, args):
        self.writeframesraw(self.pack_data(*args))

    def write_packed_frames(self, args):
        self.writeframes(self.pack_data(*args))
