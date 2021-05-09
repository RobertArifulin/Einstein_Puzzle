import string
WIDTH = 500  # ширина игрового окна
HEIGHT = 700  # высота игрового окна
FPS = 60  # частота кадров в секунду

BUTTON_SIZE = (250, 50)
INPUT_SIZE = (50, 50)

WHITE_LIST = [i for i in string.digits]

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BG_COLOR = (247, 247, 249, 255)
LABEL_COLOR = (230, 230, 230, 255)

LETTERS = [i for i in string.ascii_letters]
LETTERS.extend(['a' + i for i in string.ascii_letters])

# l1 = [[['1a'], ['1b'], ['1c'], ['1d']], [['2d'], ['2b'], ['2a'], ['2c']], [['3a'], ['3b'], ['3c'], ['3d']]]
# l2 = [[['1a'], ['1b'], ['1d'], ['1c']], [['2a'], ['2b'], ['2c'], ['2d']], [['3d'], ['3c'], ['3b'], ['3a']]]
# l3 = [[['1a'], ['1b'], ['1c'], ['1d']], [['2d'], ['2b'], ['2a'], ['2c']], [['3a'], ['3b'], ['3c'], ['3d']]]
