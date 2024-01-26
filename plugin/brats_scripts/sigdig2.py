import numpy as np
import nibabel as nib
import pandas as pd
import glob
import os
from nilearn import plotting as nilp
import nilearn.masking
import matplotlib as mpl
from matplotlib import pyplot as plt
import significantdigits as sig
import glob

# From https://raw.githubusercontent.com/gkpapers/2020AggregateMCA/master/code/utils.py
def sigdig(array, base=2, axis=-1):
    '''
    Compute significant digits of array elements along axis
    '''
    try:
        # If we have a float, this is our value of epsilon
        eps = np.finfo(array.dtype).eps
    except ValueError:
        # If it's an int, we want to convert it to a float of the same number of
        # bits to get our estimate of epsilon
        a2_dtype = "np.float{0}".format(array.dtype.itemsize*8)
        a2 = array.astype(eval(a2_dtype))
        # Re-call the function with the float version
        return sigdig(a2, base=base, axis=axis)

    # Initialize empty matrix the same size of the array
    shp = list(array.shape)
    shp.pop(axis)
    sigs = np.empty(shp)
    sigs[:] = np.NaN

    # Compute the standard deviation and handle special case 1:
    #   - if no variance, maximum significance
    sd = np.std(array, axis=axis)
    c1locs = np.where(sd == 0)
    sigs[c1locs] = -np.log(eps)/np.log(base)

    # Compute the mean and handle special case 2:
    #   - if mean of 0, no significance.
    #   - N.B. this is the incorrect formula for zero-centered data
    mn = np.mean(array, axis=axis)
    c2locs = np.where(mn == 0)
    for c2l in zip(*c2locs):
        if np.isnan(sigs[c2l]):
            sigs[c2l] = 0

    # Otherwise, compute the number of significant digits using Parker, 1997
    c3locs = np.where(np.isnan(sigs))
    for c3l in zip(*c3locs):
        sigs[c3l] = -np.log(np.abs(sd[c3l] / mn[c3l]) + eps)/np.log(base)

    # Reset any negative values to zero
    c4l = np.where(sigs <= 0)
    sigs[c4l] = 0

    # Round up to nearest full bit, and return
    sigs = np.ceil(sigs).astype(int)
    return sigs

def plot_array(array, cmap=mpl.cm.viridis):
    fig, axes = plt.subplots(nrows=1,ncols=1,figsize=(11, 8))
    ni_img = nib.Nifti1Image(array, nib.load(image_files[0]).affine)

    #fig.suptitle("(b) Distributions of significant bits averaged among 20 subjects on MNI space", fontsize=14)
    nilp.plot_img(ni_img, draw_cross=False, cmap=cmap, axes=axes,
                  annotate=False, black_bg=False, colorbar=True)


# set data directory
data_path = '/run/media/blot/HDD/experience_2/'
# path for original mask in VIP with version 181
#path_mask = '/run/media/blot/HDD/experience_12/v181/exec_1/'
path_mask = '/run/media/blot/HDD/experience_2/v181_fuzzy/exec_1/'

# path to runs to calcul significant digits on
run = ['v181_fuzzy/exec_1/', 'v181_fuzzy/exec_2/', 'v181_fuzzy/exec_3/']
n_samples = len(run)
# images modalities to work on
images = ['FL', 'T1',  'T1CE', 'T2']
#images = ['T1']
# intermediated files to compare
cases = ['_rai_n4.nii.gz', '_to_SRI.nii.gz', '_to_SRI_brain.nii.gz'] 
# folders named according to each patients

# Because it can take some time select the patient 
patients = os.listdir(os.path.join(data_path,path_mask))
# keep only the first 10 patients
patients = patients[:10]
#patients = ['UPENN-GBM-00007'] #,'UPENN-GBM-00010', 'UPENN-GBM-00003', 'UPENN-GBM-00110', 'UPENN-GBM-00105']

# name of the mask file
mask_name = 'brainMask_SRI.nii.gz'
# final output to be computed
table = []

for patient in patients:
    for image in images:
        for case in cases:

            # Load brain mask
            # only  for '_to_SRI_brain.nii.gz' the mask has been computed
            #if case == '_to_SRI_brain.nii.gz':
            #    mask = nib.load(os.path.join(path_mask + patient, mask_name))
            #    mask_ = mask.get_fdata().astype('bool')
            # for intermadiate file, the mask is the whole image since no mask has been computed yet
            #else:
            mask = nib.load(os.path.join(path_mask + patient, image + case))
            mask_ = mask.get_fdata(dtype=np.float32).astype('bool')
                
            # Build array of samples
            image_files = [os.path.join(data_path + run[i] + patient, image + case)for i in range(n_samples)]
            array = np.array([(nib.load(image_file).get_fdata(dtype=np.float32)) for image_file in image_files])
            reference = np.mean(array, axis=0)

            # Get significant digits
            # first method used
            sigdigs = sigdig(array, base=10, axis=0) 
            # create a nifti image from the array
            # convert the array into a nifti image
            """
            array = np.array(sigdigs, dtype=np.float32)
            # convert nan into 0
            array[np.isnan(array)] = 0
            ni_img = nib.Nifti1Image(array, None)
            # save the nifti image
            # create a folder to store the results
            if not os.path.exists(os.path.join('./results/v181_fuzzy', patient)):
                os.makedirs(os.path.join('./results/v181_fuzzy', patient))
            nib.save(ni_img, os.path.join('./results/v181_fuzzy', patient, image + case[:-7] + '_sigdigs.nii.gz'))
            """
            # Mean and SD of sigdigits
            mean = np.mean(sigdigs[mask_])
            sd = np.std(sigdigs[mask_])
            # Store result into table
            table.append( [patient, image, case, mean, sd] )
            #print([patient, image, case, mean, sd])
    print([patient])
# Transform list of list into data frame    
df = pd.DataFrame(table,columns = ['patient', 'image','file','mean_sigdigits', 'std_sigdigits'])
# print(df)
# Export data frame 
df.to_csv('./results/sig_digits_v181_fuzzy.csv', index=False)


# read the file sig_digits_v181_fuzzy.csv and store it as a feather file
df = pd.read_csv('./results/sig_digits_v181_fuzzy.csv')
# Rename the columns to start with an Uppercase
df.columns = ['Patient', 'Image','File','Mean_sigdigits', 'Std_sigdigits']
# Transform the file into a feather file
print(df)
df.to_feather('./results/sig_digits_v181_fuzzy.feather')
