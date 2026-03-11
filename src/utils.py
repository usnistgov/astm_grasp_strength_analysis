import csv
import os

import tkinter as tk
import numpy as np

from scipy import signal, stats
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
from numpy import ndarray
from tkinter import filedialog, simpledialog

from src.GraspRegion import GraspRegion
from src.GraspAnalysisResults import GraspAnaylsisResults
from src.InitializationAngle import InitializationAngle

class GraspAnalysisUtils:
    @staticmethod
    def select_folder() -> str:
            
            start_dir = os.getcwd()

            root = tk.Tk()
            root.withdraw()

            root.attributes('-topmost', True)

            folder_path = filedialog.askdirectory(initialdir=start_dir, title="Select folder containing data")
            root.destroy()

            if folder_path:
                print(f"Selected folder: {folder_path}")
            else:
                raise Exception("No data folder selected")
            
            return folder_path
    
    def select_file() -> str:
            
            start_dir = os.getcwd()

            root = tk.Tk()
            root.withdraw()

            root.attributes('-topmost', True)

            file_types = [
                ('CSV files', '*.csv')
            ]

            initialization_file = filedialog.askopenfilename(initialdir=start_dir, filetypes=file_types, title="Select file containing initialization data")
            root.destroy()

            if initialization_file:
                print(f"Selected file: {initialization_file}")
            else:
                raise Exception("No data folder selected")
            
            return initialization_file
    
    def select_desired_plots()-> list:
        root = tk.Tk()
        root.title("Plot Selection")
        root.attributes('-topmost', True)

        options = ['Raw Data Plot', 'Scatter Plot of Forces', 
                'Rolling Mean Plot', 'Rolling Standard Deviation Plot', 
                'Rolling Median Plot', 'Box Plot'
                    ]
        
        checkboxes = {}
        selected_options = []

        for option in options:
            var = tk.BooleanVar()
            chk = tk.Checkbutton(root, text=option, variable=var)
            chk.pack(anchor=tk.W, padx=20)
            checkboxes[option] = {'var': var, 'chk': chk}
    
        def get_selected_options():
            for option, data in checkboxes.items():
                if data['var'].get():
                    selected_options.append(option)

            root.quit()
            root.destroy()

        submit_btn = tk.Button(root, text="Submit", command=get_selected_options)
        submit_btn.pack(pady=10)

        root.mainloop()
        return selected_options
    
    def get_initialization_parameters(init_variables: InitializationAngle)-> list:

        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)

        start_angle = simpledialog.askfloat("Initialization Parameters", "Starting angle")
        increment = simpledialog.askfloat("Initialization Parameters", "Angle increment")
        trials = simpledialog.askfloat("Initialization Parameters", "Trials per angle")

        if not start_angle:
            raise ValueError("Starting angle must be specified")
        if not increment:
            raise ValueError("Angle increment must be specified")
        if not trials:
            raise ValueError("Trials per angle must be specified")
        
        root.quit()
        root.destroy()
        
        init_variables.starting_angle = start_angle
        init_variables.angle_increment = increment
        init_variables.trials_per_angle = trials

        print(f"User has chosen a starting angle of {start_angle} degrees\n")
        print(f"User has chosen an angle increment of {increment} degrees\n")
        print(f"User has specified {trials} per angle increment")


        return init_variables
        
    def load_and_preprocess_data(filepath: str) -> list[float]:
        
        matrix = np.loadtxt(open(filepath, "rb"), delimiter=",", skiprows=1)

        baselined_matrix = matrix - matrix[0,:]

        force_data = np.sum(baselined_matrix[:,[0,1,2]], axis=1)

        return force_data

    def detect_grasp_regions(force_data: np.ndarray, sample_size: int, min_force: int):
        max_grasps = 1000
        grasps: list[GraspRegion] = []

        n_grasps = 0
        in_grasp = False
        grasp_start = 0

        for i, point in enumerate(force_data):
            if not in_grasp:
                if point > min_force:
                    if i + sample_size <= len(force_data):
                        if np.all(force_data[i:i+sample_size] > min_force):
                            grasp_start = i
                            in_grasp = True
            else:
                if force_data[i] < min_force:
                    if i + sample_size <= len(force_data):
                        if np.all(force_data[i : i+sample_size] < min_force):
                            n_grasps = n_grasps + 1
                            new_grasp = GraspRegion(
                                start_idx=grasp_start,
                                end_idx=i - 1,
                                duration=i - 1 - grasp_start,
                                grasp_number=n_grasps,
                                max_force=0,
                                avg_force=0
                            )
                            grasps.append(new_grasp)
                            in_grasp = False

                            if n_grasps >= max_grasps:
                                break
                    else:
                        n_grasps = n_grasps + 1
                        new_grasp = GraspRegion(
                            start_idx=grasp_start,
                            end_idx=i - 1,
                            duration=i - 1 - grasp_start,
                            grasp_number=n_grasps,
                            max_force=0,
                            avg_force=0
                        )
                        grasps.append(new_grasp)
        if in_grasp and n_grasps < max_grasps:
            n_grasps = n_grasps + 1
            new_grasp = GraspRegion(
                start_idx=grasp_start,
                end_idx=i - 1,
                duration=i - 1 - grasp_start,
                grasp_number=n_grasps,
                max_force=0,
                avg_force=0
            )
            grasps.append(new_grasp)

        grasps = grasps[:n_grasps]

        return grasps
    
    def calculate_grasp_force(force_subset: list[float], grasp: GraspRegion, offset: int):

        fs = 1000
        dt = 1/fs

        smoothed_data = signal.savgol_filter(force_subset, polyorder=3, window_length=101)

        orig_derivative = np.gradient(smoothed_data, dt)
        grasp.max_force = max(force_subset)

        deriv_thresh = grasp.max_force * 0.10
        idx_end = -1
        flag = False

        for i, _ in enumerate(orig_derivative):
            if i >= len(orig_derivative) - 20:
                break
            if np.all(abs(orig_derivative[i:i+20]) < deriv_thresh) and flag is False:
                idx_start = i
                flag = True
            if np.any(abs(orig_derivative[i:i+20]) > deriv_thresh) and flag is True:
                idx_end = i

        y = force_subset[idx_start:idx_end].flatten()
        x = np.arange(1, len(y) + 1)

        x_scaled = x / np.max(x)

        def exp_model(x, A, k, C):
            return A*np.exp(-k*x) + C
        
        p0 = [np.max(y) - np.min(y), 1.0, np.min(y)]

        try:
            popt, _ = curve_fit(exp_model, x_scaled, y, p0=p0, maxfev=2000)
            A, k, C = popt

            dydx = -A * k * np.exp(-k * x_scaled)

            threshold_indicies = np.where(np.abs(dydx) < 5)[0]
            idx_start_new = threshold_indicies[0] if len(threshold_indicies) > 0 else 0

        except Exception as e:
            print(f"Fit failed: {e}")

            A, k, C = (0,0,0)
            idx_start_new = 0

        grasp_segment = force_subset[idx_start:idx_end]
        grasp.max_force = np.max(grasp_segment)
        grasp.avg_force = np.mean(grasp_segment)

        return grasp
    
    def calculate_grasp_statistics(result: GraspAnaylsisResults, grasp: GraspRegion)-> GraspAnaylsisResults:
        avg_forces = [g.avg_force for g in grasp]
        n_grasps = result.number_of_grasps

        result.mean = np.mean(avg_forces)
        result.std = np.std(avg_forces)
        result.sem = result.std / np.sqrt(n_grasps)
        result.ts = stats.t.ppf([0.025, 0.975], n_grasps-1)
        result.ci = result.mean + result.ts * result.sem
        result.pi = result.mean + result.ts * result.std * np.sqrt(1 + 1/n_grasps)
        result.cv_percent = result.std / result.mean * 100

        return result
    
    def calculate_required_samples(result: GraspAnaylsisResults)-> GraspAnaylsisResults:
        z = 1.96
        s = result.std
        E = 0.01 * result.mean

        result.moe = z*s/np.sqrt(result.number_of_grasps)
        result.n_required = (z*s/E)**2
        result.n_required_buffer = (z*s*1.2/E)**2

        alpha = 0.05
        chi_lwr = stats.chi2.ppf(1-alpha/2, result.number_of_grasps-1)
        chi_upr = stats.chi2.ppf(alpha/2, result.number_of_grasps -1)

        result.std_dev_interval_lwr = np.sqrt((result.number_of_grasps - 1) * s**2/chi_lwr)
        result.std_dev_interval_upr = np.sqrt((result.number_of_grasps - 1) * s**2/chi_upr)

        for n_test in range(10,1000):
            chi_lwr_test = stats.chi2.ppf(1-alpha/2, n_test-1)
            chi_upr_test = stats.chi2.ppf(alpha/2, n_test-1)

            L = np.sqrt((n_test - 1) * s**2/chi_lwr_test)
            U = np.sqrt((n_test - 1) * s**2/chi_upr_test)

            if (U-L)/2 < E:
                result.n_required_std = n_test
                return result

    def report_results(result: GraspAnaylsisResults, grasps: list[GraspRegion]):

        print(f"Filename: {result.filename}\n")

        print(f"The average strength of a grasp is {round(result.mean, 2)} N")
        print(f"The standard deviation for grasp strength is {round(result.std, 2)} N")
        print(f"Coefficient of variation: {round(result.cv_percent, 2)}")
        print(f"95% confidence interval: [{round(float(result.ci[0]), 2), round(float(result.ci[1]), 2)}]")
        print(f"95% prediction interval: [{round(float(result.pi[0]), 2), round(float(result.pi[1]), 2)}]\n")

        max_forces = [g.max_force for g in grasps]

        print(f"Average peak force: {round(np.mean(max_forces), 2)} N")
        print(f"Number of grasps detected: {result.number_of_grasps}\n")

        print(f"Margin of error: {round(result.moe,2)} N")
        print(f"Recommended number of samples to collect: {round(result.n_required, 0)}")
        print(f"Recommended number of samples (with buffer): {round(result.n_required_buffer, 0)}\n")

        print(f"95% Confidence interval for standard deviation: [{round(result.std_dev_interval_lwr, 2)}, {round(result.std_dev_interval_upr, 2)}]")
        print(f"Recommended number of samples to collect based on standard deviation: {round(result.n_required_std, 0)}\n\n")


    def create_grasp_plots(chosen_plots: list[str], force_data: np.ndarray, result: GraspAnaylsisResults, grasps: list[GraspRegion]):
        avg_force = [g.avg_force for g in grasps]
        filename = result.filename
        n_grasps = result.number_of_grasps

        if 'Raw Data Plot' in chosen_plots:
            plt.figure()
            plt.plot(force_data)

            plt.title(f"Raw Data Plot: {filename}")
            plt.xlabel(f"Time (ms)")
            plt.ylabel(f"Force (N)")
            plt.grid(True)

        if 'Scatter Plot of Forces' in chosen_plots:
            x = np.arange(1, len(grasps) + 1)

            plt.figure()
            plt.scatter(x, avg_force)

            plt.title(f"Scatter Plot: {filename}")
            plt.xlabel("Sample Number")
            plt.ylabel("Force (N)")
            plt.grid(True)

        if 'Rolling Mean Plot' in chosen_plots:
            plt.figure()
            plt.plot(result.rolling_avg)

            plt.title(f"Rolling Average for all Grasps: {filename}")
            plt.xlabel("Sample Number")
            plt.ylabel("Force (N)")
            plt.grid(True)

        if 'Rolling Standard Deviation Plot' in chosen_plots:
            plt.figure()
            plt.plot(result.rolling_std)

            plt.title(f"Rolling Standard Deviation for all Grasps: {filename}")
            plt.xlabel("Sample Number")
            plt.ylabel("Force (N)")
            plt.grid(True)

        if 'Rolling Median Plot' in chosen_plots:
            plt.figure()
            plt.plot(result.rolling_median)

            plt.title(f"Rolling Median for all Grasps: {filename}")
            plt.xlabel("Sample Number")
            plt.ylabel("Force (N)")
            plt.grid(True)

        if 'Box Plot' in chosen_plots:
            step_size = 5
            box_indicies = list(range(step_size, n_grasps + 1, step_size))
            data_to_plot = [avg_force[:idx] for idx in box_indicies]

            plt.figure()
            plt.boxplot(data_to_plot, label=box_indicies)

            plt.title(f"Box Plot: {filename}")
            plt.xlabel("Sample Number")
            plt.ylabel("Force (N)")
            plt.grid(True)
    
    def analyze_initialization_angles(avg_forces: list[float], init_params: InitializationAngle, n_grasps: float):
        angle_increment = init_params.angle_increment
        starting_angle = init_params.starting_angle
        trials_per_angle = init_params.trials_per_angle

        average_angled_force = []
        i=0

        while i < len(avg_forces):
            angled_sum = 0
            for j in range(int(trials_per_angle)):
                angled_sum = angled_sum + avg_forces[int(i+j)]
            average_angled_force.append(int(angled_sum/trials_per_angle))
            i += trials_per_angle

        num_elements = int(n_grasps//trials_per_angle)
        grasp_angle_labels = [starting_angle + i * angle_increment for i in range(num_elements)]

        plt.figure()
        plt.scatter(grasp_angle_labels, average_angled_force)

        plt.title(f"Initialization Analysis")
        plt.xlabel("Angle (Degrees)")
        plt.ylabel("Force (N)")
        plt.grid(True)

        init_params.angles = grasp_angle_labels
        init_params.avg_forces_by_angle = average_angled_force
        init_params.max_force = max(average_angled_force)
        init_params.max_angle = grasp_angle_labels[int(np.argmax(average_angled_force))]

        return init_params
    
    def report_initialization_results(result: GraspAnaylsisResults,init_params: InitializationAngle):
        print(f"Filename: {result.filename}")
        print(f"Optimal angle: {init_params.max_angle} degrees")
        print(f"Force at optimal angle: {init_params.max_force} N")
        print(f"Number of grasps analyzed: {result.number_of_grasps}")
