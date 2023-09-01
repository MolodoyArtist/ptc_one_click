from image_preprocessing import *
import simulation
from PIL import Image
from os import mkdir, listdir, remove


def _read_array_from_source_file(path: PathLike, number_of_samples: int, times_per_one_pixel: int = 10) -> np.ndarray:
    """Счтывает массив из файла, который получается на выходе из оптической схемы и возращает его"""

    from_source = np.genfromtxt(path)

    number_of_samples -= 20

    from_source = from_source[:number_of_samples, 1]

    ready_to_unflat = np.split(
        from_source, from_source.shape[0] // times_per_one_pixel)

    percent_otstup = 0.2

    otstup = int(times_per_one_pixel * percent_otstup)

    final_array = np.array([np.sum(arr[otstup: -otstup]) /
                           (times_per_one_pixel - 2*otstup) for arr in ready_to_unflat])

    return final_array


def make_convolution(img: np.ndarray, kernel: np.ndarray) -> np.ndarray:
    """Функция, производящая свертку без использования сторонних программных пакетов"""

    img_tensor = tensor_for_convolution(img, kernel_size=kernel.shape[0])

    result = np.sum(img_tensor * kernel, axis=(1, 2)).reshape(
        (img.shape[0] - kernel.shape[0] + 1, img.shape[0] - kernel.shape[0] + 1))

    return result


def make_img_from_arr(path, result_shape, couplers_coeff, kernel_size, times_per_one_pixel, number_of_samples, img_arr):

    final_arr = _read_array_from_source_file(path, number_of_samples,  times_per_one_pixel).reshape(
        (result_shape[0] - kernel_size + 1, result_shape[0] - kernel_size + 1))

    # 4.94e-6 - average noise
    # 255 - pic scale
    # 100 - laser power scale

    final_arr = (final_arr) * 100 * couplers_coeff
    to_img = np.around(final_arr) * 255 * 2 - \
        make_convolution(img_arr, np.ones((kernel_size, kernel_size)))

    to_img[to_img < 0] = 0
    to_img[to_img > 255] = 255

    return to_img


def create_result_folder(working_dir):

    result_path = path.join(working_dir, "result_images")
    if not path.isdir(result_path):
        mkdir(result_path)
    else:
        files = listdir(result_path)
        for f in files:
            remove(path.join(result_path, f))

    return result_path


def postprocess(working_dir, result_shape, couplers_coeff, kernel_size, times_per_one_pixel, number_of_samples, img_arr):

    result_path = create_result_folder(working_dir)

    for i in range(1, simulation.Dim_y + 1):

        img = make_img_from_arr(
            path.join(working_dir, "output_folder", f"output{i}.txt"),
            result_shape,
            couplers_coeff,
            kernel_size, times_per_one_pixel,
            number_of_samples, img_arr
        )
        img = Image.fromarray(img.astype(np.uint8), mode='L')
        img.save(path.join(result_path, f"filter{i}.png"))
