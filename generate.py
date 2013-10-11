#!/usr/bin/env python
import string
import random

from argparse import ArgumentParser

CHARACTER_SET = string.uppercase + string.lowercase


def generate_random_sequence(length):
    ret = ''
    for i in range(int(length)):
        ret += CHARACTER_SET[random.randint(0, len(CHARACTER_SET)-1)]
    ret += '$'
    return ret


def write_file(file_name, sequence):
    first_line = '>Sample'

    lines = [first_line]
    for i in range(1 + (len(sequence) - 1) // 80):
        lines.append(sequence[i * 80:(i + 1) * 80])

    f = open(file_name, 'w')
    f.write('\n'.join(lines) + '\n')


def main():
    parser = ArgumentParser(description='Random input generator')

    parser.add_argument('text_length', type=str, metavar='length',
                        help='Number of characters to be used')
    parser.add_argument('output_file', type=str, metavar='output',
                        help='the output file')

    args = parser.parse_args()
    output_seq = generate_random_sequence(args.text_length)

    write_file(args.output_file, output_seq)

if __name__ == '__main__':
    main()
