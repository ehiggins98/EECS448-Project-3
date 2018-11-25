import context
import classifier
import textdetection as td

import re
from flask import Flask, request
from werkzeug.utils import secure_filename
import numpy as np
import cv2
import math

app = Flask(__name__)
classifier = classifier.Model()
textdetection = td.TextDetection()

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
    if regex_str[0] == '|':
        regex_str = regex_str[1:]

    regex = re.compile(regex_str)
    result = []
    for c in mappings.keys():
        if regex.match(c):
            result.append(mappings[c])
    return result

def decode(index):
    for k, v in mappings.items():
        if v == index: return k

@app.route('/', methods=['POST'])
def process_image():
    parser = context.Scope({})
    data = request.get_data()
    file_bytes = np.asarray(bytearray(data), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

    # returns [n, 32, 32] matrix of images
    char_images = textdetection.execute(img)

    #returns [n, 93] matrix of probabilities
    probabilities = classifier.predict(char_images)

    for index, c_img in enumerate(char_images):
        if np.max(c_img) == 0 or math.isnan(np.max(c_img)):
            parser.put_character('\n')
        else:
            valid = parser.get_valid_characters()
            valid = list_from_regex(valid)

            # this is a vector of probabilities including only the syntactically-valid characters at this point in the code
            valid_prob = np.take(probabilities[index], valid)
            char = valid[np.argmax(valid_prob)]
            char = decode(char)
            cv2.imwrite('test' + str(index) + '.jpg', (np.reshape(c_img, (32, 32, 1))+0.13147026078678872)*255)
            print(index, char)
            parser.put_character(char)
    return parser.to_string()
