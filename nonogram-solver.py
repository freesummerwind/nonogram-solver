from string import whitespace

"""
colors: r b
lines:
2b 1r 1b
1b 1r

2b
3r
columns:
2b 1r
1b 1b 1r
2r 1b 1r
1b 1b
"""


class Nonogram(object):

    def __init__(self, colors, lines_matrix, columns_matrix):
        self.__colors = colors
        self.__lines = lines_matrix
        self.__columns = columns_matrix
        self.__check_correctness()

    def __check_correctness(self):
        line_len = len(self.__columns)
        for line in self.__lines:
            if min_len(line) > line_len:
                raise Exception('Incorrect input: line is longer, than can be')
        column_len = len(self.__lines)
        for column in self.__columns:
            if min_len(column) > column_len:
                raise Exception('Incorrect input: column is longer, than can be')


def min_len(line):
    minimum_len = 0
    for index in range(len(line)):
        if index == 0:
            minimum_len += line[index][1]
        else:
            minimum_len += line[index][1] + 1 if line[index][0] == line[index - 1][0] else line[index][1]
    return minimum_len


def line_transformer(line, colors):
    words_in_line = line.split()
    elements = []
    if len(words_in_line) > 0:
        for word in words_in_line:
            index = 0
            for letter in word:
                if letter.isdigit():
                    index += 1
                else:
                    break
            if index >= len(word) or word[index:] not in colors:
                raise Exception('Incorrect input: no such color \'{0}\''.format(word[index:]))
            elements.append((word[index:], int(word[:index])))
    return elements


def file_reader(path_to_file):
    colors = []
    lines = []
    columns = []
    colors_filled = False
    lines_filled = False
    with open(path_to_file) as file:
        for line in file:
            line = line.strip(whitespace)
            if not colors_filled:
                if len(line) < 9 or line[:8] != 'colors: ':
                    raise Exception('Incorrect input: no colors')
                colors = line[8:].split()
                colors_filled = True
            elif not lines_filled:
                if line == 'lines:':
                    continue
                elif line == 'columns:':
                    lines_filled = True
                else:
                    lines.append(line_transformer(line, colors))
            else:
                columns.append(line_transformer(line, colors))
    return Nonogram(colors, lines, columns)
