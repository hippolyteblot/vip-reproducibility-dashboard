import os
import random
import time
import warnings
import imageio
import numpy as np
import nibabel as nib
import os.path as op
import concurrent.futures
import threading


from nilearn import plotting as nilp
import matplotlib as mpl
from matplotlib import pyplot as plt
import pandas as pd



def sigdig(array, base=2, axis=-1):
    """Compute significant digits of array elements along axis"""
    try:
        # If we have a float, this is our value of epsilon
        eps = np.finfo(array.dtype).eps
    except ValueError:
        # If it's an int, we want to convert it to a float of the same number of
        # bits to get our estimate of epsilon
        a2_dtype = "np.float{0}".format(array.dtype.itemsize*8)
        a2 = array.astype(eval(a2_dtype))
        warnings.warn("Converting array from {} to {}".format(array.dtype,
                                                              a2.dtype),
                      Warning)
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

def plot_array(array, cmap=mpl.cm.viridis, ni_img=None, file_name=None):
    fig, axes = plt.subplots(nrows=1,ncols=1,figsize=(11, 8))

    ni_img = nib.Nifti1Image(array, nib.load(ni_img).affine, nib.load(ni_img).header)

    # invert the colormap
    nilp.plot_img(ni_img, draw_cross=False, cmap=cmap, axes=axes,
                  annotate=False, black_bg=False, colorbar=True)
    # save the figure
    # create the folder if it does not exist
    if not os.path.exists(os.path.dirname(file_name)):
        os.makedirs(os.path.dirname(file_name))
    
    plt.savefig(file_name)



def get_sigdig_mean(image):
    nifti = nib.Nifti1Image(image.get_fdata(), image.affine)
    sigd = sigdig(nifti.get_fdata())
    return np.mean(sigd)


def get_variance(image):
    nifti = nib.Nifti1Image(image.get_fdata(), image.affine)
    return np.var(nifti.get_fdata())

def get_sigdig_standard_deviation(folder):
    # get all the files in the folder
    df = pd.DataFrame()
    files = os.listdir(folder)
    values = []
    for file in files:
        # load the file
        image = nib.load(folder + file)
        sigdig_mean = get_sigdig_mean(image)
        print("Mean for file ", file, " is : ", sigdig_mean)
        values.append(sigdig_mean)
    # return the standard deviation
    # before, fill the dataframe with the values and the file names
    df['Sigdig_mean'] = values
    df['File'] = files
    df['File_type'] = 'brainTumorMask'
    patient_ids = [1,2,1,2,2,1,1,2,2,1]
    df['Patient_id'] = patient_ids

    print(df)
    # to feather
    df.to_feather('data.feather')
    return np.std(values)



#print("Standard deviation for folder nifti_brats/brainTumorMask/ : ", get_sigdig_standard_deviation('nifti_brats/brainTumorMask/'))


def build_dataframe(folder):
    # get all the execution folders in the folder
    df = pd.DataFrame()
    execution_folders = os.listdir(folder)
    total_count = 0
    for execution_folder in execution_folders:
        patient_folders = os.listdir(folder + execution_folder)
        # keep onlt the folders
        patient_folders = [patient_folder for patient_folder in patient_folders if os.path.isdir(folder + execution_folder + '/' + patient_folder)]
        total_count += len(patient_folders)

    i = 1
    starting_time = time.time()
    for execution_folder in execution_folders:
        exec_number = execution_folder.split('_')[1]
        patient_folders = os.listdir(folder + execution_folder)
        # keep onlt the folders
        patient_folders = [patient_folder for patient_folder in patient_folders if os.path.isdir(folder + execution_folder + '/' + patient_folder)]
        for patient_folder in patient_folders:
            # get all the files ending with .nii.gz
            files = os.listdir(folder + execution_folder + '/' + patient_folder)
            files = [file for file in files if file.endswith('.nii.gz')]
            for file in files:
                # load the file
                image = nib.load(folder + execution_folder + '/' + patient_folder + '/' + file)
                sigdig_mean = get_sigdig_mean(image)
                # add the file to the dataframe
                df = pd.concat([df, pd.DataFrame({'File': [file], 'Sigdig_mean': [sigdig_mean], 'File_type': [file.split('.')[0]], 'Patient_id': [patient_folder], 'Execution': [exec_number]})])
            print("Progress: ", i, "/", total_count, " (", round(i/total_count*100, 2), "%)")
            remaining_seconds = (time.time() - starting_time) / i * (total_count - i)
            r_hours = remaining_seconds // 3600
            r_minutes = (remaining_seconds - r_hours * 3600) // 60
            r_seconds = remaining_seconds - r_hours * 3600 - r_minutes * 60
            print("Approximate time remaining: ", int(r_hours), " hours, ", int(r_minutes), " minutes, ", int(r_seconds), " seconds")
            i += 1
    # return the dataframe
    return df
"""
df = build_dataframe('/run/media/blot/HDD/experience_2/v190_fuzzy/')
df.reset_index(drop=True, inplace=True)
# save as data.feather
df.to_feather('data.feather')"""

"""array = np.array([
    nib.load('/run/media/blot/HDD/experience_2/v190_fuzzy/exec_1/UPENN-GBM-00001/T2_to_SRI_brain.nii.gz').get_fdata(),
    nib.load('/run/media/blot/HDD/experience_2/v190_fuzzy/exec_2/UPENN-GBM-00001/T2_to_SRI_brain.nii.gz').get_fdata(),
    nib.load('/run/media/blot/HDD/experience_2/v190_fuzzy/exec_3/UPENN-GBM-00001/T2_to_SRI_brain.nii.gz').get_fdata(),
    nib.load('/run/media/blot/HDD/experience_2/v190_fuzzy/exec_4/UPENN-GBM-00001/T2_to_SRI_brain.nii.gz').get_fdata(),
    nib.load('/run/media/blot/HDD/experience_2/v190_fuzzy/exec_5/UPENN-GBM-00001/T2_to_SRI_brain.nii.gz').get_fdata(),
    nib.load('/run/media/blot/HDD/experience_2/v190_fuzzy/exec_6/UPENN-GBM-00001/T2_to_SRI_brain.nii.gz').get_fdata(),
])"""


def compute_sigdig_for_experiment(folder):
    # list the execution folders
    execution_folders = os.listdir(folder)
    patients_folders = os.listdir(folder + execution_folders[0])
    # keep only the 20 first patients
    patients_folders = patients_folders[:20]
    # nii files
    files = os.listdir(folder + execution_folders[0] + '/' + patients_folders[0])
    files = [file for file in files if file.endswith('.nii.gz')]
    # keep only the files containing 'T1'
    #files = [file for file in files if 'T1' in file]
    # drop the files containing 'T1CE'
    #files = [file for file in files if 'T1CE' not in file]
    results = {}
    timer = time.time()
    total_count = len(patients_folders) * len(files)
    i = 1
    for patient_folder in patients_folders:
        results[patient_folder] = {}
        for file in files:
            results[patient_folder][file] = []
            files_list = []
            for execution_folder in execution_folders:
                # add the file to the list
                files_list.append(folder + execution_folder + '/' + patient_folder + '/' + file)
            # load the files
            images = np.array([nib.load(file).get_fdata() for file in files_list])
            # get the sigdig
            sigdig_mean = np.mean(sigdig(images, base=10, axis=0))
            # add the sigdig to the results
            results[patient_folder][file] = sigdig_mean
            print("Progress: ", i, "/", total_count, " (", round(i/total_count*100, 2), "%)")
            remaining_seconds = (time.time() - timer) / i * (total_count - i)
            r_hours = remaining_seconds // 3600
            r_minutes = (remaining_seconds - r_hours * 3600) // 60
            r_seconds = remaining_seconds - r_hours * 3600 - r_minutes * 60
            e_hours = (time.time() - timer) // 3600
            e_minutes = ((time.time() - timer) - e_hours * 3600) // 60
            e_seconds = (time.time() - timer) - e_hours * 3600 - e_minutes * 60
            print("Approximate time remaining: ", int(r_hours), " hours, ", int(r_minutes), " minutes, ", 
                int(r_seconds), " seconds. Time elapsed: ", int(e_hours), " hours, ", int(e_minutes), 
                " minutes, ", int(e_seconds), " seconds.")
            i += 1
    # return the results
    return results





def compute_sigdig_for_experiment2(folder):
    # list the execution folders
    execution_folders = os.listdir(folder)
    patients_folders = os.listdir(folder + execution_folders[0])
    # keep only the 20 first patients
    patients_folders = patients_folders[:20]
    # nii files
    files = os.listdir(folder + execution_folders[0] + '/' + patients_folders[0])
    files = [file for file in files if file.endswith('.nii.gz')]
    # keep only the files containing 'T2_to_SRI_brain'
    files = [file for file in files if 'T1' in file]
    # drop the files containing 'T1CE'
    files = [file for file in files if 'T1CE' not in file]
    results = {}
    timer = time.time()
    total_count = len(patients_folders) * len(files)
    i = 1
    for patient_folder in patients_folders:
        results[patient_folder] = {}
        for file in files:
            results[patient_folder][file] = []
            files_list = []
            for execution_folder in execution_folders:
                # add the file to the list
                files_list.append(folder + execution_folder + '/' + patient_folder + '/' + file)
            # load the files
            images = np.array([nib.load(file).get_fdata() for file in files_list])
            # get the sigdig
            sigdig_array = sigdig(images, base=10, axis=0)
            mask_name = files_list[0]
            mask = nib.load(op.join(mask_name))
            mask_ = mask.get_fdata().astype('bool')
            mask_data = mask.get_fdata()
            masked_sigdigs = np.where(mask_data>0, sigdig_array, mask_data)
            plot_array(masked_sigdigs, ni_img=None, file_name='pngs/' + patient_folder + '/' + file.split('.')[0] + '.png')
            results[patient_folder][file] = np.mean(sigdig_array[mask_])

            remaining_seconds = (time.time() - timer) / i * (total_count - i)
            r_hours = remaining_seconds // 3600
            r_minutes = (remaining_seconds - r_hours * 3600) // 60
            r_seconds = remaining_seconds - r_hours * 3600 - r_minutes * 60
            e_hours = (time.time() - timer) // 3600
            e_minutes = ((time.time() - timer) - e_hours * 3600) // 60
            e_seconds = (time.time() - timer) - e_hours * 3600 - e_minutes * 60
            print("Approximate time remaining: ", int(r_hours), " hours, ", int(r_minutes), " minutes, ", 
                int(r_seconds), " seconds. Time elapsed: ", int(e_hours), " hours, ", int(e_minutes), 
                " minutes, ", int(e_seconds), " seconds.")
            
            i += 1

    # return the results
    return results

#compute_sigdig_for_experiment2('/run/media/blot/HDD/experience_2/v190_fuzzy/')

dict_sigdig = compute_sigdig_for_experiment2('/run/media/blot/HDD/experience_2/v190_fuzzy/')
# store it in a dataframe
df = pd.DataFrame()
for patient in dict_sigdig.keys():
    for file in dict_sigdig[patient].keys():
        df = pd.concat([df, pd.DataFrame({'Patient': [patient], 'File': [file], 'Sigdig_mean': [dict_sigdig[patient][file]]})])
df.reset_index(drop=True, inplace=True)
# save as data.feather
print(df)
df.to_feather('super_data99.feather')