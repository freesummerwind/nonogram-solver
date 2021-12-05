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
