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


def has_duplicates(strings):
    previous_string = None

    for string in strings:
        if string == previous_string:
            return True
        previous_string = string

    return False


def radix_sort(strings, pos):
    # Base Case for radix sort
    if pos == 3:
        return strings

    final_sorted = []

    # Create a bucket for each character, in lexicographical order
    sorted_strings = {}
    for character in CHARACTER_SET:
        sorted_strings[character] = []

    #Place string in correct bucket
    for s in strings:
        sorted_strings[s[pos]].append(s)

    # Recursively sort each bucket
    for character in CHARACTER_SET:
        final_sorted += radix_sort(sorted_strings[character], pos + 1)

    return final_sorted


def integer_radix_sort(integers, pos):
    final_sorted = []

    if pos == 3:
        return integers

    sorted_values = {}
    for i in range(10):
        sorted_values[i] = []

    for integer in integers:
        sorted_values[(integer / (10**(2 - pos))) % 10].append(integer)

    for i in range(10):
        final_sorted += integer_radix_sort(sorted_values[i], pos + 1)

    return final_sorted


def list_radix_sort(lists, pos, max_value):
    final_sorted = []

    if pos == 3:
        return lists

    sorted_values = {}
    for i in range(max_value + 1):
        sorted_values[i] = []

    for value in lists:
        sorted_values[value[pos]].append(value)

    for i in range(max_value + 1):
        final_sorted += list_radix_sort(sorted_values[i], pos + 1, max_value)

    return final_sorted


def create_new_labels(sorted_array):
    current_value = 0
    current_string = None
    labels = {}
    for string in sorted_array:
        if string == current_string:
            labels[string] = current_value
        else:
            current_string = string
            current_value = current_value + 1
            labels[string] = current_value
    return labels


def character_to_integer(character):
    if type(character) is int:
        return character
    if character is '$':
        return 0
    if character >= 'A' and character <= 'Z':
        return ord(character) - 64
    return ord(character) - 70


def k_s(text):
    # Create r_0, r_1, r_2, append '$$$'
    r_0, r_1, r_2 = [], [], []
    text += '$$$'
    positions = {}

    for i in range(len(text) - 3):
        if i % 3 == 0:
            r_0.append([character_to_integer(text[i]), character_to_integer(text[i + 1]), character_to_integer(text[i + 2]), i])
        elif i % 3 == 1:
            r_1.append([character_to_integer(text[i]), character_to_integer(text[i + 1]), character_to_integer(text[i + 2]), i])
        else:
            r_2.append([character_to_integer(text[i]), character_to_integer(text[i + 1]), character_to_integer(text[i + 2]), i])
    r = r_1 + r_2

    r_0 = list_radix_sort(r_0, 0, len(CHARACTER_SET))
    r = list_radix_sort(r, 0, len(CHARACTER_SET))

    for i in range(len(r)):
        positions[r[i][3]] = i

    sorted_array = []
    i, j = 0, 0  # Positions in r_0, r
    while i < len(r_0) and j < len(r):
        '''
        Check which character is larger
        If same, check the next character
        If same, check positions in r (if both % 3 > 0)
        Otherwise, check next positions in r
        '''
        if character_to_integer(text[r_0[i][3]]) > character_to_integer(text[r[j][3]]):
            sorted_array.append(r[j][3])
            j += 1
        elif character_to_integer(text[r_0[i][3]]) < character_to_integer(text[r[j][3]]):
            sorted_array.append(r_0[i][3])
            i += 1
        elif character_to_integer(text[r_0[i][3] + 1]) > character_to_integer(text[r[j][3] + 1]):
            sorted_array.append(r[j][3])
            j += 1
        elif character_to_integer(text[r_0[i][3] + 1]) < character_to_integer(text[r[j][3] + 1]):
            sorted_array.append(r_0[i][3])
            i += 1
        elif (r_0[i][3] + 1) % 3 > 0 and (r[j][3] + 1) % 3 > 0:
            if positions[r_0[i][3] + 1] < positions[r[j][3] + 1]:
                sorted_array.append(r_0[i][3])
                i += 1
            else:
                sorted_array.append(r[j][3])
                j += 1
        elif (r_0[i][3] + 2) % 3 > 0 and (r[j][3] + 2) % 3 > 0:
            if positions[r_0[i][3] + 2] < positions[r[j][3] + 2]:
                sorted_array.append(r_0[i][3])
                i += 1
            else:
                sorted_array.append(r[j][3])
                j += 1

    # Append the rest of r_0 if there is any left
    while i < len(r_0):
        sorted_array.append(r_0[i][3])
        i += 1

    # Append the rest of r if there is any left
    while j < len(r):
        sorted_array.append(r[j][3])
        j += 1

    return sorted_array


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


def bwt_handler(input_str):
    pass


def ibwt_handler(input_str):
    pass


def parse_command(encode_type):
    if token == '-bwt':
        return bwt_handler
    elif token == '-ibwt':
        return ibwt_handler
    raise Exception('Command not recognized. Please use -bwt or -bwt')


def main():
    if len(sys.argv) < 4:
        exit('3 Arguments required')
    encode_type = parse_command(sys.argv[1])
    input_file = sys.argv[2]
    output_file = sys.argv[3]

    # Read Text File
    sequences = read_file(input_file)

    # Assuming there is at least 1 sequence in FASTA file
    text = sequences[1]

    # Run K-S Algorithm to generate suffix array
    suffix_array = k_s(text)

if __name__ == '__main__':
    main()
