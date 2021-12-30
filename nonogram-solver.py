from collections import deque
from string import whitespace


def no_empties(line, current, length):
    for i in range(length):
        if line[current + i] == '-':
            return False
    return True


def no_colored(line, current, length):
    for i in range(length):
        if line[current + i] != '-' and line[current + i] != '.':
            return False
    return True


class Nonogram(object):

    def __init__(self, colors, lines_info, columns_info):
        self.__nonogram = [['.' for _ in range(len(columns_info))] for __ in range(len(lines_info))]
        self.__lines_info = lines_info
        self.__columns_info = columns_info
        self.__colors = colors
        self.__can_be_colored = []
        self.__evaluated_positions = []

    def __solve_line(self, line, start, blocks_info, current_block):
        flag = False
        if len(blocks_info) == 0:
            if no_colored(line, start, len(line) - start):
                flag = True
                for i in range(start, len(line)):
                    self.__can_be_colored[i].add('-')
        else:
            for i in range(start, len(line) - blocks_info[0][1] + 1):
                if not no_colored(line, start, i - start):
                    break
                if self.__evaluated_positions[i][current_block] is None:
                    if no_empties(line, i, blocks_info[0][1]) \
                            and (i == len(line) - blocks_info[0][1] or no_colored(line, i + blocks_info[0][1], 1)) \
                            and self.__solve_line(line, i + blocks_info[0][1] + 1, blocks_info[1:], current_block + 1):
                        self.__evaluated_positions[i][current_block] = True
                    else:
                        self.__evaluated_positions[i][current_block] = False
                if self.__evaluated_positions[i][current_block]:
                    flag = True
                    for j in range(start, i + blocks_info[0][1] + int(i < len(line) - blocks_info[0][1])):
                        if i <= j < i + blocks_info[0][1]:
                            self.__can_be_colored[j].add('b')
                        else:
                            self.__can_be_colored[j].add('-')
        return flag

    def solve(self):
        queue = deque()
        in_queue = set()
        for i in range(len(self.__lines_info)):
            queue.append(('l', i))
            in_queue.add(('l', i))
        for i in range(len(self.__columns_info)):
            queue.append(('c', i))
            in_queue.add(('c', i))
        while queue:
            current_element = queue.popleft()
            in_queue.remove(current_element)
            if current_element[0] == 'l':  # line
                line = self.__nonogram[current_element[1]]
                self.__can_be_colored = [set() for _ in range(len(line))]
                self.__evaluated_positions = [[None for _ in range(len(self.__lines_info[current_element[1]]))]
                                              for __ in range(len(line))]
                self.__solve_line(line, 0, self.__lines_info[current_element[1]], 0)
                for i in range(len(line)):
                    if len(self.__can_be_colored[i]) == 0:
                        raise ValueError('Error')
                    elif len(self.__can_be_colored[i]) == 1 and self.__nonogram[current_element[1]][i] == '.':
                        self.__nonogram[current_element[1]][i] = list(self.__can_be_colored[i])[0]
                        if ('c', i) not in in_queue:
                            queue.append(('c', i))
                            in_queue.add(('c', i))
            elif current_element[0] == 'c':  # column
                column = [self.__nonogram[i][current_element[1]] for i in range(len(self.__nonogram))]
                self.__can_be_colored = [set() for _ in range(len(column))]
                self.__evaluated_positions = [[None for _ in range(len(self.__columns_info[current_element[1]]))]
                                              for __ in range(len(column))]
                self.__solve_line(column, 0, self.__columns_info[current_element[1]], 0)
                for i in range(len(column)):
                    if len(self.__can_be_colored[i]) == 0:
                        raise ValueError('Error')
                    elif len(self.__can_be_colored[i]) == 1 and self.__nonogram[i][current_element[1]] == '.':
                        self.__nonogram[i][current_element[1]] = list(self.__can_be_colored[i])[0]
                        if ('l', i) not in in_queue:
                            queue.append(('l', i))
                            in_queue.add(('l', i))
            else:
                raise ValueError('Error')

    def __str__(self):
        result = ''
        for line in self.__nonogram:
            result += ' '.join(line) + '\n'
        return result


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
