import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# Figures Directory
save_dir = "D:/Research/Optical_Emission_Spectroscopy/OceanOptics/OceanView"
os.makedirs(save_dir, exist_ok=True)

# Define the Gaussian function
def Gaussian(x, A, mu, sigma):
    x = np.asarray(x)
    return A * np.exp(-(x - mu)**2 / (2 * sigma**2))

# Load in excel file and data frame
file_path = "D:/Research/Optical_Emission_Spectroscopy/OceanOptics/OceanView/Hydrogen_Spectra_DataRun_3_Sat.xlsx"
sheet_name = 0
df = pd.read_excel(file_path, sheet_name=sheet_name, usecols='A,B')
df.columns = ['A','B']
deltaLine_df = df.iloc[266:367] # inclusive indexing
gammaLine_df = df.iloc[379:480]
betaLine_df = df.iloc[626:727]

dx = deltaLine_df['A'].to_numpy(); gx = gammaLine_df['A'].to_numpy(); bx = betaLine_df['A'].to_numpy()
dy = deltaLine_df['B'].to_numpy(); gy = gammaLine_df['B'].to_numpy(); by = betaLine_df['B'].to_numpy()

x = [dx, gx, bx]; y = [dy, gy, by]
AFit = []; muFit = []; sigmaFit = []
AErr = []; muErr = []; sigmaErr = []
FWHM = []; Line = ['delta', 'gamma', 'beta']
xFit = []; yFit = []
try:
    for i in range(3):
        # Fit the Gaussian model to the data
        guess = [max(y[i]), np.mean(x[i]), np.std(x[i])] # Amplitude, mean, sigma
        pOpt, pCov = curve_fit(Gaussian, x[i], y[i], p0=guess)
        AFit_i, muFit_i, sigmaFit_i = pOpt
        AFit.append(AFit_i); muFit.append(muFit_i); sigmaFit.append(sigmaFit_i)
        stdErr = np.sqrt(np.diag(pCov))
        AErr_i, muErr_i, sigmaErr_i = stdErr
        AErr.append(AErr_i); muErr.append(muErr_i); sigmaErr.append(sigmaErr_i)

        # Calculate the FWHM
        FWHM.append(2 * np.sqrt(2 * np.log(2)) * sigmaFit_i)

        # Print the results
        print(f"Fitted parameters: ({Line[i]})")
        print(f"Amplitude (A): {AFit[i]:.5f} with standard error of {AErr[i]:.5f}")
        print(f"Mean[nm] (mu): {muFit[i]:.5f} with standard error of {muErr[i]:.5f}")
        print(f"Standard deviation (sigma): {sigmaFit[i]:.5f} with standard error of {sigmaErr[i]:.5f}")
        print(f"Full Width at Half Maximum (FWHM)[nm]: {FWHM[i]:.5f}\n")
        del pOpt; del pCov # Clear Pointers

    dxFit = np.linspace(min(x[0]), max(x[0]), 100)
    dyFit = Gaussian(dxFit, AFit[0], muFit[0], sigmaFit[0])
    gxFit = np.linspace(min(x[1]), max(x[1]), 100)
    gyFit = Gaussian(gxFit, AFit[1], muFit[1], sigmaFit[1])
    bxFit = np.linspace(min(x[2]), max(x[2]), 100)
    byFit = Gaussian(bxFit, AFit[2], muFit[2], sigmaFit[2])
    # Plot the results
    plt.figure(num=1, figsize=(10, 6))
    plt.plot(x[0], y[0], 'b.', label='Data')
    plt.plot(dxFit, dyFit, 'r-', label='Gaussian fit')
    plt.xlabel('Wavelength [nm]')
    plt.ylabel('Intensity [Counts]')
    plt.title('Gaussian Fit for $H_\delta$ Balmer line')
    plt.legend()
    #plt.savefig(os.path.join(save_dir, 'DeltaLineRun3.png'))

    plt.figure(num=2, figsize=(10, 6))
    plt.plot(x[1], y[1], 'b.', label='Data')
    plt.plot(gxFit, gyFit, 'r-', label='Gaussian fit')
    plt.xlabel('Wavelength [nm]')
    plt.ylabel('Intensity [Counts]')
    plt.title('Gaussian Fit for $H_\gamma$ Balmer line')
    plt.legend()
    #plt.savefig(os.path.join(save_dir, 'GammaLineRun3.png'))

    plt.figure(num=3, figsize=(10, 6))
    plt.plot(x[2], y[2], 'b.', label='Data')
    plt.plot(bxFit, byFit, 'r-', label='Gaussian fit')
    plt.xlabel('Wavelength [nm]')
    plt.ylabel('Intensity [Counts]')
    plt.title('Gaussian Fit for $H_{\\beta}$ Balmer line')
    plt.legend()
    #plt.savefig(os.path.join(save_dir, 'BetaLineRun3.png'))
    plt.show()
except Exception as e:
    print("Yikes buddy:",e)
