import torch
import numpy as np
import nibabel as nib
from tqdm import tqdm

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def to_channels ( arr : np . ndarray , dtype = np . uint8 ) -> np . ndarray :
    
    unique_classes = np.unique(arr) 
    one_hot = np.zeros(arr.shape + (len(unique_classes),), dtype=dtype)  
    for c in unique_classes:
        c = int(c)
        one_hot[..., c:c + 1][arr == c] = 1 

    return one_hot

def load_data_2D ( imageNames , normImage = False , categorical = False , dtype = np . float32 ,
                  getAffines = False , early_stop = False ) :
    '''
    Load medical image data from names , cases list provided into a list for each .

    This function pre - allocates 4D arrays for conv2d to avoid excessive memory &
    usage .

    normImage : bool ( normalise the image 0.0 -1.0)
    early_stop : Stop loading pre - maturely , leaves arrays mostly empty , for quick &
    loading and testing scripts .
    '''
    
    affines = []

   
    num = len(imageNames)
    print("Length of Images: ", num)
    first_case = nib.load(imageNames[0]).get_fdata(caching='unchanged')
    if len(first_case.shape) == 3:

        first_case = first_case [: ,: ,0] 
    if categorical :
        first_case = to_channels( first_case, dtype=dtype)
        rows, cols, channels = first_case.shape
        images = np.zeros ((num, rows, cols, channels), dtype=dtype)
    else :
        rows , cols = first_case.shape
        images = np.zeros ((num, rows, cols ) , dtype=dtype )

    for i, inName in enumerate (tqdm(imageNames)) :
        try:
            niftiImage = nib.load(inName)
            inImage = niftiImage.get_fdata(caching='unchanged')
            affine = niftiImage.affine
            if len(inImage.shape) == 3:
                inImage = inImage [:,:,0] 
            inImage = inImage.astype(dtype)
            if normImage:
                inImage = ( inImage - inImage . mean () ) / inImage . std ()
            if categorical :
                inImage = to_channels ( inImage , dtype = dtype )
                images [i,:,:,:] = inImage
            else :
                images [i ,: ,:] = inImage

            affines . append ( affine )
            if i > 20 and early_stop :
                break
        except:
            print("Error occured on image: ", i, inName)
            
    if getAffines :
        return images , affines
    else :
        return images