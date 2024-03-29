import wave
from struct import pack as struct_pack
from struct import unpack as struct_unpack

# Bit size struct mapping:
# https://docs.python.org/3.6/library/struct.html#format-characters
# https://stackoverflow.com/questions/3783677/how-to-read-integers-from-a-file-that-are-24bit-and-little-endian-using-python
STRUCT_FORMATS = {
    8: 'B',
    16: 'h',
    24: 'i',
    32: 'i',
    64: 'q',
}

SAMPLE_WIDTHS = {
    1: 'B',
    2: 'h',
    3: 'i',
    4: 'i',
}

BITS_WIDTHS = {
    8: 1,
    16: 2,
    24: 3,
    32: 4,
}

WIDTH_BITS = {
    1: 8,
    2: 16,
    3: 24,
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
        if self.sampwidth == 3:  # 24 bits audio
            split_size = len(data) // 3
            datas = [data[i*3:(i+1)*3] for i in range(split_size)]
            for i, d in enumerate(datas):
                datas[i] = d + (b'\x00' if d[2] <= 128 else b'\xff')  # make each 24 bits 32 bits long signed
                # Maybe we could use num = int.from_bytes(d, byteorder='little', signed=True)
                # and then int.to_bytes(num, byteorder='little', signed=True, length=4)
                # In order to convert 24 to 32 bits ?
            reformated_data = b''.join(datas)
            # Maybe we could return the `num` variables instead ?
            return struct_unpack(self.struct_fmt, reformated_data)
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
