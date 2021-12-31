from string import whitespace


def no_other_colors(line, current, length, color):
    for i in range(length):
        if line[current + i] != color and line[current + i] != '.':
            return False
    return True


class Nonogram(object):

    def __init__(self, colors, lines_info, columns_info):
        self.__nonogram = [['.' for _ in range(len(columns_info))] for __ in range(len(lines_info))]
        self.__lines_info = lines_info
        self.__columns_info = columns_info
        self.__line_was_changed = [True for _ in range(len(lines_info))]
        self.__column_was_changed = [True for _ in range(len(columns_info))]
        self.__colors = colors
        self.__can_be_colored = [[set(colors + ['-']) for _ in range(len(columns_info))]
                                 for __ in range(len(lines_info))]
        self.__evaluated_line = []
        self.__evaluated_positions = []

    def __solve_line(self, line, start, blocks_info, current_block):
        flag = False
        if len(blocks_info) == 0:
            if no_other_colors(line, start, len(line) - start, '-'):
                flag = True
                for i in range(start, len(line)):
                    self.__evaluated_line[i].add('-')
        else:
            for i in range(start, len(line) - blocks_info[0][1] + 1):
                if not no_other_colors(line, start, i - start, '-'):
                    break
                next_block_same_colored = len(blocks_info) != 1 and blocks_info[0][0] == blocks_info[1][0]
                if self.__evaluated_positions[i][current_block] is None:
                    if no_other_colors(line, i, blocks_info[0][1], blocks_info[0][0]) \
                            and (i == len(line) - blocks_info[0][1] or not next_block_same_colored
                                 or no_other_colors(line, i + blocks_info[0][1], 1, '-')) \
                            and self.__solve_line(line, i + blocks_info[0][1] + int(next_block_same_colored),
                                                  blocks_info[1:], current_block + 1):
                        self.__evaluated_positions[i][current_block] = True
                    else:
                        self.__evaluated_positions[i][current_block] = False
                if self.__evaluated_positions[i][current_block]:
                    flag = True
                    for j in range(start, i + blocks_info[0][1] + int(i < len(line) - blocks_info[0][1]
                                                                      and next_block_same_colored)):
                        if i <= j < i + blocks_info[0][1]:
                            self.__evaluated_line[j].add(blocks_info[0][0])
                        else:
                            self.__evaluated_line[j].add('-')
        return flag

    def solve(self):
        was_changed = True
        while was_changed:
            was_changed = False
            for j in range(len(self.__lines_info)):  # lines
                if self.__line_was_changed[j]:
                    self.__line_was_changed[j] = False
                    line = self.__nonogram[j]
                    self.__evaluated_line = [set() for _ in range(len(line))]
                    self.__evaluated_positions = [[None for _ in range(len(self.__lines_info[j]))]
                                                  for __ in range(len(line))]
                    self.__solve_line(line, 0, self.__lines_info[j], 0)
                    for i in range(len(line)):
                        old_number_of_colors = len(self.__can_be_colored[j][i])
                        self.__can_be_colored[j][i] &= self.__evaluated_line[i]
                        if len(self.__can_be_colored[j][i]) == 0:
                            raise ValueError('Error1')
                        elif len(self.__can_be_colored[j][i]) == 1 and self.__nonogram[j][i] == '.':
                            self.__nonogram[j][i] = list(self.__can_be_colored[j][i])[0]
                        if old_number_of_colors != len(self.__can_be_colored[j][i]):
                            self.__line_was_changed[j] = True
                            self.__column_was_changed[i] = True
                            was_changed = True
            for j in range(len(self.__columns_info)):  # columns
                if self.__column_was_changed[j]:
                    self.__column_was_changed[j] = False
                    column = [self.__nonogram[i][j] for i in range(len(self.__nonogram))]
                    self.__evaluated_line = [set() for _ in range(len(column))]
                    self.__evaluated_positions = [[None for _ in range(len(self.__columns_info[j]))]
                                                  for __ in range(len(column))]
                    self.__solve_line(column, 0, self.__columns_info[j], 0)
                    for i in range(len(column)):
                        old_number_of_colors = len(self.__can_be_colored[i][j])
                        self.__can_be_colored[i][j] &= self.__evaluated_line[i]
                        if len(self.__can_be_colored[i][j]) == 0:
                            raise ValueError('Error2')
                        elif len(self.__can_be_colored[i][j]) == 1 and self.__nonogram[i][j] == '.':
                            self.__nonogram[i][j] = list(self.__can_be_colored[i][j])[0]
                        if old_number_of_colors != len(self.__can_be_colored[i][j]):
                            self.__line_was_changed[i] = True
                            self.__column_was_changed[j] = True
                            was_changed = True

    def __str__(self):
        result = ''
        max_color_len = 0
        for color in self.__colors:
            max_color_len = len(color) if len(color) > max_color_len else max_color_len
        formatting = '{' + f':^{max_color_len}' + '}'
        for line in self.__nonogram:
            for i in range(len(line)):
                if i > 0:
                    result += ' '
                result += formatting.format(line[i])
            result += '\n'
        return result


def line_transformer(line, colors, counter):
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
                raise Exception('Incorrect input: no such color \'' + word[index:] + '\'')
            counter[word[index:]] += int(word[:index])
            elements.append((word[index:], int(word[:index])))
    return elements


def file_reader(path_to_file):
    colors = []
    lines = []
    columns = []
    colors_in_lines = {}
    colors_in_columns = {}
    colors_filled = False
    lines_filled = False
    with open(path_to_file) as file:
        for line in file:
            line = line.strip(whitespace)
            if not colors_filled:
                if len(line) < 9 or line[:8] != 'colors: ':
                    raise Exception('Incorrect input: no colors')
                colors = line[8:].split()
                for color in colors:
                    colors_in_lines[color] = 0
                    colors_in_columns[color] = 0
                colors_filled = True
            elif not lines_filled:
                if line == 'lines:':
                    continue
                elif line == 'columns:':
                    lines_filled = True
                else:
                    lines.append(line_transformer(line, colors, colors_in_lines))
            else:
                columns.append(line_transformer(line, colors, colors_in_columns))
    flag = True
    incorrect_colors = []
    for color in colors:
        if colors_in_lines[color] != colors_in_columns[color]:
            flag = False
            incorrect_colors.append(color)
    if not flag:
        message = "Incorrect colors in nonogram:\n"
        for color in incorrect_colors:
            message += color + ": in lines " + str(colors_in_lines[color]) + ", in columns " \
                       + str(colors_in_columns[color]) + '\n'
        raise Exception(message)
    return Nonogram(colors, lines, columns)
