from some_module import *


def process_items(items=[]):
    for item in items:
        print(item)
    return items


def calculate_average(numbers):
    return sum(numbers) / len(numbers)


def write_data(path, data):
    f = open(path, "w")
    f.write(str(data))


def build_callbacks():
    callbacks = []
    for i in range(3):
        callbacks.append(lambda: i)
    return callbacks
