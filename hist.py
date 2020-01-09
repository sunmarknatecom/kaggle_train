import numpy
import scipy.spatial
import pandas as pd
import matplotlib.pyplot as plt

d = 2
data = numpy.random.uniform(size=d*1000).reshape((1000,d))
distances = scipy.spatial.distance.cdist(data, data)
pd.Series(distances.reshape(1000000)).hist(bins=50)
plt.title("%i dimension distance between points" %d)
plt.show()