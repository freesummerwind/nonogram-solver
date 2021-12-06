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
            if min_len(self.__lines[i]) == len(self.__columns):
                self.__fill_line(i)
            else:
                queue.append(('l', i))
        for i in range(len(self.__columns)):
            if min_len(self.__columns[i]) == len(self.__lines):
                self.__fill_column(i)
            else:
                queue.append(('c', i))
        while queue:
            current = queue.popleft()
            changed = self.__solve_line(current[1]) if current[0] == 'l' else self.__solve_column(current[1])
            queue.extend(changed)
        return self.__solution

    def __fill_line(self, line_number):
        filled = 0
        for index in range(len(self.__lines[line_number])):
            if index > 0 and self.__lines[line_number][index - 1][0] == self.__lines[line_number][index][0]:
                self.__solution[line_number][filled] = '-'
                filled += 1
            for i in range(self.__lines[line_number][index][1]):
                self.__solution[line_number][filled + i] = self.__lines[line_number][index][0]
            filled += self.__lines[line_number][index][1]

    def __fill_column(self, column_number):
        filled = 0
        for index in range(len(self.__columns[column_number])):
            if index > 0 and self.__columns[column_number][index - 1][0] == self.__columns[column_number][index][0]:
                self.__solution[filled][column_number] = '-'
                filled += 1
            for i in range(self.__columns[column_number][index][1]):
                self.__solution[filled + i][column_number] = self.__columns[column_number][index][0]
            filled += self.__columns[column_number][index][1]

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
