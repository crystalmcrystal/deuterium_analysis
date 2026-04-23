from pathlib import Path
import pandas as pd
from scipy.signal import find_peaks, peak_widths
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import numpy as np
import colorsys
import os

# Dict to map Balmer spectral lines to correlated expected wavelengths to index
balmer_lines = {"Delta": 410, "Gamma": 434, "Beta": 486, "Fulcher": 590, "Alpha": 656}
# Product of integration time and scans to average
trial_time_product = 500

# Example file name: deutdg_200ms_20_SR4014911__0__16-45-59-520.csv,
# where 200 is integration time, 20 is scans to average
folder = Path("/home/mouesla/PythonScripts/ECRDissociator/ECR_Plasma_Test_Calibrated/")
results_path = f"{folder}_plots/Fit_Results.txt"
open(results_path, "w").close() # w - write, a - append


# H - offset, A - height of curve peak, x0 - peak center position, sigma - stddev (RMS width) of the bell shape
def gauss(data, H, A, x0, sigma):
    return H + A * np.exp(-(data - x0) ** 2 / (2 * sigma ** 2))

def is_saturated(width_middle, width_top):
    if width_top / width_middle > 0.5:
        return True
    return False

class Trial:
    def __init__(self, file, saturation_line=None):
        self.file = file
        self.saturation_line = saturation_line
        '''print("Warning: scans to average temporarily hardcoded to 10")'''
        self.scans_to_average = 10
        '''End of the filename usually dictates the independent parameter to normalize by'''
        # Integration time, Power, Magnet Current, etc.
        self.name, self.power = self.parse_filename()
        self.data = self.read_data()

        self.peak_names, self.peak_indices, \
        self.peak_wavelengths, self.peak_intensities, \
        self.widths_middle, self.widths_top, \
        self.saturated = self.find_peaks()
        
        self.H_params, self.H_param_errors, \
        self.A_params, self.A_param_errors, \
        self.x0_params, self.x0_param_errors, \
        self.sigma_params, self.sigma_param_errors = self.fit_balmer_lines()

    def parse_filename(self):
        #parts = self.file.stem.split('_')
        parts = [p for p in self.file.stem.split('_') if p]
        if len(parts) >= 2:
            name = parts[0]
            power = int(parts[-1][:-1]) 
            return name, power
        else:
            raise ValueError(f"Unexpected filename format: {self.file}")
        
    def read_data(self, skiprows=14):
        data = pd.read_csv(self.file.resolve(), skiprows=skiprows, sep='\t', header=None)
        #data = pd.read_csv(self.file.resolve(), skiprows=skiprows)
        data.columns = ['Wavelength', 'Intensity']
        #print(data.head())
        #print(data.shape)
        return data

    def balmer_line_window(self, line, range_size):
        half_range_size = range_size / 2
        balmer_wavelength = balmer_lines[line]
        window_start = balmer_wavelength - half_range_size
        window_end = balmer_wavelength + half_range_size
        data_window = self.data.loc[(self.data['Wavelength'] >= window_start) & (self.data['Wavelength'] <= window_end)]
        return data_window

    def find_peaks(self):
        names = []; indices = []
        wavelengths = []; intensities = []
        widths_middle = []; widths_top = []
        saturated = []
        for name, _ in balmer_lines.items():
            data_window = self.balmer_line_window(line=name, range_size=10)
            if data_window.empty:
                continue
            # Find the index with the max intensity, this is a peak
            peak_index = int(data_window['Intensity'].idxmax())
            peak_wavelength = data_window['Wavelength'][peak_index]
            peak_intensity = data_window['Intensity'][peak_index]
            assert peak_intensity == data_window['Intensity'].max(), "Indexmax should yield the max"
            
            # Chooses the relative height at which the peak width is measured as a percentage of its prominence. 
            width_middle = peak_widths(self.data['Intensity'], [peak_index], rel_height=0.5)[0][0]
            width_top = peak_widths(self.data['Intensity'], [peak_index], rel_height=0.05)[0][0]
            
            names.append(name); indices.append(peak_index)
            wavelengths.append(peak_wavelength); intensities.append(peak_intensity)
            widths_middle.append(width_middle); widths_top.append(width_top)
            saturated.append(is_saturated(width_middle, width_top))
        return (names, indices, wavelengths, intensities, widths_middle, widths_top, saturated)

    def graph_raw(self):
        data_graph = self.data.loc[(self.data['Wavelength'] >= 380) & (self.data['Wavelength'] <= 700)]
        plt.figure(figsize=(10, 6))
        plt.title("Detected Emission Peaks in Hydrogen Spectrum (Power: {}W, Integration Time: {}s)".format(self.power, trial_time_product/self.scans_to_average))
        plt.plot(data_graph['Wavelength'], data_graph['Intensity'], label="Intensity vs. Wavelength", color="k")
        plt.axhline(y=self.saturation_line, color='red', linestyle=':', linewidth=1.5)
        plt.xlabel('Wavelength [nm]')
        if "RelativeIrradiance" in self.name:
            plt.ylabel('Irradiance [Relative]')
        elif "SR4" in self.name:
            plt.ylabel('Intensity [Counts]')
        plt.yscale('log')
        for i, (name, x, y) in enumerate(zip(self.peak_names, self.peak_wavelengths, self.peak_intensities)):
            color = 'red' if self.saturated[i] else 'blue'
            plt.plot(x, y, "x", color=color)
            plt.text(x, y, name, fontsize=12, ha='right', va='bottom')
            with open(results_path, "a") as f:
                # < - Left Align, > - Right Align, .3f - Float Decimal digits
                f.write("{:<4}:\nWavelength: {:>4.3f} [nm], Peak Intensity: {:>4.3f} [Counts]\n".format(name, x, y))
                f.write("Middle Width: {:>4.3f}, Top Width: {:>4.3f}, Saturated: {:>4}\n".format(self.widths_middle[i], self.widths_top[i], str(self.saturated[i])))
        with open(results_path, "a") as f: f.write("\n")
        plt.savefig("{}_plots/Hydrogen_Spectrum_{}W_{}s.pdf".format(folder, self.power, int(trial_time_product/self.scans_to_average)))
        #plt.show()
        plt.close()

    def balmer_fit_window(self, line, range_size=40):
        try:
            peak_index = self.peak_names.index(line)
            half_range_size = range_size / 2
            start = int(self.peak_indices[peak_index] - half_range_size)
            end = int(self.peak_indices[peak_index] + half_range_size)
            return (start, end)
        except ValueError:
            print("No peak found for {}".format(line))
            return None
        
    def fit_balmer_lines(self):
        H_params = []; H_param_errors = []
        A_params = []; A_param_errors = []
        x0_params = []; x0_param_errors = []
        sigma_params = []; sigma_param_errors = []
        for line in self.peak_names:
            try:
                peak_index = self.peak_names.index(line)
                # H, A, x0, sigma
                guess = [0, self.peak_intensities[peak_index], self.peak_wavelengths[peak_index], 1]
                start, end = self.balmer_fit_window(line)
                params, covariance = curve_fit(gauss, self.data['Wavelength'][start:end], self.data['Intensity'][start:end], guess)
                (H, A, x0, sigma) = params
                (H_error, A_error, x0_error, sigma_error) = np.sqrt(np.diag(covariance))
                #return (H, H_error, A, A_error, x0, x0_error, sigma, sigma_error)
            except ValueError:
                print("No peak found for {}".format(line))
                return None
            H_params.append(H); H_param_errors.append(H_error)
            A_params.append(A); A_param_errors.append(A_error)
            x0_params.append(x0); x0_param_errors.append(x0_error)
            sigma_params.append(sigma); sigma_param_errors.append(sigma_error)
        return (H_params, H_param_errors, A_params, A_param_errors, x0_params, x0_param_errors, sigma_params, sigma_param_errors)

    def plot_all_fits(self):
        fig, axes = plt.subplots(2, 3, figsize=(12, 12))
        axes = axes.flatten()
        fig.suptitle("Gaussian Fits for Balmer spectra: Power: {}W, Integration Time: {}s".format(self.power, trial_time_product/self.scans_to_average))
        for i, line in enumerate(self.peak_names):
            ax = axes[i]
            start, end = self.balmer_fit_window(line)
            ax.plot(self.data['Wavelength'][start:end], self.data['Intensity'][start:end], label="Data", color="k")
            ax.plot(self.data['Wavelength'][start:end], gauss(self.data['Wavelength'][start:end], self.H_params[i], self.A_params[i], self.x0_params[i], self.sigma_params[i]), label="Fit", color="#d534eb")
            ax.set_title("{} Line".format(line))
            ax.set_xlabel('Wavelength [nm]');
            if "RelativeIrradiance" in self.name:
                ax.set_ylabel('Irradiance [Relative]')
            elif "SR4" in self.name:
                ax.set_ylabel('Intensity [Counts]')
            ax.legend(); ax.grid(True)
            with open(results_path, "a") as f:
                # 6 characters, 4 sig figs in general format
                f.write("{:<4} Gauss Fit (H, A, x0, sigma):\nParams:    {:>6.4g}, {:>6.4g}, {:>6.4g}, {:>6.4g}\nErrors:    {:>6.4g}, {:>6.4g}, {:>6.4g}, {:>6.4g}\n".format(line, self.H_params[i], self.A_params[i], self.x0_params[i], \
                self.sigma_params[i], self.H_param_errors[i], self.A_param_errors[i], self.x0_param_errors[i], self.sigma_param_errors[i]))
        with open(results_path, "a") as f: f.write("\n")
        # Hide unused subplots
        for j in range(len(self.peak_names), len(axes)):
            axes[j].axis("off")       
        plt.savefig("{}_plots/Balmer_Fits_{}W_{}s.pdf".format(folder, self.power, int(trial_time_product/self.scans_to_average)))
        #plt.show()
        plt.close()
    '''
    def plot_sigma_vs_wavelength(self):
        plt.figure(figsize=(12, 6))
        plt.title("Gaussian Fit Sigmas vs Wavelength for Power: {}W, Integration Time: {}s".format(self.power, (trial_time_product/self.scans_to_average)))
        plt.xlabel('Wavelength [nm]'); plt.ylabel('Sigma [Counts]')
        for i, (name, x, y) in enumerate(zip(self.peak_names, self.x0_params, self.sigma_params)):
            # Color red if saturated value is true
            color = 'red' if self.saturated[i] else 'blue'
            plt.errorbar(self.x0_params[i], self.sigma_params[i], yerr=self.sigma_param_errors[i], fmt='o', label="Errors", color=color)
            plt.text(x, y, name, fontsize=12, ha='right', va='bottom')
        plt.savefig("{}_plots/GaussianSigma_{}W_{}s.pdf".format(folder, self.power, int(trial_time_product/self.scans_to_average)))
        #plt.show()
        plt.close()
    '''
    def area_under_balmer_line(self, line):
        try:
            start, end = self.balmer_fit_window(line)
            # return np.trapz(self.data['Intensity'][start:end], self.data['Wavelength'][start:end])
            #return self.data['Intensity'][start:end].sum()             
            # Changed from finding actual area to averaging the heights on the curves by dividing by number of bins
            return self.data['Intensity'][start:end].sum() / len(self.data['Intensity'][start:end])
            #return self.data['Intensity'][start:end].sum()*(trial_time_product)/(self.power)
        except ValueError:
            print("No peak found for {}".format(line))
            return None
        
class Experiment:
    def __init__(self, folder, saturation_line=None):
        self.folder = folder
        os.makedirs("{}_plots".format(self.folder), exist_ok=True)
        self.trials = []
        self.saturation_line = saturation_line
        for file in Path(self.folder).iterdir():
            #print(file)
            if not file.suffix.lower() in (".txt", ".csv", ".xlsx"):
                continue
            if file.is_file():
                trial = Trial(file, saturation_line)
                self.trials.append(trial)
        self.trials = sorted(self.trials, key=lambda t: t.power)
        self.colors = self.get_colors()
                
    def graph_all(self):
        for t in self.trials:
            with open(results_path, "a") as f:
                f.write("File Name: {}\n".format(t.file))
            t.graph_raw()
            t.plot_all_fits()
            #t.plot_sigma_vs_wavelength()
            
    def get_colors(self):
        num_colors = len(self.trials)
        return [colorsys.hsv_to_rgb(i / num_colors, 0.8, 0.9) for i in range(num_colors)]


    def graph_all_balmer_lines_combined(self, range_size, normalized=False, trials=None, zoom=False):
        lines = list(balmer_lines.keys())  # e.g. ["Alpha", "Beta", ...]
        n = len(lines)
        fig, axes = plt.subplots(2, 3, figsize=(12, 10))
        axes = axes.flatten()
        fig.suptitle(f"Balmer Lines per Power Scans {'Normalized' if normalized else ''} {'Zoomed' if zoom else ''}")
        plot_trials = self.trials
        if trials:
            plot_trials = [t for t in plot_trials if t.power in trials]
        for i, line in enumerate(lines):
            ax = axes[i]
            average_peak = 0
            for t, color in zip(plot_trials, self.colors):
                balmer_range = t.balmer_line_window(line, range_size)
                if normalized:
                    y = balmer_range['Intensity'] / t.power
                    ax.plot(balmer_range['Wavelength'], y, label=f"{t.power}W", color=color)
                    if zoom:
                        average_peak += y.max()
                else:
                    ax.plot(balmer_range['Wavelength'], balmer_range['Intensity'], label=f"{t.power}W", color=color)
                    try:
                        peak_index = t.peak_names.index(line)
                        ax.plot(t.peak_wavelengths[peak_index], t.peak_intensities[peak_index], "x", color="r")
                    except ValueError:
                        pass
            # Labels per subplot
            ax.set_title(line)
            ax.set_xlabel("Wavelength [nm]"); ax.set_ylabel("Intensity [Counts]")
            ax.grid(True)
            # Zoom handling
            if normalized and zoom and len(plot_trials) > 0:
                average_peak /= len(plot_trials)
                ax.set_ylim(average_peak * 0.7, average_peak * 1.3)
        # Hide unused subplots
        for j in range(n, len(axes)):
            axes[j].axis("off")
        # Single legend (cleaner)
        handles, labels = axes[0].get_legend_handles_labels()
        fig.legend(handles, labels, loc="upper right")
        plt.tight_layout(rect=[0, 0, 1, 0.95])
        plt.savefig(f"{self.folder}_plots/Balmer_Lines_All" f"{'_normalized' if normalized else ''}.pdf")
        plt.close()
    
    '''
    # Individual plots
    def graph_balmer_line_combined(self, balmer_line, range_size, normalized=False, trials=None, zoom=False):
        plt.figure(figsize=(10, 6))
        title = "Balmer Line {}{}{}".format(balmer_line, " Normalized" if normalized else "", " Zoomed" if zoom else "")
        plt.title(title)
        plot_trials = self.trials
        average_peak = 0
        if trials:
            plot_trials = [t for t in plot_trials if t.power in trials]
        for i, (t, color) in enumerate(zip(plot_trials, self.colors)):
            balmer_range = t.balmer_line_window(balmer_line, range_size)
            if normalized:
                plt.plot(balmer_range['Wavelength'], balmer_range['Intensity'] / t.power, label="{}W".format(t.power), color=color)
                if zoom:
                    peak = balmer_range['Intensity'].max() / t.power
                    average_peak += peak
                    # single_peak_average = balmer_range['Intensity'].sum() / len(balmer_range['Intensity'])
                    # average_peak += single_peak_average
            else:
                plt.plot(balmer_range['Wavelength'], balmer_range['Intensity'], label="{}W".format(t.power), color=color)
            plt.xlabel('Wavelength [nm]')
            plt.ylabel('Intensity [Counts]')

            if not normalized:
                try:
                    peak_index = t.peak_names.index(balmer_line)
                    plt.plot(t.peak_wavelengths[peak_index], t.peak_intensities[peak_index], "x", color="r")
                except ValueError:
                    print("No peak found for {}".format(balmer_line))
        if normalized and zoom:
            average_peak /= len(plot_trials)
            plt.set_ylim(average_peak * .7, average_peak * 1.3)
        plt.legend()
        plt.savefig("{}_plots/{}_{}{}.pdf".format(self.folder, title.replace(" ", "_"), "_".join(map(str, trials)) if trials else "all_trials", "_normalized" if normalized else ""))
        #plt.show()
        plt.close()

    def graph_all_balmer_lines_combined(self, range_size, normalized=False, trials=None, zoom=False):
        # Go through all balmer lines, and call graph_balmer_line_combined with each
        for line in balmer_lines:
            self.graph_balmer_line_combined(line, range_size, normalized, trials=trials, zoom=zoom)
    '''
    def graph_all_sigmas_vs_powers(self):
        lines = list(balmer_lines.keys())
        fig, axes = plt.subplots(2, 3, figsize=(12, 8))
        axes = axes.flatten()
        fig.suptitle("Gaussian Sigma vs Power (All Balmer Lines)")
        for i, line in enumerate(lines):
            ax = axes[i]
            for t in self.trials:
                try:
                    peak_index = t.peak_names.index(line)
                    color = "red" if t.saturated[peak_index] else "blue"
                    ax.errorbar(t.power, t.sigma_params[peak_index], yerr=t.sigma_param_errors[peak_index], fmt='o', color=color)
                except ValueError:
                    continue
            ax.set_title(line)
            ax.set_xlabel("Power [W]"); ax.set_ylabel("Sigma")
            ax.grid(True)
        # Hide unused subplots (if any)
        for j in range(len(lines), len(axes)):
            axes[j].axis("off")
        plt.tight_layout(rect=[0, 0, 1, 0.95])
        plt.savefig(f"{self.folder}_plots/Gaussian_Sigma_vs_Power_Balmer_Lines_All.pdf")
        plt.close()

    '''
    def graph_all_area_ratios(self, balmer_line_1, balmer_line_2):
        plt.figure(figsize=(10,6))
        plt.title("Ratio of areas under curves of {} to {}".format(balmer_line_1, balmer_line_2))
        plt.xlabel("Power"); plt.ylabel("Ratio")
        powers = []; line_1_areas = []; line_2_areas = []; ratios = []
        for t in self.trials:
            line_1_area = t.area_under_balmer_line(balmer_line_1)
            line_2_area = t.area_under_balmer_line(balmer_line_2)
            ratio = line_1_area / line_2_area

            powers.append(t.power)
            line_1_areas.append(line_1_area)
            line_2_areas.append(line_2_area)
            ratios.append(ratio)

        # Poisson error calculation
        x = np.array(powers)
        y = np.array(ratios) # ratios = area1/area2
        line_1_areas = np.array(line_1_areas) #A1
        line_2_areas = np.array(line_2_areas) #A2
        
        # σ=N^1/2
        sigma_1 = np.sqrt(line_1_areas) # A1^1/2
        sigma_2 = np.sqrt(line_2_areas) # A2^1/2
        # sigma_ratio = np.sqrt((sigma_1 / line_2_areas) ** 2 + (line_1_areas * sigma_2 / line_2_areas ** 2) ** 2)
        sigma_ratio = (line_1_areas / line_2_areas) * np.sqrt((1 / line_1_areas) * (1 / line_2_areas))
        # print("sigma_ratio of {} to {}: {}".format(balmer_line_1, balmer_line_2, sigma_ratio))
        
        #σR2=(∂A1*∂R)2σ12+(∂A2*∂R)2σ22
        #σR=((σ1/A2)^2 + (A1σ2/A2^2)^2)
        
        plt.errorbar(x, y, yerr=sigma_ratio, fmt='o', color='red')

        m, b = np.polyfit(x, y, 1)
        x_line = np.linspace(x.min(), x.max(), 200)
        y_line = m * x_line + b
        plt.plot(x_line, y_line)
        #plt.show()
        plt.close()
    '''
    def graph_balmer_areas_and_ratios(self, line_pairs):
        lines = list(balmer_lines.keys())
        # Area vs. Power
        fig1, axes1 = plt.subplots(2, 3, figsize=(12, 8))
        axes1 = axes1.flatten()
        fig1.suptitle("Area Under Balmer Lines vs Power: Poisson Error $N^{1/2}$")
        for i, line in enumerate(lines):
            ax = axes1[i]
            for t in self.trials:
                try:
                    A = t.area_under_balmer_line(line)
                    peak_index = t.peak_names.index(line)
                    color = "red" if t.saturated[peak_index] else "blue"
                    ax.errorbar(t.power, t.area_under_balmer_line(line), yerr=np.sqrt(t.area_under_balmer_line(line)), fmt='o', color=color)
                except ValueError:
                    continue
            ax.set_title(line)
            ax.set_xlabel("Power [W]"); ax.set_ylabel("Area")
            ax.grid(True)
        for j in range(len(lines), len(axes1)):
            axes1[j].axis("off")
        plt.tight_layout(rect=[0, 0, 1, 0.95])
        plt.savefig(f"{self.folder}_plots/Balmer_Areas_vs_Power.pdf")
        plt.close(fig1)

        # Ratio vs. Power
        n = len(line_pairs)
        cols = int(np.ceil(np.sqrt(n))); rows = int(np.ceil(n / cols))
        fig2, axes2 = plt.subplots(rows, cols, figsize=(3 * cols, 3 * rows))
        axes2 = np.array(axes2).flatten()
        if len(line_pairs) == 1:
            axes2 = [axes2]
        fig2.suptitle("Balmer Area Ratios vs Power")
        for i, (line1, line2) in enumerate(line_pairs):
            ax = axes2[i]
            powers_list = []
            ratios = []; sigma_ratio = []
            for t in self.trials:
                try:
                    A1 = t.area_under_balmer_line(line1)
                    A2 = t.area_under_balmer_line(line2)
                    ratio = A1 / A2
                    # Poisson error propagation
                    sigma = ratio * np.sqrt((1 / A1) + (1 / A2))
                    
                    ax.errorbar(t.power, ratio, yerr=sigma, fmt='o', color="green")
                    with open(results_path, "a") as f:
                        f.write("Sigma Ratio of {:<6},{:<6} ({:>3}W): Sigma = {:>6.4g}\n".format(line1, line2, t.power, sigma))
                    powers_list.append(t.power)
                    ratios.append(ratio)
                    sigma_ratio.append(sigma)
                except ValueError:
                    continue
            powers = np.array(powers_list)
            ratios = np.array(ratios)
            sigma_ratio = np.array(sigma_ratio)
            # linear fit
            m, b = np.polyfit(powers, ratios, 1)
            x_line = np.linspace(powers.min(), powers.max(), 200)
            ax.plot(x_line, m * x_line + b)
            ax.set_title(f"{line1} / {line2}")
            ax.set_xlabel("Power [W]"); ax.set_ylabel("Ratio")
            ax.grid(True)
        plt.tight_layout(rect=[0, 0, 1, 0.92])
        plt.savefig(f"{self.folder}_plots/Balmer_Area_Ratios_vs_Power.pdf")
        plt.close(fig2)

experiment = Experiment(folder=folder, saturation_line=65536)
#experiment = Experiment(folder=folder, saturation_line=83500)
experiment.graph_all()
experiment.graph_all_balmer_lines_combined(25)
#experiment.graph_all_balmer_lines_combined(25, normalized=True)
experiment.graph_all_sigmas_vs_powers()

experiment.graph_balmer_areas_and_ratios([
    ("Beta", "Gamma"),
    ("Delta", "Gamma"),
    ("Beta", "Delta"),
    ("Gamma", "Delta")
])
