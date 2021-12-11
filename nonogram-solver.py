from collections import deque
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


def fill(info_line, length):
    left_line = [['.', 0] for _ in range(length)]
    right_line = [['.', 0] for _ in range(length)]
    filled = ['.' for _ in range(length)]
    blocks_number = len(info_line)
    current_left = 0
    current_right = 0
    for i in range(blocks_number):
        if i > 0:
            if info_line[i - 1][0] == info_line[i][0]:
                left_line[current_left] = ['-', 1]
                current_left += 1
            if info_line[blocks_number - i][0] == info_line[blocks_number - i - 1][0]:
                right_line[length - current_right - 1] = ['-', -1]
                current_right += 1
        for j in range(info_line[i][1]):
            left_line[current_left + j] = [info_line[i][0], i]
        for k in range(info_line[blocks_number - i - 1][1]):
            right_line[length - current_right - 1 - k] = [info_line[blocks_number - i - 1][0], blocks_number - i - 1]
        current_left += info_line[i][1]
        current_right += info_line[blocks_number - i - 1][1]
    if current_left == length:
        for i in range(length):
            filled[i] = left_line[i][0]
    else:
        for i in range(length):
            if left_line[i] == right_line[i]:
                filled[i] = left_line[i][0]
    return filled


class Nonogram(object):

    def __init__(self, colors, lines_matrix, columns_matrix):
        self.__colors = colors
        self.__lines = lines_matrix
        self.__columns = columns_matrix
        self.__solution = [['.' for _ in range(len(self.__columns))] for _ in range(len(self.__lines))]
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

    def solve(self):
        queue = deque()
        for i in range(len(self.__lines)):
            self.__fill_line(i)
            if min_len(self.__lines[i]) != len(self.__columns):
                queue.append(('l', i))
        for i in range(len(self.__columns)):
            self.__fill_column(i)
            if min_len(self.__columns[i]) != len(self.__lines):
                queue.append(('c', i))
        while queue:
            current = queue.popleft()
            changed = self.__solve_line(current[1]) if current[0] == 'l' else self.__solve_column(current[1])
            queue.extend(changed)
        return self.__solution

    def __fill_line(self, line_number):
        filled_line = fill(self.__lines[line_number], len(self.__columns))
        for i in range(len(self.__columns)):
            if filled_line[i] != '.':
                self.__solution[line_number][i] = filled_line[i]

    def __fill_column(self, column_number):
        filled_column = fill(self.__columns[column_number], len(self.__lines))
        for i in range(len(self.__lines)):
            if filled_column[i] != '.':
                self.__solution[i][column_number] = filled_column[i]

    def __solve_line(self, line_number):
        changed_columns = []
        # solving methods
        return changed_columns

    def __solve_column(self, column_number):
        changed_lines = []
        # solving methods
        return changed_lines


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
