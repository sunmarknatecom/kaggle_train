import pydicom
import matplotlib.pyplot as plt
import cv2
import numpy as np

f = pydicom.dcmread("pet.dcm")
ds = f.pixel_array
f_ds = (ds/np.max(ds))*255
n_ds = f_ds.astype('uint8')
color_map = plt.colormaps()


for i in range(len(color_map)):
    plt.imshow(n_ds, interpolation='bicubic', cmap=color_map[i])
    plt.title("%s : %s" %(color_map[i], i))
    plt.xticks([])
    plt.yticks([])
    plt.show()

print(color_map)