import ants
import numpy as np
import os
import glob
import pandas as pd
import math
import time

os.environ["ITK_GLOBAL_DEFAULT_NUMBER_OF_THREADS"] = "4"

base_directory = "/Users/ntustison/Data/Public/BRATS/RegistrationCompetition2022/"

write_xfrm_output = True

multi_modalities = [
                    ['t1'], 
                    ['t1ce'],
                    ['flair'],
                    ['t2'],
                    ['t1ce', 'flair'],
                    ['t1ce', 't2']
                   ] 
single_modality = [
                    ['t1'], 
                    ['t1ce'],
                    ['flair'],
                    ['t2']
                   ] 
transform_types = [
                   "antsRegistrationSyNQuick[a]",
                    "antsRegistrationSyNQuick[s,32]",
                    "antsRegistrationSyNQuick[b,32,26]",
                    "antsRegistrationSyN[s,2]",
                    "antsRegistrationSyN[b,2,26]",
                    "antsRegistrationSyN[s,4]",
                    "antsRegistrationSyN[b,4,26]"
                  ]

results_df = pd.DataFrame(columns=["RegistrationType", "Modalities", "Subject", "TimeElapsed", "PreLandmarkError", "PostLandmarkError"])

subjects = glob.glob(base_directory + "BraTSReg_Validation_Data/BraTSReg_*")
# subjects = glob.glob(base_directory + "BraTSReg_Training_Data_v3/BraTSReg_*")

for i in range(len(subjects)):
    
    print("\n" + subjects[i], "(", i+1, "out of", len(subjects), ")")

    subject_prefix = os.path.basename(subjects[i])

    for t in range(len(transform_types)):

        type_of_transform = transform_types[t]
        
        if type_of_transform == "brats" or type_of_transform == "antsRegistrationSyNQuick[a]":
            which_modalities = single_modality
        else:
            which_modalities = multi_modalities

        for m in range(len(which_modalities)):

            modalities = which_modalities[m]          

            output_prefix = ""
            if write_xfrm_output:
                output_directory = (os.path.dirname(subjects[i]) + "/" + subject_prefix + "/").replace("BraTSReg_Validation_Data", "BraTSReg_Validation_Processed")
                if not os.path.exists(output_directory):
                    os.makedirs(output_directory, exist_ok=True)
                output_transform_string = type_of_transform.replace("[", "_")
                output_transform_string = output_transform_string.replace("]", "_")
                output_transform_string = output_transform_string.replace(",", "_")
                output_prefix = output_directory + subject_prefix + "_" + output_transform_string + '_'.join(modalities) + "_"

            print(output_prefix)
        
            if os.path.exists(output_prefix + "moving_warped_landmarks.csv"):
               continue

            baseline_images = list()
            followup_images = list()
            for j in range(len(modalities)):
                baseline_image_filename = subjects[i] + "/" + subject_prefix + "_00_0000_" + modalities[j] + ".nii.gz"
                if not os.path.exists(baseline_image_filename):
                    raise ValueError(baseline_image_filename + " does not exist") 
                baseline_images.append(ants.image_read(baseline_image_filename))
                
                followup_image_filenames = glob.glob(subjects[i] + "/" + subject_prefix + "_01_*" + modalities[j] + ".nii.gz")
                followup_images.append(ants.image_read(followup_image_filenames[0]))

                print("    " + modalities[j] + ": ")
                print("        " + baseline_image_filename)
                print("        " + followup_image_filenames[0])

            time_start = time.time()    
            regInvXfrms = None
            regFwdXfrms = None
            if len(baseline_images) == 1 or type_of_transform == "brats":
                reg = ants.registration(baseline_images[0], followup_images[0], type_of_transform=type_of_transform, outprefix=output_prefix, verbose=1)
                if type_of_transform == "antsRegistrationSyNQuick[a]":
                    regInvXfrms = [output_prefix + "0GenericAffine.mat"]
                    regFwdXfrms = [output_prefix + "0GenericAffine.mat"]
                else:
                    regInvXfrms = [output_prefix + "0GenericAffine.mat",
                                   output_prefix + "1InverseWarp.nii.gz"]                
                    regFwdXfrms = [output_prefix + "1Warp.nii.gz",
                                   output_prefix + "0GenericAffine.mat"]                
            else:
                multivariate_extras = list()
                for j in range(1, len(baseline_images)):
                    if "Quick" in type_of_transform:
                        multivariate_extras.append(["MI", baseline_images[j], followup_images[j], 1.0, 32])
                    else:
                        if "[s,2]" in type_of_transform or "[b,2,26]" in type_of_transform:
                            multivariate_extras.append(["CC", baseline_images[j], followup_images[j], 1.0, 2])
                        else:
                            multivariate_extras.append(["CC", baseline_images[j], followup_images[j], 1.0, 4])
                reg = ants.registration(baseline_images[0], followup_images[0], type_of_transform=type_of_transform, outprefix=output_prefix, multivariate_extras=multivariate_extras, verbose=1)
                if type_of_transform == "antsRegistrationSyNQuick[a]":
                    regInvXfrms = [output_prefix + "0GenericAffine.mat"]
                    regFwdXfrms = [output_prefix + "0GenericAffine.mat"]
                else:
                    regInvXfrms = [output_prefix + "0GenericAffine.mat",
                                   output_prefix + "1InverseWarp.nii.gz"]                
                    regFwdXfrms = [output_prefix + "1Warp.nii.gz",
                                   output_prefix + "0GenericAffine.mat"]                

            time_end = time.time()

            time_elapsed = time_end - time_start
            #######

            followup_landmark_filename = glob.glob(subjects[i] + "/" + subject_prefix + "_01_*_landmarks.csv")[0]
            moving_indices = pd.read_csv(followup_landmark_filename).drop('Landmark', axis=1)
            moving_indices = moving_indices.rename(columns={'X' : 'x', 'Y' : 'y', 'Z' : 'z'})
            moving_indices['y'] = moving_indices['y'] + 239

            moving_points = np.zeros(moving_indices.shape)
            for j in range(moving_indices.shape[0]):
                moving_points[j,:] = ants.transform_index_to_physical_point(baseline_images[0], (moving_indices.iloc[j].values).astype(int))

            moving_points_df = pd.DataFrame(data = {'x': moving_points[:,0], 'y': moving_points[:,1], 'z': moving_points[:,2]})
            if len(regInvXfrms) == 1:
                moving_warped_points = ants.apply_transforms_to_points(3, moving_points_df, regInvXfrms, whichtoinvert=(True,))   
            else:
                moving_warped_points = ants.apply_transforms_to_points(3, moving_points_df, regInvXfrms, whichtoinvert=(True, False))   
            moving_warped_points = moving_warped_points.to_numpy()   

            if write_xfrm_output:
                moving_warped_points_df = pd.DataFrame(data=moving_warped_points, columns=['X', 'Y', 'Z'])
                moving_warped_points_df.insert(0, "Landmark", list(range(1, moving_points.shape[0]+1)))
                moving_warped_points_df.to_csv(output_prefix + "moving_warped_landmarks.csv", index=False)

                warpedMovOut = ants.apply_transforms(baseline_images[0], followup_images[0], regFwdXfrms, whichtoinvert=(False, False))
                ants.image_write(reg['warpedmovout'], output_prefix + "moving_warped.nii.gz")

            baseline_landmark_filename = subjects[i] + "/" + subject_prefix + "_00_0000_landmarks.csv"
            if os.path.exists(baseline_landmark_filename):
                fixed_indices = pd.read_csv(baseline_landmark_filename).drop('Landmark', axis=1)
                fixed_indices = fixed_indices.rename(columns={'X' : 'x', 'Y' : 'y', 'Z' : 'z'})    
                fixed_indices['y'] = fixed_indices['y'] + 239

                fixed_points = np.zeros(fixed_indices.shape)
                for j in range(fixed_indices.shape[0]):
                    fixed_points[j,:] = ants.transform_index_to_physical_point(baseline_images[0], (fixed_indices.iloc[j].values).astype(int))

                average_distance_pre = 0.0
                average_distance_post = 0.0

                for j in range(fixed_points.shape[0]):
                    average_distance_pre += math.sqrt((fixed_points[j, 0] - moving_points[j, 0])**2 + 
                                                    (fixed_points[j, 1] - moving_points[j, 1])**2 +
                                                    (fixed_points[j, 2] - moving_points[j, 2])**2)
                    average_distance_post += math.sqrt((fixed_points[j, 0] - moving_warped_points[j, 0])**2 + 
                                                    (fixed_points[j, 1] - moving_warped_points[j, 1])**2 +
                                                    (fixed_points[j, 2] - moving_warped_points[j, 2])**2)


                average_distance_pre /= fixed_points.shape[0] 
                average_distance_post /= fixed_points.shape[0] 
                print("    Distance:  " + str(average_distance_pre) + " ---> " + str(average_distance_post))

                results_df.loc[len(results_df.index)] = [type_of_transform, '_'.join(modalities), subject_prefix, time_elapsed, average_distance_pre, average_distance_post]

                results_df.to_csv("/Users/ntustison/Desktop/resultsBrats.csv", index=False)

            


