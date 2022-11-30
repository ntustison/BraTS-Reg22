# ANTsX evaluation in the [BraTS-Reg22 challenge](https://www.med.upenn.edu/cbica/brats-reg-challenge/)

## Modalities to test on training data

* T1
* T1-contrast enhanced
* T2
* FLAIR
* T1-contrast enhanced + T2
* T1-contrast enhanced + FLAIR

## Parameter sets to test on training data

* antsRegistrationSyNQuick[a]
    * Rigid stage 
        * similarity metric:  MI with 32 bins
        * gradient step = 0.1
        * iterations per level = [1000,500,250,0]
        * shrink factors per level = [8,4,2,1]
        * smoothing factor per level = [3,2,1,0] (voxels)
    * Affine stage
        * same parameters as affine stage
* antsRegistrationSyNQuick[s,32]
    * Rigid stage 
        * Same as "antsRegistrationSyNQuick[a]"
    * Affine stage
        * Same as "antsRegistrationSyNQuick[a]"
    * SyN stage
        * Gaussian-based
        * similarity metric:  MI with 32 bins
        * gradient step = 0.1
        * iterations per level = [100,70,50,0]
        * shrink factors per level = [8,4,2,1]
        * smoothing factor per level = [3,2,1,0] (voxels) 
* antsRegistrationSyNQuick[b,32]
    * B-spline-based (mesh size per stage = [26,13,6.5,3.25] (mm)) 
    * other metrics same as "antsRegistrationSyNQuick[s,32]" 
* antsRegistrationSyN[s,2]
    * Rigid stage 
        * similarity metric:  MI with 32 bins
        * gradient step = 0.1
        * iterations per level = [1000,500,250,100]
        * shrink factors per level = [8,4,2,1]
        * smoothing factor per level = [3,2,1,0] (voxels)    
    * Affine stage
        * Same as rigid stage
    * SyN stage
        * Gaussian-based
        * similarity metric: CC with neighborhood radius of 2
        * gradient step = 0.1
        * iterations per level = [100,70,50,20]
        * shrink factors per level = [8,4,2,1]
        * smoothing factor per level = [3,2,1,0] (voxels)
* antsRegistrationSyN[b,2,26]
    * B-spline-based version of "antsRegistrationSyN[s,2]"
* antsRegistrationSyN[s,4]
    * Same as "antsRegistrationSyN[s,2]" with CC radius of 4
* antsRegistrationSyN[b,4,26]
    * B-spline-based version of "antsRegistrationSyN[s,4]"

## Training data results

### Accuracy

$$ \text{Accuracy improvement} = 1.0 - \frac{LandmarkError_{post}}{LandmarkError_{pre}} $$

<p align="middle">
  <img src="https://github.com/ntustison/BraTS-Reg22/blob/main/Analysis/accuracyBox.png" width="400" />
  <img src="https://github.com/ntustison/BraTS-Reg22/blob/main/Analysis/accuracy.png" width="400" /> 
</p>


### Timing (in seconds)

* Mac Pro 2020
* 2.5 GHz 28-Core Intel Xeon W
* `os.environ["ITK_GLOBAL_DEFAULT_NUMBER_OF_THREADS"] = "56"`

| Parameter set | Single modality | Two modalities |
| :---        |    :----:   |          ---: |
antsRegistrationSyNQuick[a]         |  4.6  |   NA
antsRegistrationSyNQuick[b,32,26]   | 39.8  |   38.5
antsRegistrationSyNQuick[s,32]      | 27.7  |  28.3
antsRegistrationSyN[s,2]            | 169.2 |  272.1
antsRegistrationSyN[b,2,26]         | 273.1 |  382.0
antsRegistrationSyN[s,4]            | 344.2 |  610.7
antsRegistrationSyN[b,4,26]         | 446.2 |  720.5

--------------------------------------------------------------------------------------------------------

## Apply antsRegistrationSyN[s,2] with T1-contrast enhanced to validation data

The choice of antsRegistrationSyN[s,2] with T1-contrast enhanced is due to combined 
performance and timing considerations.        
        
```python
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
>>>     moving_points[j,:] = ants.transform_index_to_physical_point(baseline_image, (moving_indices.iloc[j].values).astype(int))
>>> 
>>> moving_points_df = pd.DataFrame(data = {'x': moving_points[:,0], 'y': moving_points[:,1], 'z': moving_points[:,2]})
>>> moving_warped_points = ants.apply_transforms_to_points(3, moving_points_df, reg['invtransforms'], whichtoinvert=(True, False))   
>>> moving_warped_points = moving_warped_points.to_numpy()   
>>> moving_warped_points_df = pd.DataFrame(data=moving_warped_points, columns=['X', 'Y', 'Z'])
>>> moving_warped_points_df.insert(0, "Landmark", list(range(1, moving_points.shape[0]+1)))
>>> moving_warped_points_df.to_csv(warped_followup_landmark_file, index=False)
```
-----------------------------------------------------------
![GoodhartsLaw](https://user-images.githubusercontent.com/324811/204688577-e560b992-d2af-4bdd-9ee6-2c47674cc946.png)



