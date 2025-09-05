import numpy as np
import p1seminf
import glob
import re

calPhantom = 'ndabsc'  # name of calibration phantom file
measName = 'ndabsd'  # name of measurement file
wvlen = np.array([685, 785, 852])  # wavelengths used during the measurement, in nm
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

def calibrationCoeff(theoreticalAmpPh, path):
    # def calibrationCoeff(theoreticalAmpPh, calMeasData):
    # load your calibration phantom measurement data here
    file_paths = glob.glob(f'{path}\\{calPhantom}-{rho}*.asc')  # load your calibration data here
    if not file_paths:
        raise FileNotFoundError(f"No files found matching the pattern: {path}\\{calPhantom}-{rho}*.asc")
    
    calData = [np.loadtxt(file, skiprows=16) for file in file_paths]  # skip the header row
    avg_calData = np.mean(calData, axis = 0)
    avg_calData = avg_calData[np.isin(avg_calData[:,0], freq)]
    avg_calData = avg_calData[:, 1:]  # remove the first column (frequency column)
    calDataArr = avg_calData[:, ::2] + 1j*avg_calData[:, 1::2]  # convert to complex numbers

    # calculate calibration coefficients
    calCoeff = calDataArr/theoreticalAmpPh  # element-wise division
    print(f"Calibration coefficients shape (freqs, wavelengths): {calCoeff.shape}")
    return calCoeff

def inverse(calCoeff,path):
    # apply calibration coefficients to measurement data
    file_paths = glob.glob(f'{path}\\{measName}-{rho}*.asc')  # load your measurement data here
    if not file_paths:
        raise FileNotFoundError(f"No files found matching the pattern: {measName}-{rho}*.asc")
    # Sort the file list
    sorted_files = sorted(file_paths, key=extract_sort_key)
    
    measDataNew = np.zeros((len(sorted_files),len(freq), len(wvlen)), dtype=complex)  # Initialize measurement data array
    measData = [np.loadtxt(file, skiprows=16) for file in sorted_files]  # skip the header row
    for i, meas in enumerate(measData):
        # measDataNew[i] = measData[i][np.isin(measData[i][:,0], freq)]
        temp = meas[np.isin(meas[:,0], freq)]
        temp = temp[:, 1:]  # remove the first column (frequency column)
        measDataNew[i][:,:] = temp[:, ::2] + 1j*temp[:, 1::2]  # convert to complex numbers
    # measData = measData[np.isin(measData[:,0], freq)]
    calibratedMeasData = measDataNew / calCoeff  # element-wise division
    costMin = np.zeros((calibratedMeasData.shape[0],len(wvlen), len(freq)), dtype=int)  # Initialize cost minimization array
    
    avgOPs = np.zeros((calibratedMeasData.shape[0],len(wvlen), 2))
    for num in range(calibratedMeasData.shape[0]):
        for ii in range(len(wvlen)):
            for jj in range(len(freq)):
                diff = np.sqrt((lut[jj,:].real - calibratedMeasData[num, jj,ii].real)**2 + (lut[jj,:].imag - calibratedMeasData[num, jj,ii].imag)**2)
                costMin[num, ii,jj] = np.argmin(diff)  # find index of minimum difference
                # print(f"Frequency: {freq[jj]} MHz, Wavelength: {wvlen[ii]} nm, Estimated mua: {p[costMin[ii,jj],0]:.4f} 1/mm, Estimated mus: {p[costMin[ii,jj],1]:.4f} 1/mm")
            avgOPs[num, ii,0] = np.mean(p[costMin[num, ii,:],0])  # average mua
            avgOPs[num, ii,1] = np.mean(p[costMin[num, ii,:],1])  # average mus
            print(f"File {num}, Wavelength: {wvlen[ii]} nm, Average Estimated mua: {avgOPs[num,ii,0]:.4f} 1/mm, Average Estimated mus: {avgOPs[num, ii,1]:.4f} 1/mm")

    # for ii in range(len(wvlen)):
    return costMin, avgOPs

# sort filenames based on the number before '-dcswitch.asc'
def extract_sort_key(filepath):
    # Extracts number before '-dcswitch.asc'
    match = re.search(r'-(\d+)-dcswitch\.asc$', filepath)
    if match:
        return int(match.group(1))
    else:
        return float('inf')  # Send unmatched to the end


if __name__ == "__main__":
    calPhantomData = calibrationFile(calPhantom, wvlen)
    # noise = calPhantomData * np.random.normal(0, 0.01, size =calPhantomData.shape)  # simulate some measurement data with noise
    # calMeasData = calPhantomData + noise
    # calCoeff = calibrationCoeff(calPhantomData, calMeasData)
    filePath = 'G:\\Shared drives\\NickRoss_PhDWork\\fNIRS_Project\\S13720-SiPM_SDStests\\250314'
    calCoeff = calibrationCoeff(calPhantomData, filePath)
    # inverse(calMeasData, calCoeff)
    inverse(calCoeff, filePath)