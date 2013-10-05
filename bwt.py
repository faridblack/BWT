#!/usr/bin/env python
import string
import sys

from collections import Counter

CHARACTER_SET = '$' + string.uppercase + string.lowercase  # order matters


def read_file(file_name):
    # Open file
    f = open(file_name, 'r')

    text = ''
    sequences = []

    for line in f.readlines():
        line = line.rstrip()
        if line[0] == ">":
            sequences.append(text)
            text = ''
        else:
            text += line
    sequences.append(text)
    return sequences


def radix_sort(strings, pos):
    # Base Case for radix sort
    if pos == 3:
        return strings

    final_sorted = []

    # Create a bucket for each character, in lexicographical order
    sorted_strings = {}
    for character in '$' + string.ascii_lowercase + string.ascii_uppercase:
        sorted_strings[character] = []

    #Place string in correct bucket
    for s in strings:
        sorted_strings[s[pos]].append(s)

    # Recursively sort each bucket
    for character in '$' + string.ascii_lowercase + string.ascii_uppercase:
        final_sorted += radix_sort(sorted_strings[character], pos + 1)

    return final_sorted


def k_s(text):
    # Create r_0 and r_1_2, append '$$$'
    r_0, r_1_2 = [], []
    text += '$$$'

    # Fill r_0 and r_1_2
    for i in range(len(text) - 3):
        if i % 3 == 0:
            r_0.append(text[i] + text[i + 1] + text[i + 2])
        else:
            r_1_2.append(text[i] + text[i + 1] + text[i + 2])

    # Sort r_1_2
    sorted_array = radix_sort(r_1_2, 0)
    print sorted_array
    print len(r_1_2), len(sorted_array)


def bwt(original_text, suffix_array):
    """
    Args:
    original_text  - original string with no newline characters
    suffix_array   - an array of suffix indices listed in lexicographical order
                     assuming the suffixes are indexed starting at ZERO

    Returns:
    An unformatted string that is the corresponding BWT of the suffix array.
    """
    bwt_str = ''
    for suffix_index in suffix_array:
        bwt_str += original_text[suffix_index - 1]
    return bwt_str


def ibwt(bwt_text):
    """
    Args:
    bwt_text - the BWT string no newline characters

    Returns:
    The decoded string.
    """
    # TODO(anthonysutardja): I got dibs on this
    pass


def sort_characters(text):
    """
    Sorts the characters with counting sort to preserve O(n) runtime.

    Args:
    text    - the string we wish to sort

    Returns:
    A string with the characters sorted in lexicographical order.

    >>> sort_characters('anthony')
    'ahnnoty'
    >>> sort_characters('kevin')
    'eiknv'
    >>> sort_characters('aAaAaa')
    'AAaaaa'
    """
    counts = Counter()
    for ch in text:
        counts[ch] += 1

    sorted_text = ''
    for ch in CHARACTER_SET:
        sorted_text += ''.join([ch for i in range(counts[ch])])

    return sorted_text


def main():
    if len(sys.argv) < 4:
        exit('3 Arguments required')
    encode_type = sys.argv[1]
    input_file = sys.argv[2]
    output_file = sys.argv[3]

    # Read Text File
    sequences = read_file(input_file)

    # Assuming there is at least 1 sequence in FASTA file
    text = sequences[0]

    # Run K-S Algorithm to generate suffix array
    suffix_array = k_s(text)

if __name__ == '__main__':
    main()
