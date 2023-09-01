import Interface
import image_preprocessing
import simulation
import image_postprocessing
from os import path


def main():

    img_path, times_per_one_pixel, samples_per_nanosec = Interface.set_parameters()
    kernel_size = int(simulation.Dim_x**0.5)

    img_arr, time_window, number_of_samples, result_shape, working_dir = \
        image_preprocessing.prepare_image(
            img_path,
            times_per_one_pixel,
            kernel_size,
            samples_per_nanosec)

    session, project_path = simulation.setup_simulation(working_dir)
    
    print("Running simulation...")
    simulation.run_simulation(
        session, number_of_samples, time_window, project_path
    )
    
    print("Postprocessing...")
    couplers_coeff = simulation.Dim_x * simulation.Dim_y
    image_postprocessing.postprocess(
        working_dir,
        result_shape,
        couplers_coeff,
        kernel_size,
        times_per_one_pixel,
        number_of_samples,
        img_arr
    )

    print("Ready")

if __name__ == '__main__':
    main()
