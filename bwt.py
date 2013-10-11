#!/usr/bin/env python
"""
    bwt.py
    ==============
    Kevin Tee
    Anthony Sutardja

    10/10/2013
"""
import string
import sys

from collections import Counter, namedtuple
from argparse import ArgumentParser

CHARACTER_SET = '$' + string.uppercase + string.lowercase  # order matters


CharPair = namedtuple('CharPair', ['ch', 'idx'])


def read_file(file_name):
    """Reads a given file_name"""
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
            if len(line):
                text += line
    sequences.append(text)
    return sequences


def write_file(file_name, sequence, bwt):
    """Writes to a given file_name"""
    if bwt:
        first_line = '>BWT'
    else:
        first_line = '>iBWT'

    lines = [first_line]
    for i in range(1 + (len(sequence) - 1) // 80):
        lines.append(sequence[i * 80:(i + 1) * 80])

    f = open(file_name, 'w')
    f.write('\n'.join(lines) + '\n')


def radix_sort(lists, pos, max_value, n=3, magic=None):
    """
    Multipurpose radix sort. The radix sort switches it's use case depnding on
    whether n=3 or n=2.

    If n=3, then we are sorting the regular triples in DC3 of R1 and R2.
    If n=2, then we are sorting R0 and the next index's rank.

    Args:
    lists     - sequence of of R1+R2 or R0
    pos       - the position we are sorting at
    max_value - the maximum value of the alphabet. (i.e. [0,n])

    Returns:
    The list sorted.
    """

    for idx in range(n):
        final_sorted = []
        sorted_values = {}
        pos = n - 1 - idx

        for value in lists:
            # for r0 magic
            if n == 2:
                if pos == 0:
                    if value[pos].ch not in sorted_values:
                        sorted_values[value[pos].ch] = []
                    sorted_values[value[pos].ch].append(value)
                else:
                    if value[pos] not in magic:
                        if 0 not in sorted_values:
                            sorted_values[0] = []
                        sorted_values[0].append(value)
                    else:
                        if magic[value[pos]] not in sorted_values:
                            sorted_values[magic[value[pos]]] = []
                        sorted_values[magic[value[pos]]].append(value)
            # for sorting r1+r2
            else:
                if value[pos].ch not in sorted_values:
                    sorted_values[value[pos].ch] = []
                sorted_values[value[pos].ch].append(value)

        for i in range(max_value + 1):
            if i in sorted_values:
                final_sorted += [v for v in sorted_values[i]]

        lists = final_sorted

    return final_sorted


def create_new_labels(sorted_array):
    """
    Given the sorted array of sequences, find a unique set of labels.
    This will eliminate duplicates.

    Args:
    sorted_array  -   an array of tuple sequences

    Returns:
    A dictionary with mappings for the new array
    """
    current_value = 1
    current_seq = None
    labels = {}
    for seq in sorted_array:
        seq = tuple((c.ch for c in seq))
        if seq == current_seq:
            labels[seq] = current_value
        else:
            current_seq = seq
            current_value = current_value + 1
            labels[seq] = current_value
    return labels


def character_to_integer(character):
    """
    Args:
    character - a string character

    Returns:
    Ordinal number with offset
    """
    if type(character) is int:
        return character
    if character is '$':
        return 1
    if character >= 'A' and character <= 'Z':
        return ord(character) - 64 + 1
    return ord(character) - 70 + 1


def create_r_n(n, text):
    """
    Create a triples sequence for R0, R1, and R2 depending on n. This will pad
    the sequences with zeros if necessary.

    Args:
    n    - the number n in {0,1,2} for the sequence R_n we are intereted in
    text - the original text sequence
    """
    if len(text[n:]) % 3 == 0:
        num_expand = 0
    else:
        num_expand = 3 - (len(text[n:]) % 3)
    s = text[n:] + [CharPair(0, len(text[n:]) + i) for i in range(num_expand)]
    r_n = []
    idx = 0
    while idx < len(s):
        r_n.append((s[idx], s[idx + 1], s[idx + 2]))
        idx += 3
    return r_n


def bwt_wrap(text):
    """
    Wrapper function to kickstart the KS algorithm.
    Args:
        text - the string that we wish to process through KS and BWT

    Returns:
        The encoded BWT string.
    """
    text_list = [character_to_integer(ch) for ch in text]
    suffix_array = k_s(text_list, len(CHARACTER_SET))
    return bwt(text, suffix_array)


def print_seq(r):
    """
    Used for debugging a sequence. Prints the sequence.
    """
    s = ''
    for seq in r:
        s += '['
        for c in seq:
            s += ' ' + str(c.ch)
        s += ' ]'
    return s


def k_s(text, ch_set_length):
    """
    Our implementation of the DC3 algorithm.

    Returns:
    Suffix array
    """
    # We pair every character with an index.
    text = [CharPair(text[i], i) for i in range(len(text))]
    # Create r_0, r_1, r_2, append '$$$'
    r_0, r_1, r_2 = [], [], []

    r_0 = create_r_n(0, text)
    r_1 = create_r_n(1, text)
    r_2 = create_r_n(2, text)

    r_pr = r_1 + r_2

    r_pr_sorted = radix_sort(r_pr, 0, ch_set_length + 1)
    r_pr_ranks = {}

    labels = create_new_labels(r_pr_sorted)

    for i, seq in enumerate(r_pr_sorted):
        r_pr_ranks[seq[0]] = i

    new_r_pr = []
    for i, seq in enumerate(r_pr):
        seq = tuple((c.ch for c in seq))
        new_r_pr.append(labels[seq])

    if len(labels.keys()) != len(r_pr_sorted):
        # recurse..
        r_pr_suffix_array = k_s(new_r_pr, len(labels.keys()))
        r_pr_ranks = {}
        r_pr_sorted = []
        for rank, suffix_index in enumerate(r_pr_suffix_array):
            triple = r_pr[suffix_index]  # will yield a character not triple.
            ch = r_pr[suffix_index][0]  # will yield a character not triple.
            r_pr_ranks[ch] = rank
            r_pr_sorted.append(triple)

    r_0_sorted = radix_sort(r_0, 0, max(ch_set_length + 1, len(r_1) + len(r_2)), n=2, magic=r_pr_ranks)

    # at this stage, r_0_sorted and r_pr_sorted are perfectly sorted

    sorted_array = []
    i, j = 0, 0  # Positions in r_0, r
    while i < len(r_0_sorted) and j < len(r_pr_sorted):
        r0_triple = r_0_sorted[i]
        rpr_triple = r_pr_sorted[j]
        if r0_triple[0].ch > rpr_triple[0].ch:
            sorted_array.append(rpr_triple[0])
            j += 1
        elif r0_triple[0].ch < rpr_triple[0].ch:
            sorted_array.append(r0_triple[0])
            i += 1
        # must mean they are equal -> move to next character
        elif rpr_triple[0].idx % 3 == 1:
            if r_pr_ranks[r0_triple[1]] > r_pr_ranks[rpr_triple[1]]:
                sorted_array.append(rpr_triple[0])
                j += 1
            else:
                sorted_array.append(r0_triple[0])
                i += 1
        elif rpr_triple[0].idx % 3 == 2:
            if r0_triple[1].ch > rpr_triple[1].ch:
                sorted_array.append(rpr_triple[0])
                j += 1
            elif r0_triple[1].ch < rpr_triple[1].ch:
                sorted_array.append(r0_triple[0])
                i += 1
            else:
                if r_pr_ranks[r0_triple[2]] > r_pr_ranks[rpr_triple[2]]:
                    sorted_array.append(rpr_triple[0])
                    j += 1
                else:
                    sorted_array.append(r0_triple[0])
                    i += 1

    # Append the rest of r_0 if there is any left
    while i < len(r_0_sorted):
        sorted_array.append(r_0_sorted[i][0])
        i += 1

    # Append the rest of r if there is any left
    while j < len(r_pr_sorted):
        sorted_array.append(r_pr_sorted[j][0])
        j += 1

    return [pair.idx for pair in sorted_array]


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
    Finds the inverse BWT of a BWT-encoded string with forward mapping.

    Args:
    bwt_text - the BWT string no newline characters

    Returns:
    The decoded string.

    >>> ibwt("arbbr$aa")
    'barbara$'
    """
    first_column = sort_characters(bwt_text)
    M = first_occurrence_factory(first_column)
    N = last_occurrence_list_factory(bwt_text)
    original_str = ''

    idx = 0
    # find the row where the $ sign is in the last column
    while bwt_text[idx] != '$':
        idx += 1

    while first_column[idx] != '$':
        original_str += first_column[idx]
        number_of_ch = idx - M[first_column[idx]] + 1
        idx = N[first_column[idx]][number_of_ch - 1]
    original_str += first_column[idx]
    return original_str


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


def last_occurrence_list_factory(last_column):
    """
    Args:
    last_column  - A string that is the BWT

    Returns:
    A dictionary where a character is the key to a list of positions in which
    that character occurs in the last column.
    """
    N = dict()
    for idx, ch in enumerate(last_column):
        if ch not in N:
            N[ch] = []
        N[ch].append(idx)
    return N


def first_occurrence_factory(first_column):
    """
    Args:
    first_column    - A string containing the first column of the BWT matrix

    Returns:
    A dictionary where a character is the key to the first position in
    first_column where that character appears.
    """
    M = dict()
    for idx, ch in enumerate(first_column):
        if ch not in M:
            M[ch] = idx
    return M


def main():
    parser = ArgumentParser(description='Burrows-Wheeler transform')

    direction = parser.add_mutually_exclusive_group(required=True)
    direction.add_argument('-bwt', action='store_true',
                           help='Burrows-Wheeler transform')
    direction.add_argument('-ibwt', action='store_true',
                           help='inverse Burrows-Wheeler transform')

    parser.add_argument('input_file', type=str, metavar='input',
                        help='the input file')
    parser.add_argument('output_file', type=str, metavar='output',
                        help='the output file')

    args = parser.parse_args()

    sequences = read_file(args.input_file)
    input_seq = sequences[1]

    if args.bwt:
        output_seq = bwt_wrap(input_seq)
    else:
        output_seq = ibwt(input_seq)

    write_file(args.output_file, output_seq, args.bwt)

if __name__ == '__main__':
    main()
