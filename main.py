import pygame
import pygame_gui as pgui
import utypes as tp
import random
import re
import os
import copy


def generate_ans(width, height):
    """Генерируем заполненую таблицу."""

    table = [[] for _ in range(height)]
    for i in range(height):
        letters = [j for j in tp.LETTERS[:width]]  # Создаем новый массив букв
        table[i] = [[f'{i + 1}{letters.pop(random.randint(0, len(letters) - 1))}'] for _ in
                    range(width)]  # Заполняем строки параметрами НОМЕР_СТРОКИ+БУКВА

    completed_cells = []
    for x in range(width):  # Создаем список нетронутых клеток
        completed_cells.append([])
        for y in range(height):
            completed_cells[-1].append(y)

    return table, completed_cells


def check_possibility(completed_cells, allowed_x):
    """Проверка на возможность использования разных типов утверждений."""

    """
    Возможные конфигурации:
    000-только 1 тип
    100-только 2 тип
    010-только 3 тип
    110-2 и 3 тип
    011-3 и 4 тип
    111-все типы (кроме 1)
    """

    n = 0
    result = '000'
    for i in range(len(completed_cells)):
        if len(completed_cells[i]) >= 2:  # Проверка 2 типа
            result = '1' + result[1:]
            n += len(completed_cells[i])

        if i and completed_cells[i] and completed_cells[i - 1]:  # Проверка 3 типа
            result = result[:1] + '1' + result[2:]
            n += len(completed_cells[i])
            if i < len(completed_cells) - 1 and completed_cells[i + 1]:
                for x in allowed_x:  # Проверка 4 типа
                    if x:
                        result = result[:2] + '1'
                        break
    if n < 2:
        return '000'

    return result


def create_condition(possibility, table, completed_cells, allowed_x):

    """Генерация новых утверждений.
       Общий алгоритм:
       Создовая новое условие, привязываем одну завершенную клетку к другой (или к дому).
       Теперь ее значение можно вычислить через другую клетку => можно убирать ее из списка завершенных клеток.
       Повторяем пока не закончатся завершенные клетки.
    """

    height = len(table)
    width = len(table[0])
    new_condition = []
    new_question = ''
    new_answer = ''
    if '1' in possibility:  # Если доступны типы с 2 по 4.
        if possibility == '110':
            roll = random.choice([2, 2, 2, 3])
        elif possibility == '011':
            roll = random.choice([3, 4])
        else:
            roll = random.choice([2, 2, 2, 2, 3, 3, 4])

        # Порядок вариантов клеток не менялся с момента их создания, то на 1 месте сейчас находится ответ для клетки.

        if roll == 2 and int(possibility[0]) or possibility == '100':
            # Если выпал 2 тип и он разрешен, или он единственный разрешенный тип.
            x = random.randint(0, width - 1)
            while len(completed_cells[x]) < 2:  # Пока в столбце не будет 2 или больше завершенных клеток реролим x.
                x = random.randint(0, width - 1)
            y2 = completed_cells[x].pop(random.randint(0, len(
                completed_cells[x]) - 1))  # Удаляем вторую клетку с координатами x;y2 из массива завершенных клеток.
            y1 = completed_cells[x][random.randint(0, len(
                completed_cells[x]) - 1)]  # К первой клетке мы прявязали утверждением вторую, ее удалять не надо.
            k1, k2 = table[y1][x][0], table[y2][x][0]  # Смотрим чему действительно равны параметры в клетках.
            new_condition = f'2;{k1};{k2}'  # Создаем условие
            new_question = f'{x + 1};{y2 + 1}'  # Создаем вопрос
            new_answer = k2  # Запоминаем ответ
            for i in range(width):
                if k2 not in table[y2][i]:
                    table[y2][i].append(k2)  # Добавляем параметр 2-ой клетки в варианты остальных клеток строки.

        elif roll == 3 and int(possibility[1]) or possibility == '010':
            # Если выпал 3 тип и он разрешен, или он единственный разрешенный тип.
            x1 = random.randint(0, width - 1)
            if x1 == 0:
                x2 = 1
            elif x1 == width - 1:
                x2 = width - 2
            else:
                x2 = x1 - random.choice([-1, 1])
            while not completed_cells[x1] or not completed_cells[x2]:
                # Пока в двух соседних слобцах не будут завершенные клетки реролим x.
                x1 = random.randint(0, width - 1)
                if x1 == 0:
                    x2 = 1
                elif x1 == width - 1:  # Если х1 крайний, то x2 однозначно задан
                    x2 = width - 2
                else:  # Иначе все равно, где будет х2 относительно х1
                    x2 = x1 - random.choice([-1, 1])
            y2 = completed_cells[x2].pop(random.randint(0, len(
                completed_cells[x2]) - 1))  # Удаляем вторую клетку с координатами x2;y2 из массива завершенных клеток.
            y1 = completed_cells[x1][random.randint(0, len(
                completed_cells[x1]) - 1)]  # К первой клетке мы прявязали утверждением вторую, ее удалять не надо.
            if x1 - x2 == 1:  # Определяем расположение х1 относительно х2
                place = 'справа'
            else:
                place = 'слева'
            k1, k2 = table[y1][x1][0], table[y2][x2][0]  # Смотрим чему действительно равны параметры в клетках.
            new_condition = f'3;{k1};{place};{k2}'  # Создаем условие
            new_question = f'{x2 + 1};{y2 + 1}'  # Создаем вопрос
            new_answer = k2  # Запоминаем ответ
            for i in range(width):
                if k2 not in table[y2][i]:
                    table[y2][i].append(k2)  # Добавляем параметр 2-ой клетки в варианты остальных клеток строки.

        elif roll == 4 and int(possibility[2]):  # Если выпал 4 тип и он разрешен.
            x1 = random.randint(0, width - 1)
            if x1 == 0:
                x2 = 1
            elif x1 == width - 1:
                x2 = width - 2
            else:
                x2 = x1 - random.choice([-1, 1])
            while not completed_cells[x1] or not completed_cells[x2] or max([0, x1 - x2]) not in allowed_x[x1]:
                # Пока в двух соседних слобцах не будут завершенные клетки реролим x.
                x1 = random.randint(0, width - 1)
                if x1 == 0:
                    x2 = 1
                elif x1 == width - 1:  # Если х1 крайний, то x2 однозначно задан
                    x2 = width - 2
                else:  # Иначе все равно, где будет х2 относительно х1
                    x2 = x1 - random.choice([-1, 1])
            if 1 - max([0, x1 - x2]) in allowed_x[x1]:
                allowed_x[x1].remove(1 - max([0, x1 - x2]))
            y2 = completed_cells[x2].pop(random.randint(0, len(
                completed_cells[x2]) - 1))  # Удаляем вторую клетку с координатами x2;y2 из массива завершенных клеток.
            y1 = completed_cells[x1][random.randint(0, len(
                completed_cells[x1]) - 1)]  # К первой клетке мы прявязали утверждением вторую, ее удалять не надо.

            k1, k2 = table[y1][x1][0], table[y2][x2][0]  # Смотрим чему действительно равны параметры в клетках.
            new_condition = f'4;{k1};{k2}'  # Создаем условие
            new_question = f'{x2 + 1};{y2 + 1}'  # Создаем вопрос
            new_answer = k2  # Запоминаем ответ
            for i in range(width):
                if k2 not in table[y2][i]:
                    table[y2][i].append(k2)  # Добавляем параметр 2-ой клетки в варианты остальных клеток строки.


    elif possibility == '000':  # Если доступен только 1 тип.
        completed_cells_exist = True
        while completed_cells_exist:  # Пока существуют завершенные клетки
            x = random.randint(0, width - 1)
            while not completed_cells[x]:  # Пока не встретим столбец с завершенной клеткой реролим х.
                x = random.randint(0, width - 1)
            y = completed_cells[x].pop(random.randint(0, len(completed_cells[x]) - 1))
            # Удаляем 2ю клетку из массива завершенных клеток. Она будет привязана к номеру дома напрямую.
            k = table[y][x][0]  # Смотрим чему действительно равен параметр в клетке.
            new_condition.append(f'1;{x + 1};{k}')  # Создаем условие
            new_question = f'{x + 1};{y + 1}'  # Создаем вопрос
            new_answer = k  # Запоминаем ответ
            for i in range(width):
                if k not in table[y][i]:
                    table[y][i].append(k)  # Добавляем параметр клетки в варианты остальных клеток строки.

            completed_cells_exist = False
            for i in completed_cells:  # Проверяем остались ли завершенные клетки
                if i:
                    completed_cells_exist = True
        return table, completed_cells, new_condition, new_question, new_answer, allowed_x

    return table, completed_cells, [new_condition], new_question, new_answer, allowed_x


def convert(string):
    global g_width, g_height
    """Делает вывод красивым."""

    options = {}
    for i in range(1, g_height + 1):
        options.update({f'{i}': f'{i}'})
        options.update({f'{i}{j}': f'{i}{j}' for j in tp.LETTERS[:g_width]})
    with open('Шаблоны.txt', 'r', encoding='utf-8') as file:
        i = 1
        for line in file:
            line = line.replace(' ', '').strip('\n')
            options.update({f'{i}': f'{line.split(":")[0]}'})
            for j, option in enumerate(line.split(':')[1].split(',')):
                options.update({f'{i}{tp.LETTERS[j]}': f'{option}'})
            i += 1
    parts = string.split(';')
    if len(parts) == 2 and parts[1][-1].isalpha():
        y = str(int(re.search(r'\d+', parts[1]).group(0)))
        return f'В доме с номером {parts[0]} {options[y]} - {options[parts[1]]}.'  # Вывод ответа
    elif len(parts) == 2 and not parts[1][-1].isalpha():
        y = str(int(re.search(r'\d+', parts[1]).group(0)))
        return f'Что в доме с номером {parts[0]} в параметре {options[y]}?'  # Вывод вопроса
    elif parts[0] == '0':
        start = f'В ряд стоят {parts[1]} дома(ов) с {parts[2]} параметрами(ом).\n'  # Вывод условия
        end = ''
        for i in range(1, g_height + 1):
            end += options[str(i)] + ': '
            for j in tp.LETTERS[:g_width]:
                end += options[f'{i}{j}'] + ', '
            end = end[:-2] + '\n'
        start += end
        return start
    elif parts[0] == '1':  # Вывод 1 типа
        y = str(int(re.search(r'\d+', parts[2]).group(0)))
        return f'В доме номер {parts[1]} {options[y]} - {options[parts[2]]}.'
    elif parts[0] == '2':  # Вывод 2 типа
        y1 = str(int(re.search(r'\d+', parts[1]).group(0)))
        y2 = str(int(re.search(r'\d+', parts[2]).group(0)))
        return f'В доме, в котором {options[y1]} - {options[parts[1]]}, {options[y2]} - {options[parts[2]]}.'
    elif parts[0] == '3':  # Вывод 3 типа
        y1 = str(int(re.search(r'\d+', parts[1]).group(0)))
        y2 = str(int(re.search(r'\d+', parts[3]).group(0)))
        return f'Дом, в котором {options[y1]} - {options[parts[1]]}, {parts[2]} от дома, в котором {options[y2]} - {options[parts[3]]}.'
    elif parts[0] == '4':  # Вывод 4 типа
        y1 = str(int(re.search(r'\d+', parts[1]).group(0)))
        y2 = str(int(re.search(r'\d+', parts[2]).group(0)))
        return f'Дом, в котором {options[y1]} - {options[parts[1]]}, соседний с домом, в котором {options[y2]} - {options[parts[2]]}.'


def save_result(conditions, questions, answers):
    """Сохранение результатов в файл."""
    number = 1
    while True:
        if os.path.exists(rf'Задачи\Условие {number}.txt'):
            number += 1
        else:
            file = open(rf'Задачи\Условие {number}.txt', 'w')
            for i in conditions:
                file.write(convert(i) + '\n')
            file.write('\n')

            for i in questions:
                file.write(convert(i) + '\n')
            file.close()
            break

    file = open(r'Задачи\Ответы.txt', 'a')
    file.write(f'Задача {number}\n')
    for i in questions:
        file.write(convert(i) + '\n')
    file.write('\nОтвет: \n')

    for i in answers:
        file.write(convert(i) + '\n')
    file.write('\n')
    file.close()


def solve_puzzle(conditions, questions, table, deep):
    """Решает задачу по условиям."""

    incompleted_cells = 0
    height = len(table)
    width = len(table[0])
    completed_cells = [[] for _ in range(width)]
    last_completed_cells = []
    used_conditions = []
    something_happened = True
    answer = []

    while something_happened:
        something_happened = False
        for condition in conditions:
            if condition[0] == '1':
                used_conditions.append(condition)
                k = condition.split(';')[2]
                x = int(condition.split(';')[1]) - 1
                y = int(re.search(r'\d+', condition.split(';')[2]).group(0)) - 1
                if len(table[y][x]) == 1 and table[y][x][0] != k:  # Проверка на соответсвие таблицы утверждению
                    return False, None, None, None
                table[y][x] = [k]
                if (x, y) not in last_completed_cells:
                    last_completed_cells.append((x, y))
                something_happened = True
                completed_cells[x].append(y)
                for i in range(width):
                    if y not in completed_cells[i]:
                        try:
                            table[y][i].pop(table[y][i].index(k))
                        except ValueError:
                            pass

            if condition[0] == '2':
                k1 = condition.split(';')[1]
                k2 = condition.split(';')[2]
                y1 = int(re.search(r'\d+', k1).group(0)) - 1
                y2 = int(re.search(r'\d+', k2).group(0)) - 1
                for x in range(width):
                    if len(table[y1][x]) == 1 and table[y1][x][0] == k1:
                        if len(table[y2][x]) == 1 and table[y2][x][0] != k2:  # Проверка на соответсвие таблицы утверждению
                            return False, None, None, None
                        table[y2][x] = [k2]
                        if (x, y2) not in last_completed_cells:
                            last_completed_cells.append((x, y2))
                        something_happened = True
                        used_conditions.append(condition)
                        completed_cells[x].append(y2)
                        for i in range(width):
                            if y2 not in completed_cells[i]:
                                try:
                                    table[y2][i].pop(table[y2][i].index(k2))
                                except ValueError:
                                    pass

                    if len(table[y2][x]) == 1 and table[y2][x][0] == k2:
                        if len(table[y1][x]) == 1 and table[y1][x][0] != k1:  # Проверка на соответсвие таблицы утверждению
                            return False, None, None, None
                        table[y1][x] = [k1]
                        if (x, y1) not in last_completed_cells:
                            last_completed_cells.append((x, y1))
                        something_happened = True
                        used_conditions.append(condition)
                        completed_cells[x].append(y1)
                        for i in range(width):
                            if y1 not in completed_cells[i]:
                                try:
                                    table[y1][i].pop(table[y1][i].index(k1))
                                except ValueError:
                                    pass

            if condition[0] == '3':
                k1 = condition.split(';')[1]
                place = condition.split(';')[2]
                k2 = condition.split(';')[3]
                y1 = int(re.search(r'\d+', k1).group(0)) - 1
                y2 = int(re.search(r'\d+', k2).group(0)) - 1

                for x in range(width):
                    if len(table[y1][x]) == 1 and table[y1][x][0] == k1:
                        if place == "слева":
                            x2 = x + 1
                        else:
                            x2 = x - 1
                        if x2 >= width or x2 < 0:
                            return False, None, None, None
                        if len(table[y2][x2]) == 1 and table[y2][x2][0] != k2:  # Проверка на соответсвие таблицы утверждению
                            return False, None, None, None
                        table[y2][x2] = [k2]
                        if (x2, y2) not in last_completed_cells:
                            last_completed_cells.append((x2, y2))
                        something_happened = True
                        used_conditions.append(condition)
                        completed_cells[x2].append(y2)
                        for i in range(width):
                            if y2 not in completed_cells[i]:
                                try:
                                    table[y2][i].pop(table[y2][i].index(k2))
                                except ValueError:
                                    pass

                    if len(table[y2][x]) == 1 and table[y2][x][0] == k2:
                        if place == "слева":
                            x1 = x - 1
                        else:
                            x1 = x + 1
                        if x1 >= width or x1 < 0:
                            return False, None, None, None
                        if len(table[y1][x1]) == 1 and table[y1][x1][0] != k1:  # Проверка на соответсвие таблицы утверждению
                            return False, None, None, None
                        table[y1][x1] = [k1]
                        if (x1, y1) not in last_completed_cells:
                            last_completed_cells.append((x1, y1))
                        something_happened = True
                        used_conditions.append(condition)
                        completed_cells[x1].append(y1)
                        for i in range(width):
                            if y1 not in completed_cells[i]:
                                try:
                                    table[y1][i].pop(table[y1][i].index(k1))
                                except ValueError:
                                    pass
            if condition[0] == '4':
                k1 = condition.split(';')[1]
                k2 = condition.split(';')[2]
                y1 = int(re.search(r'\d+', k1).group(0)) - 1
                y2 = int(re.search(r'\d+', k2).group(0)) - 1

                for x in range(width):
                    if len(table[y1][x]) == 1 and table[y1][x][0] == k1:
                        # Проверка на соответсвие таблицы утверждению
                        # Если есть 2 соседа, оба завершены и параметры не соответствуют утверждению
                        if x and len(table[y2][x - 1]) == 1 and table[y2][x - 1][0] != k2:
                            if x < width - 1 and len(table[y2][x + 1]) == 1 and table[y2][x + 1][0] != k2:
                                return False, None, None, None
                        # Если есть только сосед справа, он завершен и параметр не соответствуют утверждению
                        if not x and len(table[y2][x + 1]) == 1 and table[y2][x + 1][0] != k2:
                            return False, None, None, None
                        # Если есть только сосед слева, он завершен и параметр не соответствуют утверждению
                        if x == width - 1 and len(table[y2][x - 1]) == 1 and table[y2][x - 1][0] != k2:
                            return False, None, None, None
                        something_happened = True
                        used_conditions.append(condition)
                        for i in range(width):
                            if y2 not in completed_cells[i] and abs(x - i) != 1:
                                try:
                                    table[y2][i].pop(table[y2][i].index(k2))
                                except ValueError:
                                    pass
                    if len(table[y2][x]) == 1 and table[y2][x][0] == k2:
                        # Проверка на соответсвие таблицы утверждению
                        # Если есть 2 соседа, оба завершены и параметры не соответствуют утверждению
                        if x and len(table[y1][x - 1]) == 1 and table[y1][x - 1][0] != k1:
                            if x < width - 1 and len(table[y1][x + 1]) == 1 and table[y1][x + 1][0] != k1:
                                return False, None, None, None
                        # Если есть только сосед справа, он завершен и параметр не соответствуют утверждению
                        if not x and len(table[y1][x + 1]) == 1 and table[y1][x + 1][0] != k1:
                            return False, None, None, None
                        # Если есть только сосед слева, он завершен и параметр не соответствуют утверждению
                        if x == width - 1 and len(table[y1][x - 1]) == 1 and table[y1][x - 1][0] != k1:
                            return False, None, None, None
                        something_happened = True
                        used_conditions.append(condition)
                        for i in range(width):
                            if y1 not in completed_cells[i] and abs(x - i) != 1:
                                try:
                                    table[y1][i].pop(table[y1][i].index(k1))
                                except ValueError:
                                    pass

        for used_condition in used_conditions:
            try:
                conditions.pop(conditions.index(used_condition))
            except ValueError:
                pass
        used_conditions = []

        for x in range(width):
            for y in range(height):
                if len(table[y][x]) == 1 and y not in completed_cells[x]:
                    completed_cells[x].append(y)
                    if (x, y) not in last_completed_cells:
                        last_completed_cells.append((x, y))
                    something_happened = True
                    for i in range(width):
                        if y not in completed_cells[i]:
                            try:
                                table[y][i].pop(table[y][i].index(table[y][x][0]))
                            except ValueError:
                                pass

    for x in range(width):
        for y in range(height):
            if len(table[y][x]) != 1:
                incompleted_cells += 1

    if incompleted_cells > 0 and not conditions:
        return False, None, None, None
    elif incompleted_cells > 0 and conditions:
        is_solved, table, deep, answer, last_completed_cells = brute_force_search(copy.deepcopy(table), conditions.copy(), questions.copy(), deep, last_completed_cells)
        if is_solved:
            return True, answer.copy(), copy.deepcopy(table), last_completed_cells.copy()
        else:
            return False, None, None, None

    for question in questions:
        x = int(question.split(';')[0]) - 1
        y = int(question.split(';')[1]) - 1
        answer.append(f'{x + 1};{table[y][x][0]}')

    return True, answer.copy(), copy.deepcopy(table), last_completed_cells.copy()


def removing_excess(conditions, questions, table, deep):
    """Убирает избытычность условий."""

    new_conditions = conditions.copy()
    empty_table = copy.deepcopy(table)
    is_solved, new_answers, new_table, last_completed_cells = solve_puzzle(new_conditions.copy(), questions.copy(), copy.deepcopy(empty_table), deep)
    if not is_solved:
        print(is_solved)
        pass
    while is_solved:  # Если смогло решить.
        conditions = new_conditions.copy()
        if not conditions:
            break
        for i in conditions:
            new_conditions = conditions.copy()
            new_conditions.remove(i)  # Удаляем 1 из условий.
            empty_table = copy.deepcopy(table)
            is_solved, new_answers, new_table, last_completed_cells = solve_puzzle(new_conditions.copy(), questions.copy(), copy.deepcopy(empty_table), deep)
            if is_solved:  # Если смогло запомним резульат.
                break
    return conditions.copy()  # Если ни разу решилось то возвращаем.


def brute_force_search(table, conditions, questions, deep, last_completed_cells):
    """
    Подставляет один из вариантов и пытается решить.
    Есть ограничение по глубине.
    """

    # answer = []
    final_table = []
    final_answer = []
    new_table = copy.deepcopy(table)
    if deep < 1 and (len(conditions) != 1 or conditions[0][0] != '3'):  # Выход из рекурсии
        return False, None, None, None, None
    height = len(new_table)
    width = len(new_table[0])
    min_k = width + 1
    min_cell = (-1, -1)
    incomplete_cells = []
    number_of_solution = 1


    for y in range(height):
        for x in range(width):
            if len(new_table[y][x]) > 1:  # Находим клетку с мин кол-вом вариантов.
                incomplete_cells.append((x, y))
                if len(new_table[y][x]) <= min_k:
                    min_k = len(new_table[y][x])
                    min_cell = (x, y)
    for new_cell in incomplete_cells:
        number_of_solution -= 1
        for option in table[new_cell[1]][new_cell[0]]:  # Перебор вариантов.
            new_table[new_cell[1]][new_cell[0]] = [option]  # Подстовляем вариант как ответ.
            if new_cell not in last_completed_cells:
                last_completed_cells.append(new_cell)

            for x in range(width):
                for y in range(height):
                    if len(new_table[y][x]) == 1:
                        remove = new_table[y][x][0]  # Убираем ответы клеток из варинтов других клеток.
                        for i in range(width):
                            if i != x:
                                try:
                                    new_table[y][i].remove(remove)
                                except ValueError:
                                    pass

            is_solved, answer, new_table, new_last_completed_cells = solve_puzzle(conditions.copy(), questions.copy(), new_table, deep - 1)  # Пытаемся решить
            if is_solved:  # Если решило inc(number_of_solution) и запоминам результаты
                number_of_solution += 1
                for new_last_completed_cell in new_last_completed_cells:
                    if new_last_completed_cell not in last_completed_cells and min_cell == new_cell:
                        last_completed_cells.append(new_last_completed_cell)
                final_answer = answer.copy()
                final_table = copy.deepcopy(new_table)
                new_table = copy.deepcopy(table)
            else:  # Иначе восстанавливаем таблицу.
                last_completed_cells.remove(new_cell)
                new_table = copy.deepcopy(table)
        if number_of_solution != 1:
            break



    if number_of_solution == 1:
        return True, copy.deepcopy(final_table), deep - 1, final_answer.copy(), last_completed_cells
    return False, None, deep, None, None


def generate_puzzle(width, height, deep):
    """Основное тело программы."""

    table, competed_cells = generate_ans(width, height)
    competed_table = copy.deepcopy(table)
    conditions = []
    allowed_x = [[i for i in range(2)] for _ in range(width)]
    questions = []
    answers = []
    possibility = '110'

    while '1' in possibility:
        possibility = check_possibility(competed_cells, allowed_x)
        table, competed_cells, new_condition, new_question, new_answer, allowed_x = create_condition(possibility, table, competed_cells, allowed_x)
        for i in new_condition:
            conditions.append(i)
        if len(questions) < 2:
            questions.append(new_question)
            # answers.append(f'{new_question.split(";")[0]};{new_answer}')

    for y in range(len(table)):
        for x in range(len(table[0])):
            random.shuffle(table[y][x])

    len1 = len(conditions)
    print(len1)
    random.shuffle(conditions)
    empty_table = copy.deepcopy(table)
    conditions = removing_excess(conditions, questions, empty_table, deep).copy()
    _, _, _, last_completed_cells = solve_puzzle(conditions.copy(), questions.copy(), copy.deepcopy(table), deep)
    questions = []
    for x, y in last_completed_cells[-2:]:
        questions.append(f'{x + 1};{y + 1}')
    is_solved, answers, new_table, last_completed_cells = solve_puzzle(conditions.copy(), questions.copy(), copy.deepcopy(table), deep)
    conditions.insert(0, f'0;{len(table[0])};{len(table)}')  # Добвляем вводную часть.
    save_result(conditions, questions, answers)
    len2 = len(conditions) - 1
    print(len2, is_solved)

    print('________________Если совпали - хорошо___________________')
    print(competed_table == new_table)
    if not competed_table == new_table:
        print(competed_table == new_table)
    if len1 - len2 < height + 1:
        print(len2)
    print(competed_table)
    print(new_table)


def start_bf(width, height, deep, number_generation):
    start_b.disable()
    width_input.disable()
    height_input.disable()
    for i in range(number_generation):
        generate_puzzle(width, height, deep)
    start_b.enable()
    width_input.enable()
    height_input.enable()

def get_values():
    if width_input.text == '':
        if not width_input.is_focused:
            width_input.set_text('4')
        width = 4
    else:
        width = int(width_input.text)
    if height_input.text == '':
        if not height_input.is_focused:
            height_input.set_text('3')
        height = 3
    else:
        height = int(height_input.text)
    if deep_input.text == '':
        if not deep_input.is_focused:
            deep_input.set_text('1')
        deep = 1
    else:
        deep = int(deep_input.text)
    if number_input.text == '':
        if not number_input.is_focused:
            number_input.set_text('1')
        number_generation = 1
    else:
        number_generation = int(number_input.text)
    return width, height, deep, number_generation


pygame.init()
pygame.font.init()
out_font = pygame.font.Font(None, 30)
manager = pgui.UIManager((tp.WIDTH, tp.HEIGHT))
screen = pygame.display.set_mode((tp.WIDTH, tp.HEIGHT))
pygame.display.set_caption("Генератор загадок Эйнштейна")
clock = pygame.time.Clock()
screen.fill(tp.BG_COLOR)

start_b = pgui.elements.UIButton(relative_rect=pygame.Rect((125, 20), tp.BUTTON_SIZE),
                                 text='Начать',
                                 manager=manager)
start_b.colours['normal_text'] = pygame.Color(tp.WHITE)
start_b.colours['normal_bg'] = pygame.Color((40, 40, 40, 255))
start_b.rebuild()

doc_b = pgui.elements.UIButton(relative_rect=pygame.Rect((125, 370), tp.BUTTON_SIZE),
                               text='Документация',
                               manager=manager)
doc_b.colours['normal_text'] = pygame.Color(tp.WHITE)
doc_b.colours['normal_bg'] = pygame.Color((40, 40, 40, 255))
doc_b.rebuild()

width_input = pgui.elements.UITextEntryLine(relative_rect=pygame.Rect((350, 90), tp.INPUT_SIZE),
                                            manager=manager)
width_input.set_allowed_characters(tp.WHITE_LIST)
width_input.set_text('4')
width_input.set_text_length_limit(2)

height_input = pgui.elements.UITextEntryLine(relative_rect=pygame.Rect((350, 160), tp.INPUT_SIZE),
                                             manager=manager)
height_input.set_allowed_characters(tp.WHITE_LIST)
height_input.set_text('3')
height_input.set_text_length_limit(2)

deep_input = pgui.elements.UITextEntryLine(relative_rect=pygame.Rect((350, 230), tp.INPUT_SIZE),
                                           manager=manager)
deep_input.set_allowed_characters(tp.WHITE_LIST)
deep_input.set_text('1')
deep_input.set_text_length_limit(1)

number_input = pgui.elements.UITextEntryLine(relative_rect=pygame.Rect((350, 300), tp.INPUT_SIZE),
                                             manager=manager)
number_input.set_allowed_characters(tp.WHITE_LIST)
number_input.set_text('1')
number_input.set_text_length_limit(2)



width_label = pgui.elements.UILabel(relative_rect=pygame.Rect((125, 90), (166, 30)), text='Введите кол-во домов',
                                    manager=manager)
width_label.bg_colour = pygame.Color(tp.BG_COLOR)
width_label.text_colour = pygame.Color(tp.BLACK)
width_label.font = pygame.font.Font('arial.ttf', 16)
width_label.rebuild()

height_label = pgui.elements.UILabel(relative_rect=pygame.Rect((125, 160), (209, 30)), text='Введите кол-во параметров',
                                     manager=manager)
height_label.bg_colour = pygame.Color(tp.BG_COLOR)
height_label.text_colour = pygame.Color(tp.BLACK)
height_label.font = pygame.font.Font('arial.ttf', 16)
height_label.rebuild()

deep_label = pgui.elements.UILabel(relative_rect=pygame.Rect((125, 230), (208, 30)), text='Введите кол-во переборов',
                                   manager=manager)
deep_label.bg_colour = pygame.Color(tp.BG_COLOR)
deep_label.text_colour = pygame.Color(tp.BLACK)
deep_label.font = pygame.font.Font('arial.ttf', 16)
deep_label.rebuild()

number_label = pgui.elements.UILabel(relative_rect=pygame.Rect((125, 300), (208, 30)), text='Введите кол-во генераций',
                                     manager=manager)
number_label.bg_colour = pygame.Color(tp.BG_COLOR)
number_label.text_colour = pygame.Color(tp.BLACK)
number_label.font = pygame.font.Font('arial.ttf', 16)
number_label.rebuild()

# print(solve_puzzle(['1;4;1b', '3;1d;слева;1a', '3;1b;слева;1e'], ['5;1', '3;1'], [[['1d', '1b', '1e', '1c', '1a'], ['1c', '1a', '1e', '1b', '1d'], ['1b', '1a', '1e', '1c', '1d'], ['1b', '1a', '1e', '1c', '1d'], ['1c', '1b', '1e', '1d', '1a']]], 1))
# print(solve_puzzle(['2;2b;3a', '3;2d;слева;2a', '4;3a;1d', '1;1;2c', '4;2c;2b', '2;2c;3d', '1;3;2d', '3;1c;справа;3b', '3;2a;справа;1a', '4;3d;1b', '2;2a;1c', '1;4;3c'], ['2;1', '3;1'], [[['1d', '1b', '1c', '1a'], ['1c', '1a', '1d', '1b'], ['1a', '1b', '1c', '1d'], ['1c', '1d', '1a', '1b']], [['2d', '2b', '2c', '2a'], ['2b', '2a', '2c', '2d'], ['2c', '2b', '2a', '2d'], ['2b', '2c', '2a', '2d']], [['3b', '3a', '3c', '3d'], ['3d', '3c', '3a', '3b'], ['3b', '3c', '3a', '3d'], ['3a', '3c', '3d', '3b']]], 1))
# print(solve_puzzle(['3;1a;слева;1e', '1;2;1b', '4;1b;1d', '1;4;1a', '4;1b;1c'], ['5;1', '1;1'], [[['1a', '1e', '1d', '1c', '1b'], ['1b', '1a', '1d', '1c', '1e'], ['1c', '1a', '1e', '1d', '1b'], ['1c', '1b', '1e', '1a', '1d'], ['1a', '1b', '1d', '1c', '1e']]], 1))
# print(solve_puzzle(['3;1a;справа;1d', '2;3b;2d', '2;3c;2a', '1;1;3b', '3;3d;справа;1c', '3;3b;слева;2b', '2;3c;1a'], ['2;3', '4;1'], [[['1b', '1d', '1a', '1c'], ['1b', '1a', '1d', '1c'], ['1c', '1b', '1a', '1d'], ['1d', '1a', '1c', '1b']], [['2d', '2a', '2c', '2b'], ['2d', '2b', '2c', '2a'], ['2d', '2c', '2a', '2b'], ['2c', '2a', '2b', '2d']], [['3d', '3c', '3b', '3a'], ['3b', '3c', '3d', '3a'], ['3b', '3a', '3c', '3d'], ['3d', '3b', '3a', '3c']]], 1))

run = True
while run:
    time_delta = clock.tick(60) / 1000.0
    g_width, g_height, g_deep, number_generation = get_values()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        manager.process_events(event)
        if event.type == pygame.USEREVENT:
            if event.user_type == pgui.UI_BUTTON_PRESSED:  # обработка нажатий на кнопки
                if event.ui_element == start_b:
                    start_bf(g_width, g_height, g_deep, number_generation)
                if event.ui_element == doc_b:
                    os.system(r'start " " Документация.pdf')
    manager.update(time_delta)
    manager.draw_ui(screen)
    pygame.display.flip()
