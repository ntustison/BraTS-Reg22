# ANTsX evaluation in the [BraTS-Reg22 challenge](https://www.med.upenn.edu/cbica/brats-reg-challenge/)

* [Training phase leaderboard](https://www.cbica.upenn.edu/BraTSReg2022/lboardTraining.html)
* [Validation phase leaderboard](https://www.cbica.upenn.edu/BraTSReg2022/lboardValidation.html)

## Written description

BraTS-Reg22 data were processed using previously vetted and frequently used registration parameter sets [1-2] which have been 
packaged in the different ANTsX platforms, specifically ANTs, ANTsPy, and ANTsR.  Each of these
parameter sets consists of multiple transform stages for determining anatomical corresponce.
Initial linear estimation of transform parameters comprises center of (intensity) mass alignment 
followed by optimization of both rigid and affine transforms using mutual information 
as the similarity metric [3].  The final deformable alignment utilizes symmetric normalization (SyN)
with Gaussian [4] or B-spline [5] regularization and a neighborhood cross-correlation [] or 
mutual information similarity metric.  Although performance with the training data was similar across 
the resulting six different ANTs variants, SyN with Gaussian regularization and a neighborhood 
cross-correlation similarity metric (neighborhood radius = 2 voxels) was selected for the validation
phase.

[1] [Avants et al., _A reproducible evaluation of ANTs similarity metric performance in brain image registration_.](https://pubmed.ncbi.nlm.nih.gov/20851191/)
[2] [Avants et al., _The Insight ToolKit Image Registration Framework_.](http://www.ncbi.nlm.nih.gov/pubmed/24817849)
[3] [Viola and Wells, _Alignment by Maximization of Mutual Information_.](https://ieeexplore.ieee.org/document/466930)
[4] [Avants et al., _Symmetric diffeomorphic image registration with cross-correlation: evaluating automated labeling of elderly and neurodegenerative brain_.](https://pubmed.ncbi.nlm.nih.gov/17659998/)
[5] [Tustison and Avants, _Explicit B-spline regularization in diffeomorphic image registration_.](http://www.ncbi.nlm.nih.gov/pubmed/24409140)

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

Although the organizers employed several metrics for evaluating performance, we 
employed the following "accuracy improvement" measure for assessment:

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
>>> moving_indices = pd.read_csv(followup_landmark_file).drop('Landmark', axis=1)
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

![GoodhartsLaw](https://user-images.githubusercontent.com/324811/204690199-685a44e3-b7d4-4d25-a19b-40b06c50c29d.png)




