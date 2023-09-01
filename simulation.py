import numpy as np
import importlib.util
from typing import TypeVar
from os import path, mkdir

PathLike = TypeVar('PathLike')
LumericalSession = TypeVar("LumericalSession")

spec_win = importlib.util.spec_from_file_location(
    'lumapi', 'C:\\Program Files\\Lumerical\\v202\\api\\python\\lumapi.py')
lumapi = importlib.util.module_from_spec(spec_win)
spec_win.loader.exec_module(lumapi)


Matrix = np.array([
    [0., 1., 1., 0.],
    [0.5, 1., 0.5, 0.],
    [1., 1., 0., 0.],
    [0., 0.5, 1., 0.5],
    [0.5, 0.5, 0.5, 0.5],
    [1., 0.5, 0., 0.5],
    [0., 0., 1., 1.],
    [0.5, 0., 0.5, 1.],
    [1., 0., 0., 1.]
])
Dim_x, Dim_y = Matrix.shape

def create_folder_for_output(working_dir):
    output_dir = path.join(working_dir, 'output_folder')

    if not path.isdir(output_dir):
        mkdir(output_dir)

def setup_simulation(working_dir: PathLike) -> tuple[LumericalSession, PathLike]:


    h = lumapi.open("interconnect")
    project_path = path.join(working_dir, "PTC.icp")
    lumapi.evalScript(h, f'load("{project_path}");')

    lumapi.evalScript(h, '''
            switchtodesign;             # renew file
            deleteall;
            closeall;  
        ''')

    lumapi.putMatrix(h, "Input_Matrix", Matrix)
    lumapi.putDouble(h, "Dim_x", Dim_x)
    lumapi.putDouble(h, "Dim_y", Dim_y)

    filter_cutoff = 0.8
    amplif_cutoff = 1.0
    lumapi.putDouble(h, "fltr_cutoff", filter_cutoff)
    lumapi.putDouble(h, "amplf_cutoff", amplif_cutoff)

    with open("lumerical_script.txt", "r") as script_file:

        lumerical_script = script_file.read()

    lumapi.evalScript(h, lumerical_script)

    create_folder_for_output(working_dir)
    return h, project_path


def run_simulation(lumerical_session, number_of_samples, time_window, project_path):

    lumapi.putDouble(lumerical_session, "time_window", time_window)
    lumapi.putDouble(lumerical_session, "number_of_samples", number_of_samples)

    lumapi.evalScript(lumerical_session, '''   
            switchtodesign;                       
            setnamed("::Root Element","time window", time_window);
            setnamed("::Root Element","number of samples", number_of_samples);
            setnamed("::Root Element","number of threads", 8);
            setnamed("::Root Element", "monitor data", "save to memory");
            
        ''')
    lumapi.evalScript(lumerical_session, f'save("{project_path}");')
    lumapi.evalScript(lumerical_session, "run;")
    
