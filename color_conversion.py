import numpy as np


def rgb_to_hex(rgb: np.ndarray) -> str:
    rgb = rgb.reshape(3)
    return '#{:02X}{:02X}{:02X}'.format(*rgb)


def hex_to_rgb(hex_str: str) -> np.ndarray:
    hex_str = hex_str.strip()

    if hex_str[0] == '#':
        hex_str = hex_str[1:]

    if len(hex_str) != 6:
        raise ValueError('Input #{} is not in #RRGGBB format.'.format(hex_str))

    r, g, b = hex_str[:2], hex_str[2:4], hex_str[4:]
    rgb = (int(n, base=16) for n in (r, g, b))
    return np.array(rgb)