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
screen.fill(tp.white)

start_b = pgui.elements.UIButton(relative_rect=pygame.Rect((125, 20), tp.button_size),
                                 text='Начать',
                                 manager=manager)

width_input = pgui.elements.UITextEntryLine(relative_rect=pygame.Rect((200, 90), tp.input_size),
                                            manager=manager)
height_input = pgui.elements.UITextEntryLine(relative_rect=pygame.Rect((200, 160), tp.input_size),
                                             manager=manager)

width_input.set_allowed_characters(tp.white_list)
height_input.set_allowed_characters(tp.white_list)
width_input.set_text_length_limit(2)
height_input.set_text_length_limit(2)


def start_bf():
    start_b.disable()
    width_input.disable()
    height_input.disable()


def generate_ans(width, height):
    """Генерируем заполненую таблицу"""
    table = [[] for _ in range(height)]
    for i in range(width - 1):
        letters = [i for i in tp.letters[:width]]
        table[i] = [[f'{i + 1}{letters.pop(random.randint(1, len(letters)) - 1)}'] for _ in range(width)]
    completed_cells = []
    for x in range(width):
        completed_cells.append([])
        for y in range(height):
            completed_cells[-1].append(y)

    return table, completed_cells


def check_possibility(completed_cells):  # переделать на проверку каждого типа
    n = 0
    result = False
    for i in range(len(completed_cells)):
        if len(completed_cells[i]) >= 2:
            result = True
            n += len(completed_cells[i])
        elif i and completed_cells[i] and completed_cells[i - 1]:
            result = True
            n += len(completed_cells[i])
        else:
            n += len(completed_cells[i])
    if n < 3:
        return False
    return result


def create_condition(possibility, table, completed_cells):
    height = len(table)
    width = len(table[0])
    print(completed_cells)
    print(table)
    print(possibility)
    if possibility:
        roll = random.random()
        if roll >= 0.25:
            x = random.randint(0, width - 1)
            while len(completed_cells[x]) < 2:
                x = random.randint(0, width - 1)
            y2 = completed_cells[x].pop(random.randint(0, len(completed_cells[x]) - 1))
            y1 = completed_cells[x][random.randint(0, len(completed_cells[x]) - 1)]
            k1, k2 = table[y1][x][0], table[y2][x][0]
            new_condition = f'{k1} вместе с {k2}'
            for i in range(width):
                print(k2)
                table[y2][i].append(k2)

        else:
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
                place = 'слева'
            else:
                place = 'справа'
            k1, k2 = table[y1][x1][0], table[y2][x1][0]
            new_condition = f'дом с {k1} {place} от дома с {k2}'
            for i in range(width):
                table[y2][i].append(k2)
    if not possibility:
        go = True
        while go:
            x = random.randint(0, width - 1)
            while not completed_cells[x]:
                x = random.randint(0, width - 1)
            y = completed_cells[x].pop(random.randint(0, len(completed_cells[x]) - 1))
            k = table[y][x][0]
            new_condition = f'дом {x} c {k}'
            for i in range(width):
                table[x][i].append(k)
            go = False
            for i in completed_cells:
                if i:
                    go = True
    return table, new_condition, completed_cells


def generate_puzzle():
    table, competed_cells = generate_ans(4, 3)
    print(table)
    conditions = []
    possibility = True
    while possibility:
        possibility = check_possibility(competed_cells)
        table, new_condition, competed_cells = create_condition(possibility, table, competed_cells)
        conditions.append(new_condition)


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
