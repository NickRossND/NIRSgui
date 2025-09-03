# Note on Units:    Accepts MHz for frequency, 1/mm for optical properties, and mm for distances

import numpy as np
# from NIRSgui.GUItutorial.main.py import x,y 



def p1seminf(p,f,nind,rho,wt,reim_flag):
#     # P = input of optical properties [mua, musp], 1/mm
#     # F = input of frequencies, MHz
#     # NIND = refractive index of medium
#     # rho = source-detector separation, mm
#     # WT = weighing factor for the frequencies, set to 0 for no weighting
#     # REIM_FLAG = set to 1 for real/imaginary, 0 for amplitude/phase
#     # BOUND_OPT = boundary conditions to set based on based upon  Haskell, R. C., L. O. Svaasand, T. Tsong-Tseh, 
#     #        F. Ti-Chen, M. S. McAdams and B. J. Tromberg (1994). "Boundary conditions for the diffusion equation in radiative transfer." 
#     #        Journal of the Optical Society of America A (Optics, Image Science and Vision) 11(10): 2727-41.
#     #        Set to 0 to use precalculated values, 1 to calculate directly (slower ...)

    # # %*************************************************************************
    # # %BASIC CALCULATIONS
    # # %*************************************************************************
    # # % [mus, mua, f] = ndgrid(p(2,:), p(1,:), freq)
    # wt = 0  # Weight for the curvefitting, set to 0 for no weighting
    # reim_flag = 1  # Set to 1 for real/imaginary, 1 for amplitude/phase
    # rho = 30; # source-detector separation, mm 
    # nind = 1.4  # refractive index of medium

    # muaRes= 20  # number of points for mua
    # muspRes= 20  # number of points for musp

    # muaVals= np.linspace(0.002, 0.5, muaRes)
    # muspVals= np.linspace(0.5, 2.0, muspRes)

    # MUA, MUSP = np.meshgrid(muaVals, muspVals, indexing="ij")
    # p = np.column_stack((MUA.ravel(), MUSP.ravel()))
    # f = np.arange(50,352,2)  # Example frequencies in MHz, 50-350 MHz with 2 MHz step (352 means stop at 350)
    y = np.zeros((len(f), len(p)), dtype=complex)  # Initialize output array

    c = 2.99792458e11/nind				# now in mm/s
    # I=np.sqrt(-1)

    # set boundary condition based on refractive index
    if nind==1.4:
        reff=0.493
    elif nind==1.33:
        reff=0.431
    # else:
    #     if boundary_opt==1:
    #         reff=Ref_n_lookup_v2(nind)   #use integrals
    #     else:    #polynomial fit 6 order by Sophie and AEC
    #         reff = 2.1037.*nind.^6-19.8048.*nind.^5+76.8786.*nind.^4-156.9634.*nind.^3+176.4549.*nind.^2 -101.6004.*nind+22.9286

    for ii in range(len(f)):
        # print(kk)
        fbc = 1.0e6*2*np.pi*f[ii]/c  # Convert MHz to Hz
        # i=0   
        for jj in range(len(p)):
            # i += 1
            # print(i)
            # print(f"Processing mua: {jj[0]}, musp: {jj[1]} at frequency: {kk} MHz")
            # if i == 15:
            #     break 
            
            # %definitions 
            mutr = p[jj,0]+p[jj,1] # total attenuation coefficient, 1/mm
            ltr = 1./mutr # transport mean free path, mm
                
            # D=1/3*ltr;			%diffusion coefficient, uses the mua for kicks
            # g = .8;
            # alfa = 1-0.8.*(mutr./(mus.*(1+g)+mua));
            # D = 1./(3.*mus+alfa.*mua);
            D=1/3*ltr 
            # fbc = 1.0e6*2*np.pi*freq/c			# now in MHZ for omega
            alpha=3*fbc*D		# Josh definition, such that alpha is 2pi*Tcoll/Tmod (page 109).
                

            # %calcuate true distances   
            zb = 2/3*(1+reff)/(1-reff)*ltr									#extrapolated boundary
            
            r01 = np.sqrt(ltr*ltr+rho*rho)  	            #s-d separation for source, dist 1   
            rb1 = np.sqrt((2*zb+ltr)*(2*zb+ltr)+rho*rho)	#s-d separation for image, dist 1
            
            # %===kvector=====================================================================================
            k_josh=np.sqrt((p[jj,0]-fbc*alpha-1j*(fbc+p[jj,0]*alpha))/D);	#complete P1 wavevector
            kr=np.abs(k_josh.real)	
            ki=np.abs(k_josh.imag)
            
            # %==photon density wave===========================================================================
            er01 = np.exp(-kr*r01)					# exponentials in form e(-kr)/r
            erb1 = np.exp(-kr*rb1)
            Re1 = (+(er01/r01)*np.cos(ki*r01) - (erb1/rb1)*np.cos(ki*rb1))/D
            Im1 = (+(er01/r01)*np.sin(ki*r01) - (erb1/rb1)*np.sin(ki*rb1))/D  
                
                
    # %*************************************************************************
    # %OUTPUT
    # %*************************************************************************
            # if(rho2==0)		#flag for single distance = real and imaginary
            
            if(reim_flag == 0):
                fa=np.sqrt(Re1^2+Im1^2)
                fb=np.unwrap(np.arctan2(Im1,Re1))		#in radians
                y[ii,jj] = [fa,fb] # returns in amp and phase 
                y[ii,jj] = np.transpose(y)
            
            else:
                fa=Re1
                fb=Im1
                y[ii,jj]=fa+(fb*1j)		#final return in complex form

                    
            # %final outputs
            # if reim_flag ==0:
            #     # % fb = fb.*180/pi;
            #     # % fa = reshape(fa,1,size(fa,3));
            #     # % fb = reshape(fb,1,size(fb,3));
            # else:

            # % y=[fa;fb]
            # check to see if weighting is applied
            if wt !=0:
                y = y*wt;  # Weight for the curvefitting
    return y
    print(f"Output shape (freqs, mu complex): {y.shape}")  # Display output shape and first few values


        