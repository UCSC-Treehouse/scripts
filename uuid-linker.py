#!/usr/bin/env python2.7

import argparse
import os
import string
import uuid

from itertools import izip_longest

alphabet = string.ascii_uppercase


# https://stackoverflow.com/questions/16789776/iterating-over-two-values-of-a-list-at-a-time-in-python
def grouper(iterable, chunk, fillvalue=None):
    args = [iter(iterable)] * chunk
    return izip_longest(*args, fillvalue=fillvalue)


def main():
    """
    Takes a tab separated list of paired fastq paths and creates a hard-link using a randomly generated uuid.

    Paths file format:
    f1_1.fq.gz  f1_2.fq.gz
    f2_1.fq.gz  f2_2.fq.gz  f3_1.fq.gz  f3_2.fq.gz

    Files on the same line will share a UUID. Use this feature when there are multiple fastq files for the same sample.
    ...
    """
    parser = argparse.ArgumentParser(description=main.__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--paths',
                        dest='paths',
                        required=True,
                        type=argparse.FileType('r'),
                        help='File containing tab separated list of paired file paths.')

    parser.add_argument('--ext',
                        dest='ext',
                        required=True,
                        help='Extension for the uuid filename.')

    parser.add_argument('--output_dir',
                        required=True,
                        help='Output directory')

    args = parser.parse_args()

    if not os.path.exists(args.output_dir):
        raise ValueError('Output directory does not exist!')

    if not args.ext.startswith('.'):
        args.ext = '.' + args.ext

    log_path = args.paths.name + '.map'

    with open(log_path, 'w') as f:
        f.write('File1\tUUID1\tFile2\tUUID2\n')
        for i, line in enumerate(args.paths):

            files = line.strip().split('\t')

            if len(files) % 2 != 0:
                msg = 'ERROR: Number of files per line must be a multiple of 2. ' \
                      'Ensure input file is tab delimited.'
                raise ValueError(msg)

            # Keep track of replicate samples
            replicate = None

            if len(files) > 2:
                replicate = 0

            new_id = uuid.uuid4()

            for r1, r2 in grouper(files, 2, None):
                # If files don't exist, then skip line
                if not os.path.exists(r1) or not os.path.exists(r2):
                    print 'WARNING: Cannot locate files on line %d!' % i
                    break


                if replicate is not None:
                    replicate_tag = '-%s' % alphabet[replicate]
                    replicate += 1

                else:
                    replicate_tag = ''

                new_r1 = '%s%s_1%s' % (new_id,
                                       replicate_tag,
                                       args.ext)

                new_r1_path = os.path.abspath(os.path.join(args.output_dir, new_r1))
                os.link(r1, new_r1_path)

                new_r2 = '%s%s_2%s' % (new_id,
                                       replicate_tag,
                                       args.ext)

                new_r2_path = os.path.abspath(os.path.join(args.output_dir, new_r2))
                os.link(r2, new_r2_path)

                f.write('%s\t%s\n' % (r1, new_r1_path))
                f.write('%s\t%s\n' % (r2, new_r2_path))


if __name__ == '__main__':
    main()
