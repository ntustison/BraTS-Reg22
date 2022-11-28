# BrATs-Reg22
ANTsX evaluation in the BrATs-Reg22 challenge


```
>>> import ants
>>> import pandas as pd
>>>
>>> #######################################################################
>>> # I am making assumptions about file names.  Please change accordingly.
>>> 
>>> baseline_image = ants.image_read("baseline_t1ce.nii.gz")
>>> followup_image = ants.image_read("followup_t1ce.nii.gz")
>>> followup_landmark_file = "followup_landmarks.csv"
>>> warped_followup_landmark_file = "warped_followup_landmarks.csv"
>>>
>>> ########################################################################
>>> 
>>> reg = ants.registration(baseline_image, followup_image, type_of_transform="antsRegistrationSyN[s,2]", verbose=1)
>>>
>>> moving_indices = pd.read_csv(followup_landmark_filename).drop('Landmark', axis=1)
>>> moving_indices = moving_indices.rename(columns={'X' : 'x', 'Y' : 'y', 'Z' : 'z'})
>>> moving_indices['y'] = moving_indices['y'] + 239
>>>
>>> moving_points = np.zeros(moving_indices.shape)
>>> for j in range(moving_indices.shape[0]):
>>>     moving_points[j,:] = ants.transform_index_to_physical_point(baseline_images[0], (moving_indices.iloc[j].values).astype(int))
>>> 
>>> moving_points_df = pd.DataFrame(data = {'x': moving_points[:,0], 'y': moving_points[:,1], 'z': moving_points[:,2]})
>>> moving_warped_points = ants.apply_transforms_to_points(3, moving_points_df, reg['invtransforms'], whichtoinvert=(True, False))   
>>> moving_warped_points = moving_warped_points.to_numpy()   
>>> moving_warped_points_df = pd.DataFrame(data=moving_warped_points, columns=['X', 'Y', 'Z'])
>>> moving_warped_points_df.insert(0, "Landmark", list(range(1, moving_points.shape[0]+1)))
>>> moving_warped_points_df.to_csv(warped_followup_landmark_file, index=False)
```
