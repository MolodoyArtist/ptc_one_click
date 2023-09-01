import multiprocessing
from os import path, mkdir
import numpy as np
from PIL import Image
from typing import TypeVar
PathLike = TypeVar('PathLike')


def tensor_for_convolution(img: np.matrix, kernel_size: int) -> np.ndarray:
    """ Функция делает из двумерного массива тензор размера (kernel_size)**2 * (img.shape[0] - kernel_size + 1) """

    tensor = np.zeros(
        ((img.shape[0] - kernel_size + 1) ** 2, kernel_size, kernel_size)
    )

    cur_x = 0
    cur_y = 0

    while cur_y + kernel_size <= img.shape[0]:

        while cur_x + kernel_size <= img.shape[0]:
            tensor[cur_y * (img.shape[0] - kernel_size + 1) + cur_x] = \
                img[cur_y: cur_y + kernel_size, cur_x: cur_x + kernel_size]

            cur_x += 1

        cur_y += 1
        cur_x = 0

    return tensor


def img_to_2D_array(path: PathLike, result_shape: tuple | list = None) -> tuple[np.ndarray, tuple, Image.Image]:
    """Принимает путь к картинке и создает из нее двумерный массив
    размера result_shape если он указана, либо исходного размера в противном случае"""

    img = Image.open(path)
    img_arr = np.asarray(img)

    shape = img_arr.shape
    if len(shape) == 2:
        x, y = shape

    else:
        x, y, *rest = shape

        img_arr = img_arr[:, :, 1]

    x_gap = y_gap = y_step = x_step = 0
    if result_shape is not None:

        # Обрезаем картинку в соответствии с result_shape
        if x % 2 != 0:
            x_step = 1

        if y % 2 != 0:
            y_step = 1

        if result_shape[0] < x:
            x_gap = (x - result_shape[0]) // 2

        if result_shape[0] < y:
            y_gap = (y - result_shape[1]) // 2

    else:
        result_shape = x, y

    img_arr = img_arr[x_gap: x - x_step - x_gap, y_gap: y - y_step - y_gap]
    img_to_show = Image.fromarray(img_arr.astype(np.uint8))

    return img_arr, result_shape, img_to_show


def _write_array_to_source_file(
        full_source_path: PathLike,
        array: np.ndarray,
        times_per_one_pixel: int,
        simulation_time: float):
    """Принимает на вход массив и путь к файлу.
    Записывает в файл пары вида (время, значение).
    Каждое значение из массива делится на 255 и записывается в файл по times_per_one_pixel раз
    В конец приписывается еще 20 раз последнее значение с целью 
    возместить потерянные во время симуляции сэмплы"""
    with open(full_source_path, 'w') as file:
        array /= 255

        times = np.linspace(0, simulation_time,
                            times_per_one_pixel * array.shape[0] + 20)

        current_pix = -1

        for num, elem in enumerate(times):
            elem = float(elem)
            if num % times_per_one_pixel == 0:
                current_pix += 1
            try:
                print(f'{elem} {array[current_pix]}', file=file)

            except IndexError:
                print(f'{elem} {array[-1]}', file=file)


def write_img_to_source_files(directory_path: PathLike,
                              img: np.ndarray, kernel_size: int,
                              times_per_one_pixel: int = 10,
                              simulation_time: float = 1e-6) -> int:
    """Получает на вход двумерный массив и записывает его в элементы в различные файлы,
    соответствующие алгоритму разбиения картинки для разных лазеров"""

    matrices = tensor_for_convolution(img, kernel_size)
    sources_path = path.join(directory_path, "sources_folder")
    if not path.isdir(sources_path):
        mkdir(sources_path)

    procs = []
    for i in range(kernel_size):
        for j in range(kernel_size):

            array_for_file = matrices[:, i, j]
            full_source_path = path.join(
                sources_path, f"source{i * kernel_size + j + 1}.txt"
            )
            print(full_source_path, "processing...")

            p = multiprocessing.Process(
                target=_write_array_to_source_file,
                args=(full_source_path, 
                      array_for_file, 
                      times_per_one_pixel, 
                      simulation_time)
            )
            procs.append(p)
            p.start()

    for proc in procs:
        proc.join()

    number_of_samples, simulation_time = times_per_one_pixel * \
        array_for_file.shape[0] + 20, simulation_time

    return number_of_samples


def prepare_image(img_path: PathLike, times_per_one_pixel: int, kernel_size: int, samples_per_nanosec: int) -> tuple[np.ndarray, int, tuple[int, int]]:
    """Функция, запускаемая перед симуляцией.
    Картинка преобразуется в двумерный массив и записывается в файлы.
    После чего на экран выводится сама исходная картинка и печатаются параметры,
    необходимые для работы программного пакета Lumerical Interconnect"""

    img_arr, result_shape, show_img = img_to_2D_array(img_path)
    result_shape = img_arr.shape

    working_dir = path.dirname(img_path)
    simulation_time = 1e-9 * times_per_one_pixel * \
        (result_shape[0] - kernel_size + 1)**2 / samples_per_nanosec

    number_of_samples = write_img_to_source_files(
        working_dir, img_arr, kernel_size, times_per_one_pixel, simulation_time)

    samples_per_nanosec = number_of_samples / simulation_time / 1e9

    show_img.show()

    return img_arr, simulation_time, number_of_samples, result_shape, working_dir
