import pygame
import pygame_gui as pgui
import uTypes as tp
import random

pygame.init()
pygame.font.init()
out_font = pygame.font.Font(None, 30)
manager = pgui.UIManager((tp.WIDTH, tp.HEIGHT))
screen = pygame.display.set_mode((tp.WIDTH, tp.HEIGHT))
pygame.display.set_caption("Генератор загадок Эйнштейна")
clock = pygame.time.Clock()
screen.fill(tp.WHITE)


start_b = pgui.elements.UIButton(relative_rect=pygame.Rect((125, 20), tp.BUTTON_SIZE),
                                 text='Начать',
                                 manager=manager)

width_input = pgui.elements.UITextEntryLine(relative_rect=pygame.Rect((200, 90), tp.INPUT_SIZE),
                                            manager=manager)
height_input = pgui.elements.UITextEntryLine(relative_rect=pygame.Rect((200, 160), tp.INPUT_SIZE),
                                             manager=manager)

width_input.set_allowed_characters(tp.WHITE_LIST)
height_input.set_allowed_characters(tp.WHITE_LIST)
width_input.set_text_length_limit(2)
height_input.set_text_length_limit(2)


def start_bf():
    start_b.disable()
    width_input.disable()
    height_input.disable()


def generate_ans(width, height):

    """Генерируем заполненую таблицу."""

    table = [[] for _ in range(height)]
    for i in range(height):
        letters = [j for j in tp.LETTERS[:width]]  # Создаем новый массив букв
        table[i] = [[f'{i + 1}{letters.pop(random.randint(0, len(letters) - 1))}'] for _ in range(width)]  # Заполняем строки параметрами НОМЕР_СТРОКИ+БУКВА

    completed_cells = []
    for x in range(width):  # Создаем список нетронутых клеток
        completed_cells.append([])
        for y in range(height):
            completed_cells[-1].append(y)

    print(table)
    print(completed_cells)
    return table, completed_cells


def check_possibility(completed_cells):

    """Проверка на возможность использования разных типов утверждений."""

    """
    Доступные типы утверждений:
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

    if n < 3:
        return '000'

    return result


def create_condition(possibility, table, completed_cells):

    """Генерация новых утверждений."""

    height = len(table)
    width = len(table[0])
    new_condition = []
    new_question = ''
    new_answer = ''

    if '1' in possibility:  # Если доступны типы с 2 по 4.
        roll = random.random()
        if roll >= 0.25 and int(possibility[0]) or possibility == '100':
            x = random.randint(0, width - 1)
            while len(completed_cells[x]) < 2:
                x = random.randint(0, width - 1)
            y2 = completed_cells[x].pop(random.randint(0, len(completed_cells[x]) - 1))
            y1 = completed_cells[x][random.randint(0, len(completed_cells[x]) - 1)]
            k1, k2 = table[y1][x][0], table[y2][x][0]
            new_condition = f'2;{k1};{k2}'
            new_question = f'{x + 1};{y2 + 1}'
            new_answer = k2
            for i in range(width):
                if k2 not in table[y2][i]:
                    table[y2][i].append(k2)

        elif roll < 0.25 and int(possibility[1]) or possibility == '010':
            x1 = random.randint(0, width - 1)
            if x1 == 0:
                x2 = 1
            elif x1 == width - 1:
                x2 = width - 2
            else:
                x2 = x1 - random.choice([-1, 1])
            while not completed_cells[x1] or not completed_cells[x2]:
                x1 = random.randint(0, width - 1)
                if x1 == 0:
                    x2 = 1
                elif x1 == width - 1:
                    x2 = width - 2
                else:
                    x2 = x1 - random.choice([-1, 1])
            y2 = completed_cells[x2].pop(random.randint(0, len(completed_cells[x2]) - 1))
            y1 = completed_cells[x1][random.randint(0, len(completed_cells[x1]) - 1)]
            if x1 - x2 == 1:
                place = 'справа'
            else:
                place = 'слева'
            k1, k2 = table[y1][x1][0], table[y2][x2][0]
            new_condition = f'3;{k1};{place};{k2}'
            new_question = f'{x2 + 1};{y2 + 1}'
            new_answer = k2
            for i in range(width):
                if k2 not in table[y2][i]:
                    table[y2][i].append(k2)

    else:  # Если доступен только 1 тип.
        go = True
        while go:
            x = random.randint(0, width - 1)
            while not completed_cells[x]:
                x = random.randint(0, width - 1)
            y = completed_cells[x].pop(random.randint(0, len(completed_cells[x]) - 1))
            k = table[y][x][0]
            new_condition.append(f'1;{x + 1};{k}')
            new_question = f'{x + 1};{y + 1}'
            print(new_condition)
            for i in range(width):
                if k not in table[y][i]:
                    table[y][i].append(k)

            go = False
            for i in completed_cells:
                if i:
                    print(i, completed_cells)
                    go = True

        print(completed_cells)
        print(table)
        print(possibility)
        return table, completed_cells, new_condition, new_question, new_answer

    print(completed_cells)
    print(table)
    print(possibility)
    return table, completed_cells, [new_condition], new_question, new_answer


def convert(input):

    """Делает вывод красивым."""

    parts = input.split(';')
    if len(parts) == 2 and parts[1][-1].isalpha():
        return f'В доме с номером {parts[0]} параметр {parts[1]}.'  # Вывод ответа
    elif len(parts) == 2 and not parts[1][-1].isalpha():
        return f'Что в доме с номером {parts[0]} в параметре {parts[1]}?'  # Вывод вопроса
    elif parts[0] == '0':
        return f'В ряд стоят {parts[1]} дома(ов) с {parts[2]} параметрами \n.'  # Вывод условия
    elif parts[0] == '1':
        return f'В доме номер {parts[1]} параметр {parts[2]}.'  # Вывод 1 типа
    elif parts[0] == '2':
        return f'В доме, который {parts[1]}, {parts[2]}.'  # Вывод 2 типа
    elif parts[0] == '3':
        return f'Дом, который {parts[1]} {parts[2]} от дома, который {parts[3]}.'  # Вывод 3 типа



def save_result(conditions, questions, answers):

    """Сохранение результатов в файл."""

    file = open('Задачи\Условие.txt', 'w')
    for i in conditions:
        file.write(convert(i) + '\n')
    file.write('\n')

    for i in questions:
        file.write(convert(i) + '\n')
    file.close()

    file = open('Задачи\Ответ.txt', 'w')
    for i in questions:
        file.write(convert(i) + '\n')
    file.write('\nОтвет: \n')

    for i in answers:
        file.write(convert(i) + '\n')
    file.close()


def solve_puzzle(conditions, question, table):
    pass



def generate_puzzle():

    """Основное тело программы."""

    table, competed_cells = generate_ans(4, 3)
    conditions = [f'0;{len(table[0])};{len(table)}']
    questions = []
    answers = []
    possibility = '110'
    while '1' in possibility:
        possibility = check_possibility(competed_cells)
        table, competed_cells, new_condition, new_question, new_answer = create_condition(possibility, table, competed_cells)
        for i in new_condition:
            conditions.append(i)
        if len(questions) < 2:
            questions.append(new_question)
            answers.append(f'{new_question.split(";")[1]};{new_answer}')
    save_result(conditions, questions, answers)


generate_puzzle()

run = False
while run:
    time_delta = clock.tick(60) / 1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        manager.process_events(event)

    manager.update(time_delta)
    manager.draw_ui(screen)
    pygame.display.flip()
