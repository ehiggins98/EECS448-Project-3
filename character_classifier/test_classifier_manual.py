import classifier
import numpy as np
import context
import re
import cv2 as cv

mappings = {
    '0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, 'A': 10, 'B': 11, 'C': 12, 'D': 13, 'E': 14,
    'F': 15, 'G': 16, 'H': 17, 'I': 18, 'J': 19, 'K': 20, 'L': 21, 'M': 22, 'N': 23, 'O': 24, 'P': 25, 'Q': 26, 'R': 27,
    'S': 28, 'T': 29, 'U': 30, 'V': 31, 'W': 32, 'X': 33, 'Y': 34, 'Z': 35, 'a': 36, 'b': 37, 'c': 38, 'd': 39, 'e': 40,
    'f': 41, 'g': 42, 'h': 43, 'i': 44, 'j': 45, 'k': 46, 'l': 47, 'm': 48, 'n': 49, 'o': 50, 'p': 51, 'q': 52, 'r': 53,
    's': 54, 't': 55, 'u': 56, 'v': 57, 'w': 58, 'x': 59, 'y': 60, 'z': 61, ':': 62, ';': 63, '<': 64, '=': 65, '>': 66,
    '?': 67, '!': 68, '"': 69, '%': 70, '&': 71, '\'': 72, '(': 73, ')': 74, '*': 75, '+': 76, ',': 77, '-': 78, '.': 79,
    '/': 80, '[': 81, ']': 82, '^': 83, '{': 84, '|': 85, '}': 86, '#': 87, '$': 88, '_': 89, '`': 90, '@': 91, '\\': 92
}

def encode(char):
    return mappings[char]

def list_from_regex(regex_str):
    print(regex_str)
    regex = re.compile(regex_str)
    result = []
    for c in mappings.keys():
        if regex.match(c):
            result.append(mappings[c])

    return result

def decode(index):
    for k, v in mappings.items():
        if v == index: return k

classifier = classifier.Model()
parser = context.Scope({})

data = np.load('test_images_balanced.npy')
labels = np.load('test_labels_balanced.npy')
print('Ready!')
while True:
    char = input()
    if char == "": break
    char = encode(char)
    indices = np.where(labels == char)[0]

    indices = np.reshape(indices, (-1))
    index = np.random.choice(indices, size=1)
    img = data[index]
    img = np.reshape(img, (32, 32, 1))

    cv.imshow('test', img)
    cv.waitKey(1000)

    probabilities = classifier.predict(img)
    valid = parser.get_valid_characters()
    valid = list_from_regex(valid)

    # this is a vector of probabilities including only the syntactically-valid characters at this point in the code
    valid_prob = np.take(probabilities, valid)
    char = valid[np.argmax(valid_prob)]
    char = decode(char)
    parser.put_character(char)
    print("Got:", char)
print(parser.to_string())
