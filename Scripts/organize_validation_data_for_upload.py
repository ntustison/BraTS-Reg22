import os
import glob
import shutil

os.environ["ITK_GLOBAL_DEFAULT_NUMBER_OF_THREADS"] = "4"

base_directory = "/Users/ntustison/Data/Public/BRATS/RegistrationCompetition2022/"

subjects = glob.glob(base_directory + "BraTSReg_Validation_Processed/BraTSReg_*")

for i in range(len(subjects)):
    
    print("\n" + subjects[i], "(", i+1, "out of", len(subjects), ")")

    subject_prefix = os.path.basename(subjects[i])

    subject_files = glob.glob(subjects[i] + "/*.csv")    
    for j in range(len(subject_files)):
        print("   " + subject_files[j]) 

        subject_file_basename = os.path.basename(subject_files[j])
        tokens = subject_file_basename.split("_")

        if "t1ce_flair" in subject_file_basename or "t1ce_t2" in subject_file_basename:
            if tokens[3] == 'b':
                experiment = "_".join(tokens[2:8])
            else:
                experiment = "_".join(tokens[2:7])
        else:
            if tokens[3] == 'b':
                experiment = "_".join(tokens[2:7])
            else:
                experiment = "_".join(tokens[2:6])

        output_directory = base_directory + "BraTSReg_Validation_Processed_Upload" + "/" + experiment
        if not os.path.exists(output_directory):
            os.makedirs(output_directory, exist_ok=True)

        output_file = output_directory + "/" + subject_prefix
        if ".csv" in tokens[-1]:
            output_file += ".csv"
        else:
            continue

        # elif "moving_warped.nii.gz" in tokens[-1]:
        #     output_file += "Warped.nii.gz"
        # else:
        #     output_file += tokens[-1]

        if not os.path.exists(output_file):
            print(subject_files[j] + " --> " + output_file)        
            shutil.copy(subject_files[j], output_file)
