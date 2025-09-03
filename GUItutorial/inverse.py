import numpy as np
import p1seminf
import glob

calPhantom = 'ndabsc'  # name of calibration phantom file
wvlen = np.array([785, 852])  # wavelengths used during the measurement, in nm
rho = 30  # source-detector separation, mm
nind = 1.4  # refractive index of medium
wt = 0  # Weight for the curvefitting, set to 0 for
freq = np.arange(50,352,2)  # Example frequencies in MHz, 50-350 MHz with 2 MHz step (352 means stop at 350)
reim_flag = 1  # Set to 1 for real/imaginary,

muaRes= 500  # number of points for mua
muspRes= 500  # number of points for musp

muaVals= np.linspace(0.002, 0.5, muaRes)
muspVals= np.linspace(0.5, 2.0, muspRes)

MUA, MUSP = np.meshgrid(muaVals, muspVals, indexing="ij")
p = np.column_stack((MUA.ravel(), MUSP.ravel()))
lut = p1seminf.p1seminf(p, freq, nind, rho, wt, reim_flag) #shape is # of frequencies x # of (mua,musp) pairs
# print(f"Lookup table shape (freqs, mua*musp pairs): {lut.shape}")
# calDataDir = 'X'
# calibrationData = glob.glob(f'{calPhantom}*.asc')  # load your calibration data here

def calibrationFile(calPhantom, wvlen):
    calfile = f'C:\\Users\\nross3\\Documents\\MATLAB\\ssfdpm\\ssfdpmPro\\phantoms\\{calPhantom}.txt'
    # load data from the calibration phantom file of interest
    calOPs = np.loadtxt(calfile)# change this to where you store the phantom files
    calMua = np.zeros(len(wvlen))
    calMus = np.zeros(len(wvlen))
    indx = np.zeros(len(wvlen), dtype=int)

    # compare each wavelength in the phantom file with that in the measurement
    # data to pull the appropriate wavelength OPs that are closest to
    # wavelengths used during the measurement
    for ii, wl in enumerate(wvlen):
        indx= np.argmin(np.abs(calOPs[:,0]-wl))
        calMua[ii]= calOPs[indx,1]
        calMus[ii]= calOPs[indx,2]
        print(f"Wavelength: {wl} nm, mua: {calMua[ii]:.4f} 1/mm, mus: {calMus[ii]:.4f} 1/mm")
    # generate forward model data for calibration phantom
    ops = np.column_stack((calMua, calMus))
    theoreticalAmpPh = p1seminf.p1seminf(ops, freq, nind, rho, wt, reim_flag) #shape is # of frequencies x # of wavelengths
    # print(f"Complex amplitude & phase data for calibration phantom at {rho} mm source-detector separation:")
    # print(complexAmpPh)
    return theoreticalAmpPh

def calibrationCoeff(theoreticalAmpPh, calMeasData):
    # load your calibration data here
    # calData = np.loadtxt(calMeasData, skiprows=1)  # skip the header row
    # calData = calData[:, 1:]  # remove the first column (frequency column)
    # calData = calData[:, ::2] + 1j*calData[:, 1::2]  # convert to complex numbers

    # calculate calibration coefficients
    calCoeff = calMeasData/theoreticalAmpPh  # element-wise division
    print(f"Calibration coefficients shape (freqs, wavelengths): {calCoeff.shape}")
    return calCoeff

def inverse(measurementData, calCoeff):
    # apply calibration coefficients to measurement data
    calibratedMeasData = measurementData / calCoeff  # element-wise division
    costMin = np.zeros((len(wvlen), len(freq)), dtype=int)  # Initialize cost minimization array
    for ii in range(len(wvlen)):
        for jj in range(len(freq)):
            diff = np.sqrt((lut[jj,:].real - calibratedMeasData[jj,ii].real)**2 + (lut[jj,:].imag - calibratedMeasData[jj,ii].imag)**2)
            costMin[ii,jj] = np.argmin(diff)  # find index of minimum difference
            print(f"Frequency: {freq[jj]} MHz, Wavelength: {wvlen[ii]} nm, Estimated mua: {p[costMin[ii,jj],0]:.4f} 1/mm, Estimated mus: {p[costMin[ii,jj],1]:.4f} 1/mm")

if __name__ == "__main__":
    calPhantomData = calibrationFile(calPhantom, wvlen)
    noise = calPhantomData * np.random.normal(0, 0.01, size =calPhantomData.shape)  # simulate some measurement data with noise
    calMeasData = calPhantomData + noise
    calCoeff = calibrationCoeff(calPhantomData, calMeasData)
    inverse(calMeasData, calCoeff)