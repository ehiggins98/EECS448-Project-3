import context
import classifier
import textdetection as td

import re
from flask import Flask, request
from werkzeug.utils import secure_filename
import numpy as np
import cv2
import math
import test_context

import subprocess


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

similar = {
    '0': 'oO', '1': 'Ili!', '2': 'Zz', '3': '}', '4': '', '5': 'sS', '6': 'G', '7': 'T', 'c': 'C<', 'C': 'c<', 'o': 'O0', 'O': 'o0', 'i': ';!',
    ';': 'i!', '!': ';i', 'x': '*', '*': 'x'
}

def encode(char):
    return mappings[char]

def list_from_regex(regex_str):
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
    data = request.files['file']
    data = data.read()
    file_bytes = np.asarray(bytearray(data), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    cv2.imwrite('testFile.jpg', img)
    # returns [n, 32, 32] matrix of images
    char_images = textdetection.execute(img)
    cv2.imwrite('testFile2.jpg', char_images[0])
    print(np.shape(char_images))
    #returns [n, 93] matrix of probabilities
    probabilities = classifier.predict(char_images)

    for index in range(0, len(char_images)):
        c_img = char_images[index]
        if np.max(c_img) == 0 or math.isnan(np.max(c_img)):
            parser.put_character('\n')
        else:
            valid = list_from_regex(parser.get_valid_characters())
            valid_prob = np.take(probabilities[index], valid)
            prob2 = find_probs(index, 1, probabilities)
            prob3 = find_probs(index, 2, probabilities)
            prob4 = find_probs(index, 3, probabilities)
            char = lookahead(parser, probabilities[index], prob2, prob3, prob4)

            print(index, char)
            cv2.imwrite('test' + str(index) + '.jpg', (np.reshape(c_img, (32, 32, 1)) + 0.13147026078678872) * 255)
            parser.put_character(char)
    return parser.to_string()

def find_probs(start, offset, probabilities):
    count = 0
    for i in range(start + 1, np.shape(probabilities)[0]):
        if not all(np.isnan(probabilities[i])) and not all(probabilities[i] == 0):
            count += 1
        if count == offset:
            return probabilities[i]
    return []

def aggregate(probabilities, chars):
    final = 1

    for p, c in zip(probabilities, chars):
        p = sum_similar(p, c)
        if p > 0.65:
            final *= p * 1000
        elif p < 5e-5:
            final *= p * 1e-3
        else:
            final *= p
    return final

def sum_similar(probabilities, character):
    result = probabilities[encode(character)]
    if character in similar:
        for c in similar[character]:
            result += probabilities[encode(c)]
    return result

def lookahead(context, prob1, prob2, prob3, prob4):
    max = 0
    argmax = 0
    greatest_n_elem = 10
    valid1 = list_from_regex(context.get_valid_characters())
    valid_prob1 = np.take(prob1, valid1)
    greatest_n1 = range(0, len(valid_prob1)) if len(valid_prob1) < greatest_n_elem else np.argpartition(valid_prob1, -greatest_n_elem)[-greatest_n_elem:]
    valid1 = np.take(valid1, greatest_n1)
    valid_prob1 = np.take(valid_prob1, greatest_n1)
    print(valid1)
    if not len(prob2): prob2 = [1]
    if not len(prob3): prob3 = [1]
    if not len(prob4): prob4 = [1]

    for i1, p1 in enumerate(valid_prob1):
        working1 = context.clone()
        working1.put_character(decode(valid1[i1]))
        try:
            valid2 = list_from_regex(working1.get_valid_characters())
        except:
            print(decode(valid1[i1]))
            raise IndexError('uhh')
        valid_prob2 = np.take(prob2, valid2)
        greatest_n2 = range(0, len(valid_prob2)) if len(valid_prob2) < greatest_n_elem else np.argpartition(valid_prob2, -greatest_n_elem)[-greatest_n_elem:]
        valid2 = np.take(valid2, greatest_n2)
        valid_prob2 = np.take(valid_prob2, greatest_n2)
        for i2, p2 in enumerate(valid_prob2):
            if aggregate([prob1, prob2], [decode(valid1[i1]), decode(valid2[i2])]) > max:
                max = aggregate([prob1, prob2], [decode(valid1[i1]), decode(valid2[i2])])
                argmax = decode(valid1[i1])
    return argmax

@app.route('/', methods=['GET'])
def runTests():
    result = subprocess.check_output(['python3', 'test_context.py'], stderr=subprocess.STDOUT)
    return(result)
