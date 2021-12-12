import argparse
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


class InfoBlock(object):
    def __init__(self, length, color):
        self.length = length
        self.color = color
        self.is_painted = False


class InfoLine(object):
    def __init__(self):
        self.__blocks = []
        self.is_full = False

    def __len__(self):
        return len(self.__blocks)

    def __check_fullness(self):
        fullness = True
        for block in self.__blocks:
            fullness = fullness and block.is_painted
        self.is_full = fullness

    def add_block(self, block):
        self.__blocks.append(block)

    def paint_block(self, block_number):
        if not self.__blocks[block_number].is_painted:
            self.__blocks[block_number].is_painted = True
            self.__check_fullness()

    def get_block(self, block_number):
        return self.__blocks[block_number]


def fill(current_line, info_line):
    length = len(current_line)
    left_line = [['.', 0] for _ in range(length)]
    right_line = [['.', 0] for _ in range(length)]
    blocks_number = len(info_line)
    current_left = 0
    current_right = 0
    for i in range(blocks_number):
        if i > 0:
            if info_line.get_block(i - 1).color == info_line.get_block(i).color:
                left_line[current_left] = ['-', 1]
                current_left += 1
            if info_line.get_block(blocks_number - i).color == info_line.get_block(blocks_number - i - 1).color:
                right_line[length - current_right - 1] = ['-', -1]
                current_right += 1
        for j in range(info_line.get_block(i).length):
            left_line[current_left + j] = [info_line.get_block(i).color, i]
        for k in range(info_line.get_block(blocks_number - i - 1).length):
            right_line[length - current_right - 1 - k] = [info_line.get_block(blocks_number - i - 1).color,
                                                          blocks_number - i - 1]
        current_left += info_line.get_block(i).length
        current_right += info_line.get_block(blocks_number - i - 1).length
    changed = False
    if current_left == length:
        for i in range(len(info_line)):
            info_line.paint_block(i)
        for i in range(length):
            current_line[i] = left_line[i][0]
            changed = True
    else:
        for i in range(length):
            if left_line[i] == right_line[i] and left_line[i][0] != '.' and current_line[i] == '.':
                current_line[i] = left_line[i][0]
                changed = True
    return changed


def repulsion_from_walls(current_line, info_line):
    changed = False
    flag_left = False
    length_left = 0
    for i in range(info_line.get_block(0).length):
        if flag_left:
            length_left += 1
            if current_line[i] == '.':
                current_line[i] = info_line.get_block(0).color
                changed = True
        elif current_line[i] == info_line.get_block(0).color:
            flag_left = True
            length_left += 1
    if length_left == info_line.get_block(0).length:
        info_line.paint_block(0)
        if len(info_line) > 1 and info_line.get_block(0).color == info_line.get_block(1).color \
                and current_line[length_left] != '-':
            current_line[length_left] = '-'
            changed = True
    flag_right = False
    length_right = 0
    for i in range(info_line.get_block(-1).length):
        if flag_right:
            length_right += 1
            if current_line[len(current_line) - i - 1] == '.':
                current_line[len(current_line) - i - 1] = info_line.get_block(-1).color
                changed = True
        elif current_line[len(current_line) - i - 1] == info_line.get_block(-1).color:
            flag_right = True
            length_right += 1
    if length_right == info_line.get_block(-1).length:
        info_line.paint_block(-1)
        if len(info_line) > 1 and info_line.get_block(len(info_line) - 2).color == info_line.get_block(-1).color \
                and current_line[len(current_line) - length_right - 1] != '-':
            current_line[len(current_line) - length_right - 1] = '-'
            changed = True
    return changed


def empties_from_walls(current_line, info_line):
    if info_line.is_full:
        return False
    current_empties = 0
    current_block = 0
    last_space = 0
    changed = False
    index = 0
    while index < len(current_line):
        if current_line[index] == '.':
            current_empties += 1
            index += 1
        elif current_line[index] == '-' and current_empties < info_line.get_block(current_block).length:
            for j in range(last_space, index):
                if current_line[j] != '-':
                    current_line[j] = '-'
                    changed = True
            last_space = index
            current_empties = 0
            index += 1
        elif current_line[index] != '-' and info_line.get_block(current_block).is_painted:
            for j in range(last_space, index):
                if current_line[j] == '.':
                    current_line[j] = '-'
                    changed = True
            index += info_line.get_block(current_block).length
            current_block += 1
            current_empties = 0
            last_space = index
        else:
            break
    current_empties = 0
    current_block = len(info_line) - 1
    last_space = len(current_line)
    index = len(current_line) - 1
    while index > -1:
        if current_line[index] == '.':
            current_empties += 1
            index -= 1
        elif current_line[index] == '-' and current_empties < info_line.get_block(current_block).length:
            for j in range(index, last_space):
                if current_line[j] != '-':
                    current_line[j] = '-'
                    changed = True
            last_space = index
            current_empties = 0
            index -= 1
        elif current_line[index] != '-' and info_line.get_block(current_block).is_painted:
            for j in range(index, last_space):
                if current_line[j] == '.':
                    current_line[j] = '-'
                    changed = True
            index -= info_line.get_block(current_block).length
            current_block -= 1
            current_empties = 0
            last_space = index + 1
        else:
            break
    return changed


def solve_line(current_line, info_line):
    changed = False
    changed = fill(current_line, info_line) or changed
    changed = repulsion_from_walls(current_line, info_line) or changed
    changed = empties_from_walls(current_line, info_line) or changed
    return changed


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
        solution_changed = True
        while solution_changed:
            solution_changed = False
            for i in range(len(self.__lines)):
                if self.__solve_line(i):
                    solution_changed = True
            for i in range(len(self.__columns)):
                if self.__solve_column(i):
                    solution_changed = True
        return self.__solution

    def __solve_line(self, line_number):
        if self.__lines[line_number].is_full:
            return False
        current_line = self.__solution[line_number]
        left, right = 0, len(current_line) - 1
        for i in range(len(current_line)):
            if current_line[i] != '-':
                left = i
                break
        for i in range(len(current_line) - 1, -1, -1):
            if current_line[i] != '-':
                right = i
                break
        current_line = current_line[left:right + 1]
        was_changed = solve_line(current_line, self.__lines[line_number])
        for i in range(left, right + 1):
            self.__solution[line_number][i] = current_line[i - left]
        return was_changed

    def __solve_column(self, column_number):
        if self.__columns[column_number].is_full:
            return False
        current_column = [self.__solution[i][column_number] for i in range(len(self.__lines))]
        up, down = 0, len(current_column) - 1
        for i in range(len(current_column)):
            if current_column[i] != '-':
                up = i
                break
        for i in range(len(current_column) - 1, -1, -1):
            if current_column[i] != '-':
                down = i
                break
        current_column = current_column[up:down + 1]
        was_changed = solve_line(current_column, self.__columns[column_number])
        for i in range(up, down + 1):
            self.__solution[i][column_number] = current_column[i - up]
        return was_changed


def min_len(line):
    minimum_len = 0
    for index in range(len(line)):
        if index == 0:
            minimum_len += line.get_block(index).length
        else:
            minimum_len += line.get_block(index).length + 1 \
                if line.get_block(index).color == line.get_block(index - 1).color else line.get_block(index).length
    return minimum_len


def line_transformer(line, colors):
    words_in_line = line.split()
    info_line = InfoLine()
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
            info_line.add_block(InfoBlock(int(word[:index]), word[index:]))
    return info_line


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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Files for input and output')
    parser.add_argument('input_file', type=str, help='name of file with numbers')
    parser.add_argument('-s', type=str, default=None, help='name of file with result')
    arguments = parser.parse_args()
    nonogram = file_reader(arguments.input_file)
    solution = nonogram.solve()
    if arguments.s is None:
        for line in solution:
            print(*line)
    else:
        with open(arguments.s, 'w') as f_out:
            for line in solution:
                f_out.write(' '.join(line) + '\n')
