import argparse
from copy import deepcopy
from string import whitespace


def no_other_colors(line, current, length, color):
    """
    Функция проверяет, что в линии line начиная с позиции current и до позиции current + length все клетки либо
    еще не были окрашены, либо окрашены цветом color
    :param line: array of strings, представление линии
    :param current: integer, стартовая позиция
    :param length: integer, длина блока, который нужно проверить
    :param color: string, цвет, в который могут быть окрашены клетки
    :return: bool, все ли клетки не окрашены или окрашены нужным цветом
    """
    for i in range(length):
        if line[current + i] != color and line[current + i] != '.':
            return False
    return True


class NonoException(Exception):
    """
    Класс для выброса исключений в нонограмме
    """


class Nonogram(object):

    def __init__(self, colors, lines_info, columns_info):
        """
        self.__nonogram - представление нонограммы, матрица строк N*M. Если клетка заполнена '.', она еще не рассчитана
        self.__lines_info - массив пар (цвет, длина), информация о горизонтальных блоках нонограммы
        self.__columns_info - массив пар (цвет, длина), информация о вертикальных блоках нонограммы
        self.__line_was_changed - массив булевых значений, содержит информацию, были ли изменения в i-й строке
        self.__column_was_changed - массив булевых значений, содержит информацию, были ли изменения в i-м столбце
        self.__colors - массив строк, содержит цвета, которые используются в нонограмме
        self.__can_be_colored - матрица размера N*M, содержит множества цветов, в которые может быть окрашена
        соответствующая клетка
        self.__evaluated_line - массив, который будет пересоздаваться для расчета строки/столбца. Содержит информацию о
        том, в какие цвета может быть окрашена i-я клетка на основе уже полученной информации
        self.__evaluated_positions - матрица, в которой будут запоминаться уже рассчитанные расположения блоков в линии.
        Нужна для уменьшении глубины рекурсии путем сохранения уже рассчитанных значений

        :param colors: array of strings, цвета, используемые в нонограмме
        :param lines_info: array of pairs (string, int), информация о горизонтальных блоках нонограммы
        :param columns_info: array of pairs (string, int), информация о вертикальных блоках нонограммы
        """
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

    def __presolve_line(self, line, possible_colors, blocks_info):
        minimum_length = 0
        for i in range(len(blocks_info)):
            if i > 0 and blocks_info[i][0] == blocks_info[i - 1][0]:
                minimum_length += 1
            minimum_length += blocks_info[i][1]
        if minimum_length == 0:
            for i in range(len(line)):
                line[i] = '-'
                possible_colors[i] = {'-'}
            return
        number_of_free_cells = len(line) - minimum_length
        current = 0
        for i in range(len(blocks_info)):
            if i > 0 and blocks_info[i][0] == blocks_info[i - 1][0]:
                current += 1
            if blocks_info[i][1] > number_of_free_cells:
                for j in range(number_of_free_cells, blocks_info[i][1]):
                    line[current + j] = blocks_info[i][0]
                    possible_colors[current + j] = {blocks_info[i][0]}
            current += blocks_info[i][1]

    def __presolve(self):
        for i in range(len(self.__lines_info)):
            line = self.__nonogram[i]
            possible_colors = self.__can_be_colored[i]
            self.__presolve_line(line, possible_colors, self.__lines_info[i])
        for i in range(len(self.__columns_info)):
            column = [line[i] for line in self.__nonogram]
            possible_colors = [line[i] for line in self.__can_be_colored]
            self.__presolve_line(column, possible_colors, self.__columns_info[i])

    def __solve_line(self, line, start, blocks_info, current_block):
        """
        Функция, рассчитывающая строку. Начиная с первой клетки пытаемся расставить блоки, возможность поставить i-й
        блок с j-й клетки запоминаем в матрицу self.__evaluated_positions. Возможные варианты окраски i-й клетки
        запоминаем в массив self.__evaluated_line.
        Сложность O(N*M) - сложность заполнения матрицы.

        :param line: массив строк, информация об уже окрашенных клетках (или еще не окрашенных)
        :param start: число, стартовая позиция для текущего блока
        :param blocks_info: массив пар (цвет, длина), информация о блоках для строки
        :param current_block: число, текущий блок
        :return: булево значение, можно ли поставить блок current_block начиная с позиции start
        """
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

    def __cell_coloring(self, line_number, column_number, position):
        old_number_of_colors = len(self.__can_be_colored[line_number][column_number])
        self.__can_be_colored[line_number][column_number] &= self.__evaluated_line[position]
        if len(self.__can_be_colored[line_number][column_number]) == 0:
            raise NonoException(f'Incorrect input: cell on position [{line_number}][{column_number}] cannot be colored')
        elif len(self.__can_be_colored[line_number][column_number]) == 1:
            self.__nonogram[line_number][column_number] = \
                list(self.__can_be_colored[line_number][column_number])[0]
        if old_number_of_colors != len(self.__can_be_colored[line_number][column_number]):
            self.__line_was_changed[line_number] = True
            self.__column_was_changed[column_number] = True
            return True
        return False

    def __solve(self):
        """
        Проходим поочередно по всем строкам и стоблцам, производим расчет для тех строк и столбцов, в которых были
        изменения на прошлой итерации. Если получили новые изменения - помечаем столбец и строку, в которых находится
        измененная клетка, как измененные в массивах self.__line_was_changed и self.__column_was_changed соответственно,
        помечаем, что в нонограмме были изменения (was_changed). Если на данной итерации в нонограмме были изменения
        (was_changed is True), запускаем новую итерацию. Если изменений не было - то больше рассчитывать нечего, либо
        нонограмма решена, либо она не имеет логического решения (без угадываний).
        Сложность O((N^2)*(M^2)) - в худшем случае на каждой итерации изменяется только одна клетка
        :return:
        """
        was_changed = True
        while was_changed:
            was_changed = False
            for line_number in range(len(self.__lines_info)):  # lines
                if self.__line_was_changed[line_number]:
                    self.__line_was_changed[line_number] = False
                    line = self.__nonogram[line_number]
                    self.__evaluated_line = [set() for _ in range(len(line))]
                    self.__evaluated_positions = [[None for _ in range(len(self.__lines_info[line_number]))]
                                                  for __ in range(len(line))]
                    can_be_solved = self.__solve_line(line, 0, self.__lines_info[line_number], 0)
                    if not can_be_solved:
                        raise NonoException(f'Incorrect input: line {line_number} cannot be colored')
                    for column_number in range(len(line)):
                        if self.__cell_coloring(line_number, column_number, column_number):
                            was_changed = True
            for column_number in range(len(self.__columns_info)):  # columns
                if self.__column_was_changed[column_number]:
                    self.__column_was_changed[column_number] = False
                    column = [self.__nonogram[i][column_number] for i in range(len(self.__nonogram))]
                    self.__evaluated_line = [set() for _ in range(len(column))]
                    self.__evaluated_positions = [[None for _ in range(len(self.__columns_info[column_number]))]
                                                  for __ in range(len(column))]
                    can_be_solved = self.__solve_line(column, 0, self.__columns_info[column_number], 0)
                    if not can_be_solved:
                        raise NonoException(f'Incorrect input: column {column_number} cannot be colored')
                    for line_number in range(len(column)):
                        if self.__cell_coloring(line_number, column_number, line_number):
                            was_changed = True
        self.__guess()

    def __guess(self):
        x, y = 0, 0
        flag = False
        for i in range(len(self.__lines_info)):
            for j in range(len(self.__columns_info)):
                if self.__nonogram[i][j] == '.':
                    x, y = i, j
                    flag = True
                    break
            if flag:
                break
        if self.__nonogram[x][y] != '.':
            return
        properties = list(self.__can_be_colored[x][y])
        old_nono = deepcopy(self.__nonogram)
        old_prop = deepcopy(self.__can_be_colored)
        for i in range(len(properties)):
            try:
                self.__can_be_colored[x][y] = {properties[i]}
                self.__nonogram[x][y] = properties[i]
                self.__line_was_changed[x] = True
                self.__column_was_changed[y] = True
                self.__solve()
            except NonoException:
                if i == len(properties) - 1:
                    raise
                self.__nonogram = old_nono
                self.__can_be_colored = old_prop
            else:
                break

    def solve(self):
        self.__presolve()
        self.__solve()

    def __str__(self):
        """
        Строковое представление нонограммы для вывода
        :return:
        """
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
    """
    Функция, которая преобразует введенные данные в строку с информацией о блоках
    :param line: строка, линия с введенной информацией
    :param colors: массив строк, цвета, используемые в нонограмме
    :param counter: словарь {цвет - количество}, для подсчета клеток каждого цвета в информации о строках/столбцах
    :return: массив пар (цвет, длина), информация о блоках для строки/столбца
    """
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
                raise NonoException('Incorrect input: no such color \'' + word[index:] + '\'')
            counter[word[index:]] += int(word[:index])
            elements.append((word[index:], int(word[:index])))
    return elements


def file_reader(path_to_file):
    """
    Функция, обрабатывающая входной файл и представляющая информацию в нем в виде нонограммы.
    :param path_to_file: строка, путь к входному файлу
    :return: объект класса Nonogram, нонограмма, готовая к расчету
    """
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
                if not line.startswith('colors: '):
                    raise NonoException('Incorrect input: no colors')
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
            message += f'{color}: in lines {colors_in_lines[color]}, in columns {colors_in_columns[color]}\n'
        raise NonoException(message)
    return Nonogram(colors, lines, columns)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Files for input and output')
    parser.add_argument('input_file', type=str, help='name of file with numbers')
    parser.add_argument('-s', type=str, default=None, help='name of file with result')
    arguments = parser.parse_args()
    try:
        nonogram = file_reader(arguments.input_file)
        nonogram.solve()
    except NonoException as exception:
        nonogram = str(exception)
    if arguments.s is None:
        print(nonogram)
    else:
        with open(arguments.s, 'w') as f_out:
            f_out.write(str(nonogram))
