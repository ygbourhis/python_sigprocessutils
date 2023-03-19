import argparse
import logging
import math
import sys

import six

from ..conf.logconf import configure_logging
from ..lib.integration import DownSamplingLSBIntegration, Integrator
from ..lib.wavelib import WaveRead, WaveWrite, BITS_WIDTHS, WIDTH_BITS


def create_argument_parser(parser=None):
    if not parser:
        parser = argparse.ArgumentParser(
            description="Down sample audio wav file."
        )
    parser.add_argument(
        "--verbose", action="store_true",
        help="Make output verbose"
    )
    parser.add_argument(
        "-b", "--bits", type=int, choices=(8, 16), default=16
    )
    parser.add_argument(
        "-i", "--input", required=True
    )
    parser.add_argument(
        "-o", "--output", required=True
    )
    return parser


def main():
    parser = create_argument_parser()
    options = parser.parse_args()
    log_level = 'info'
    if options.verbose:
        log_level = 'debug'
    configure_logging(log_level)
    logger = logging.getLogger(__name__)

    infile = WaveRead(options.input)

    input_bits = WIDTH_BITS[infile.sampwidth]
    logger.debug('Input sample width = %s bits', input_bits)
    logger.debug('Output sample width = %s bits', options.bits)
    input_offset = 0
    if input_bits == 8:
        input_offset = 128
    logger.debug('Input offset = %s', input_offset)

    outfile = WaveWrite(options.output, infile.params)
    outfile.setsampwidth(BITS_WIDTHS[options.bits])

    output_offset = 0
    if options.bits == 8:
        output_offset = 128
    logger.debug('Output offset = %s', output_offset)
    divider = math.pow(2, input_bits) / math.pow(2, options.bits)
    logger.debug('Divider = %s', divider)
    try:

        downsample_chans = [
            DownSamplingLSBIntegration(Integrator())
            for _ in six.moves.xrange(infile.nchannels)
        ]

        last_out_nb_chars = 0
        total_frames = infile.nframes
        for frame_nb in six.moves.xrange(total_frames):  # noqa pylint: disable=W0612
            inputs = infile.read_unpacked_frames(1)
            outputs = tuple(
                integrator.transfert(
                    (inp - input_offset) / divider
                ) + output_offset
                for integrator, inp in zip(downsample_chans, inputs)
            )
            progress_percent = (frame_nb / total_frames) * 100
            out_str = '\rProgression: %3.3f%%' % progress_percent
            if options.verbose:
                out_str += ' | Input: %s -> Output: %s' % (
                    str(inputs), str(outputs)
                )
            str_nb_chars = len(out_str)
            remaining_chars = last_out_nb_chars - str_nb_chars
            if remaining_chars < 0:
                remaining_chars = 0
            out_str += ' ' * remaining_chars
            last_out_nb_chars = sys.stdout.write(out_str)
            sys.stdout.flush()
            outfile.write_packed_frames(outputs)
        sys.stdout.write('\n')
        sys.stdout.flush()

    finally:
        logger.debug('Success')
        infile.close()
        outfile.close()
