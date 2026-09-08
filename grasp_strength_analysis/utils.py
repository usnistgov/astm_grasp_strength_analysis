import csv
import os

import tkinter as tk
import numpy as np

import itertools

from scipy import signal, stats
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
from numpy import ndarray
from tkinter import filedialog, simpledialog

from models import GraspRegion, InitializationAngle, GraspAnalysisResults

class GraspAnalysisUtils:
    @staticmethod
    def select_folder() -> str:
            
            start_dir = os.path.dirname(os.getcwd())            

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
    
    @staticmethod
    def select_file() -> str:
            
            start_dir = os.path.dirname(os.getcwd()) 

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
    
    @staticmethod
    def select_desired_plots()-> list:
        root = tk.Tk()
        root.title("Plot Selection")
        root.attributes('-topmost', True)

        options = ['Raw Data Plot', 'Scatter Plot of Forces', 
                'Cumulative Mean Plot', 'Cumulative Standard Deviation Plot', 
                'Cumulative Median Plot', 'Box Plot'
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
    
    @staticmethod
    def get_initialization_parameters()-> tuple[float, float, int]:

        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)

        start_angle = simpledialog.askfloat("Initialization Parameters", "Starting angle")
        increment = simpledialog.askfloat("Initialization Parameters", "Angle increment")
        trials = simpledialog.askinteger("Initialization Parameters", "Trials per angle")

        if start_angle is None:
            raise ValueError("Starting angle must be specified")
        if not increment:
            raise ValueError("Angle increment must be specified")
        if not trials:
            raise ValueError("Trials per angle must be specified")
        
        root.quit()
        root.destroy()

        print(f"User has chosen a starting angle of {start_angle} degrees\n")
        print(f"User has chosen an angle increment of {increment} degrees\n")
        print(f"User has specified {trials} per angle increment")


        return start_angle, increment, trials
       
    @staticmethod 
    def load_and_preprocess_data(filepath: str) -> np.ndarray:
        
        matrix = np.loadtxt(open(filepath, "rb"), delimiter=",", skiprows=1)

        baselined_matrix = matrix - matrix[0,:]

        force_data = np.sum(baselined_matrix[:,[0,1,2]], axis=1)

        return force_data

    @staticmethod
    def detect_grasp_regions(force_data: np.ndarray, sample_size: int, min_force: int) -> list[GraspRegion]:
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
                                end_idx=i,
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
                            end_idx=i,
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
                end_idx=i,
                duration=i - 1 - grasp_start,
                grasp_number=n_grasps,
                max_force=0,
                avg_force=0
            )
            grasps.append(new_grasp)

        grasps = grasps[:n_grasps]

        return grasps
    
    @staticmethod
    def calculate_grasp_force(force_subset: np.ndarray, grasp: GraspRegion) -> GraspRegion:

        fs = 1000
        dt = 1/fs

        smoothed_data = signal.savgol_filter(force_subset, polyorder=3, window_length=101)
        
        orig_derivative = np.gradient(np.array(smoothed_data), dt)
        grasp.max_force = max(force_subset)

        deriv_thresh = grasp.max_force * 0.10
        idx_start = 0
        idx_end = len(force_subset)
        flag = False

        for i, _ in enumerate(orig_derivative):
            if i >= len(orig_derivative) - 20:
                break
            if np.all(abs(orig_derivative[i:i+20]) < deriv_thresh) and flag is False:
                idx_start = i
                flag = True
            if np.any(abs(orig_derivative[i:i+20]) > deriv_thresh) and flag is True:
                idx_end = i
                flag = False

        y = force_subset[idx_start:idx_end].flatten()
        x = np.arange(1, len(y) + 1)

        grasp_segment = force_subset[idx_start:idx_end]
        grasp.avg_force = float(np.mean(grasp_segment))

        return grasp
    
    @staticmethod
    def calculate_grasp_statistics(n_grasps: int, grasps: list[GraspRegion])-> tuple[float, float, float, ndarray, ndarray, ndarray, float]:
        avg_forces = [g.avg_force for g in grasps]

        mean = float(np.mean(avg_forces))
        std = float(np.std(avg_forces))
        sem = std / np.sqrt(n_grasps)
        ts = stats.t.ppf([0.025, 0.975], n_grasps-1)
        ci = mean + ts * sem
        pi = mean + ts * std * np.sqrt(1 + 1/n_grasps)
        cv_percent = std / mean * 100

        return mean, std, sem, ts, ci, pi, cv_percent
    
    @staticmethod
    def calculate_required_samples(mean: float, std: float, number_of_grasps: int)-> tuple[float, float, float, float, float, int]|None:
        z = 1.96
        s = std
        E = 0.01 * mean

        moe = z*s/np.sqrt(number_of_grasps)
        n_required = (z*s/E)**2
        n_required_buffer = (z*s*1.2/E)**2

        alpha = 0.05
        chi_lwr = float(stats.chi2.ppf(1-alpha/2, number_of_grasps-1))
        chi_upr = float(stats.chi2.ppf(alpha/2, number_of_grasps -1))

        std_dev_interval_lwr = float(np.sqrt((number_of_grasps - 1) * s**2/chi_lwr))
        std_dev_interval_upr = float(np.sqrt((number_of_grasps - 1) * s**2/chi_upr))

        for n_test in range(10,1000):
            chi_lwr_test = stats.chi2.ppf(1-alpha/2, n_test-1)
            chi_upr_test = stats.chi2.ppf(alpha/2, n_test-1)

            L = np.sqrt((n_test - 1) * s**2/chi_lwr_test)
            U = np.sqrt((n_test - 1) * s**2/chi_upr_test)

            if (U-L)/2 < E:
                n_required_std = n_test
                return moe, n_required, n_required_buffer, std_dev_interval_lwr, std_dev_interval_upr, n_required_std
        return None

    @staticmethod
    def report_results(result: GraspAnalysisResults):

        print(f"Filename: {result.filename}\n")
        print(f"Number of grasps detected: {result.number_of_grasps}\n")
        print(f"The average strength of a grasp is {round(result.mean, 2)} N")
        print(f"95% confidence interval: [{round(float(result.ci[0]), 2)}, {round(float(result.ci[1]), 2)}]")
        print(f"The standard deviation for grasp strength is {round(result.std, 2)} N")
        print(f"95% Confidence interval for standard deviation: [{round(result.std_dev_interval_lwr, 2)}, {round(result.std_dev_interval_upr, 2)}]")

        print(f"Recommended number of samples to collect: {round(result.n_required_std, 0)}\n\n")

    @staticmethod
    def create_grasp_plots(chosen_plots: list[str], force_data: np.ndarray, result: GraspAnalysisResults, grasps: list[GraspRegion]):
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

        if 'Cumulative Mean Plot' in chosen_plots:
            plt.figure()
            plt.plot(result.cumulative_avg)

            plt.title(f"Cumulative Average for all Grasps: {filename}")
            plt.xlabel("Sample Number")
            plt.ylabel("Force (N)")
            plt.grid(True)

        if 'Cumulative Standard Deviation Plot' in chosen_plots:
            plt.figure()
            plt.plot(result.cumulative_std)

            plt.title(f"Cumulative Standard Deviation for all Grasps: {filename}")
            plt.xlabel("Sample Number")
            plt.ylabel("Force (N)")
            plt.grid(True)

        if 'Cumulative Median Plot' in chosen_plots:
            plt.figure()
            plt.plot(result.cumulative_median)

            plt.title(f"Cumulative Median for all Grasps: {filename}")
            plt.xlabel("Sample Number")
            plt.ylabel("Force (N)")
            plt.grid(True)

        if 'Box Plot' in chosen_plots:
            step_size = 5
            box_indicies = range(step_size, n_grasps + 1, step_size)
            data_to_plot = [avg_force[:idx] for idx in box_indicies]

            plt.figure()
            plt.boxplot(data_to_plot, tick_labels=[str(i) for i in box_indicies])

            plt.title(f"Box Plot: {filename}")
            plt.xlabel("Sample Number")
            plt.ylabel("Force (N)")
            plt.grid(True)
    
    @staticmethod
    def analyze_initialization_angles(avg_forces: list[float], start_angle: float, increment: float, trials: int) -> tuple[float, float]:        
        average_angled_force = []
        i=0
        
        chunked_avg_forces = itertools.batched(avg_forces, trials)
        
        angle = start_angle
        avg_force_per_angle: dict[float, float] = {}
        
        max_force = 0
        max_angle = 0
        
        for chunk in chunked_avg_forces:
            avg_force = sum(chunk)/trials
            avg_force_per_angle[angle] = avg_force
            
            if avg_force > max_force:
                max_force = avg_force
                max_angle = angle
            
            angle += increment

        plt.figure()
        plt.scatter(list(avg_force_per_angle.keys()), list(avg_force_per_angle.values()))

        plt.title(f"Initialization Analysis")
        plt.xlabel("Angle (Degrees)")
        plt.ylabel("Force (N)")
        plt.grid(True)

        return max_force, max_angle
    
    @staticmethod
    def report_initialization_results(filename: str, number_of_grasps: int, max_force: float, max_angle: float):
        print(f"Filename: {filename}")
        print(f"Optimal angle: {max_angle} degrees")
        print(f"Force at optimal angle: {max_force} N")
        print(f"Number of grasps analyzed: {number_of_grasps}")
