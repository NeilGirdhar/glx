__all__ = ['next_power_of_two']


def next_power_of_two(x):
    return 1 << (x - 1).bit_length()
