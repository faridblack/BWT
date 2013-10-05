import string
import sys

def read_file(file_name):
    # Open file
    f = open(file_name, 'r')
    text = ''

    # Ignore first line and strip newline character
    for i,line in enumerate(f):
        if i > 0:
            text += line[:-1]
    return text

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
        final_sorted += radix_sort(sorted_strings[character],pos+1)

    return final_sorted

def k_s(text):
    # Create r_0 and r_1_2, append '$$$'
    r_0,r_1_2 = [],[]
    text += '$$$'

    # Fill r_0 and r_1_2
    for i in range(len(text)-3):
        if i % 3 == 0:
            r_0.append(text[i] + text[i+1] + text[i+2])
        else:
            r_1_2.append(text[i] + text[i+1] + text[i+2])

    # Sort r_1_2
    sorted_array = radix_sort(r_1_2,0)
    print sorted_array
    print len(r_1_2), len(sorted_array)

def bwt():
    pass

def ibwt():
    pass

def main():
    if len(sys.argv) < 4:
        exit('3 Arguments required')
    encode_type = sys.argv[1]
    input_file = sys.argv[2]
    output_file = sys.argv[3]

    # Read Text File
    text = read_file(input_file)

    # Run K-S Algorithm to generate suffix array
    suffix_array = k_s(text)

if __name__ == '__main__':
    main()
