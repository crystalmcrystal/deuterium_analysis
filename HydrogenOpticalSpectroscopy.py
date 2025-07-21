import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.signal import find_peaks, peak_widths
'''
TO-DO:
1. FIGURE OUT WIDTH FUNCTION & PLOT
2. IMPLEMENT NIST DATABASE EMISSION LINES 
3. COMPUTE LINE RATIO
'''

# Figures Directory
save_dir = "D:/Project8/ECR_Cavity/OpticalEmissionSpectroscopy/OceanOptics/"
#os.makedirs(save_dir, exist_ok=True)

# Define the Gaussian function
def Gaussian(x, A, mu, sigma):
    x = np.asarray(x)
    return A * np.exp(-(x - mu)**2 / (2 * sigma**2))

def dN_dE(x, m_beta):
    diff = np.power(x, 2) - np.power(m_beta, 2)
    return x * np.sqrt(np.where(diff < 0, 0, diff))

# Load in excel file and data frame
file_path = ["D:/Project8/ECR_Cavity/OpticalEmissionSpectroscopy/OceanOptics/Hydrogen_SR4014911.xlsx", "D:/Project8/ECR_Cavity/OpticalEmissionSpectroscopy/OceanOptics/Spectra_output_0_1732215328.xlsx"]

sheet_name = 0
len_f = len(file_path)
# Initialize a nested list such that each entry in the list has a different ID, pointing to a different list object.
x = np.empty((len_f, 0)).tolist();  y = np.empty((len_f, 0)).tolist()
AFit = np.empty((len_f, 0)).tolist(); muFit = np.empty((len_f, 0)).tolist(); sigmaFit = np.empty((len_f, 0)).tolist()
AErr = np.empty((len_f, 0)).tolist(); muErr = np.empty((len_f, 0)).tolist(); sigmaErr = np.empty((len_f, 0)).tolist()
FWHM = np.empty((len_f, 0)).tolist(); xFit = np.empty((len_f, 0)).tolist(); yFit = np.empty((len_f, 0)).tolist()
peakFit = np.empty((len_f, 0)).tolist();  peakWavelengthFit = np.empty((len_f, 0)).tolist()
widthFit = np.empty((len_f, 0)).tolist(); wHeightFit = np.empty((len_f, 0)).tolist(); leftIPSFit = np.empty((len_f, 0)).tolist(); rightIPSFit = np.empty((len_f, 0)).tolist()
dataList = ['OceanView Data', 'OceanDirect Data']
emissionLine = ['delta', 'gamma', 'beta', 'fulcher']
titleList = ['Gaussian Fit for $H_\delta$ Balmer line', 'Gaussian Fit for $H_\gamma$ Balmer line', 'Gaussian Fit for $H_{\\beta}$ Balmer line', '$Fulcher-{\\alpha}$ band']
outputList = ['DeltaLineRun.png', 'GammaLineRun.png', 'BetaLineRun.png', 'FulcherRun.png']
colorList = ['b.', 'k.', 'r-', 'g-', 'mx', 'yx']
fitList = ['', 'Amplitude', 'Amplitude Err', 'Mean', 'Mean Err', 'Sigma', 'Sigma Err', 'FWHM']

for f in range(len(file_path)):
    df = pd.read_excel(file_path[f], sheet_name=sheet_name, usecols='A,B') # read_csv
    df.columns = ['A','B']
    # FIX LATER
    deltaLine_df = df.iloc[266:367] # inclusive indexing(50 before & after): lambda(delta) = 410 at index 306
    gammaLine_df = df.iloc[379:480]
    betaLine_df = df.iloc[626:727]
    fulcher_df = df.iloc[1210:1311] # 600-620 nm
    dx = deltaLine_df['A'].to_numpy(); gx = gammaLine_df['A'].to_numpy(); bx = betaLine_df['A'].to_numpy(); fx=fulcher_df['A'].to_numpy()
    dy = deltaLine_df['B'].to_numpy(); gy = gammaLine_df['B'].to_numpy(); by = betaLine_df['B'].to_numpy(); fy=fulcher_df['B'].to_numpy()
    x[f].append(dx); x[f].append(gx); x[f].append(bx); x[f].append(fx)
    y[f].append(dy); y[f].append(gy); y[f].append(by); y[f].append(fy)
    '''
    Crystal Alternative: Alpha
    start = 1470; end = 1505; guess = [0,60000,656,1] # ?, intensity, wavelength, ?
    res = curve_fit(gauss, data['Wavelength'][start:end], data['Intensity'][start:end],guess)
    '''
    try:
        for i in range(len(emissionLine)):
            # Find peaks
            peaks, properties = find_peaks(y[f][i], height=4000, threshold=50) # Arbitrary choice of height and threshold
            # Peak Prominence - How much a peak stands out from the surrounding baseline of the signal. Defined by vertical distance b/w peak and lowest contour
            widths, width_heights, left_ips, right_ips = peak_widths(y[f][i], peaks, rel_height=.5) # 0.5 - half prominence line, 1 - lowest contour line
            # print("peak wavelengths:\n{}".format(x[f][i][peaks]))
            # print("peak intensities:\n{}".format(y[f][i][peaks]))
            peakWavelengthFit[f].append(x[f][i][peaks]); peakFit[f].append(y[f][i][peaks])
            widthFit[f].append(widths); wHeightFit[f].append(width_heights); leftIPSFit[f].append(left_ips); rightIPSFit[f].append(right_ips)
            plt.figure(num=i, figsize=(10, 6))
            plt.plot(x[f][i], y[f][i], colorList[f], label=dataList[f])
            # plt.hlines(wHeightFit[f][i], x[f][i](np.trunc(left_ips)), x[f][i](np.trunc(right_ips)), color="cyan", label="Widths")
            # plt.hlines(widthFit[f][i], left_ips, right_ips, color="cyan", label="Widths")
            plt.plot(peakWavelengthFit[f][i], peakFit[f][i], colorList[f + 4], markersize=10, label="Peaks")
            if i != (len(emissionLine)-1):
                # Fit the Gaussian model to the data: Amplitude, mean, sigma
                guess = [max(y[f][i]), np.mean(x[f][i]), np.std(x[f][i])]
                pOpt, pCov = curve_fit(Gaussian, x[f][i], y[f][i], p0=guess)
                AFit_i, muFit_i, sigmaFit_i = pOpt
                AFit[f].append(AFit_i); muFit[f].append(muFit_i); sigmaFit[f].append(sigmaFit_i)
                stdErr = np.sqrt(np.diag(pCov))
                AErr_i, muErr_i, sigmaErr_i = stdErr
                AErr[f].append(AErr_i); muErr[f].append(muErr_i); sigmaErr[f].append(sigmaErr_i)
                # Calculate the FWHM
                FWHM[f].append(2 * np.sqrt(2 * np.log(2)) * sigmaFit_i)
                # Print the results
                print(f"Fitted parameters: ({emissionLine[i]})")
                print(f"Amplitude (A): {AFit[f][i]:.5f} with standard error of {AErr[f][i]:.5f}")
                print(f"Mean[nm] (mu): {muFit[f][i]:.5f} with standard error of {muErr[f][i]:.5f}")
                print(f"Standard deviation (sigma): {sigmaFit[f][i]:.5f} with standard error of {sigmaErr[f][i]:.5f}")
                print(f"Full Width at Half Maximum (FWHM)[nm]: {FWHM[f][i]:.5f}\n")
                xFit[f].append(np.linspace(min(x[f][i]), max(x[f][i]), 100))
                yFit[f].append(Gaussian(xFit[f][i], AFit[f][i], muFit[f][i], sigmaFit[f][i]))
                # Plot the results
                plt.plot(xFit[f][i], yFit[f][i], colorList[f+2], label='Gaussian fit')
                # Clear Pointers
                del pOpt; del pCov
            plt.xlabel('Wavelength [nm]')
            plt.ylabel('Intensity [Counts]')
            plt.title(titleList[i])
            plt.legend()
            plt.savefig(os.path.join(save_dir, outputList[i]))
            del peaks; del properties; del widths; del width_heights; del left_ips; del right_ips
            '''
            plt.figure(num=i+4, figsize=(10,6))
            plt.xlabel('Wavelength [nm]')
            plt.ylabel('Intensity [Counts]')
            plt.title('width: {}'.format(titleList[i]))
            plt.savefig(os.path.join(save_dir, 'width{}.png'.format(outputList[i])))
            '''
    except Exception as e:
        print("Yikes buddy:", e)

# Truncating output information
file_output = save_dir + "SpectrumFitData.txt"
with open(file_output, "w") as fo:
    for f in range(len(file_path)):
        fo.write(file_path[f] + "\n")
        fo.write("-"*60 + "\n")
        i = 0
        for j in range(len(fitList)):
            fo.write(f"{fitList[j]:<20}")
        fo.write("\n")
        for a, ae, m, me, std, stde, fwhm in zip(AFit[f], AErr[f], muFit[f], muErr[f], sigmaFit[f], sigmaErr[f], FWHM[f]):
            a_tr = f"{a:.5f}"; ae_tr = f"{ae:.5f}"; m_tr = f"{m:.5f}"; me_tr = f"{me:.5f}"; std_tr = f"{std:.5f}"; stde_tr = f"{stde:.5f}" ;fwhm_tr = f"{fwhm:.5f}"
            fo.write(f"{emissionLine[i]:<20}{a_tr:<20}{ae_tr:<20}{m_tr:<20}{me_tr:<20}{std_tr:<20}{stde_tr:<20}{fwhm_tr:<20}\n")
            i += 1
        fo.write(" " * 60 + "\n")
    '''
    # Finding widths by peak finder that I removed by my selection criteria. i.e. 1 peak found for Delta, but 3 widths given.
    print(widthFit[0][0])
    print("\n")
    print(widthFit[0])
    
    for wid, wh in zip(widthFit[f], wHeightFit[f]):
            wid_tr = [f"{val:.5f}" for val in wid];
            wh_tr = [f"{val:.5f}" for val in wh]
    '''
print(f"Data Written to {file_output}")