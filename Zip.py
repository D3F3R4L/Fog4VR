#!/usr/bin/env python
# coding: utf-8

# In[1]:


from scipy.stats import zipf
import numpy as np
import matplotlib.pyplot as plt

a = 2
k=1
# x = np.arange(zipf.ppf(0.01, a),
#               zipf.ppf(0.99, a))

# rv = zipf(a)
# prob = zipf.cdf(x, a)
# np.allclose(x, zipf.ppf(prob, a))
r = zipf.rvs(a, size=10)
pf = zipf.pmf(k, a, loc=0)
# print(r)
#print(pf)
# pmf(k, a, loc=0)
# la = 1-pf


# In[2]:


# np.random.choice(5, 3, p=[0.1, 0, 0.3, 0.6, 0])

from random import choices
files = [0,1, 2, 3, 4, 5, 6,7,8,9]
weights = [0.6079271018540265, 0.04356365534955261, 0.04356365534955261, 0.04356365534955261,
           0.04356365534955261, 0.04356365534955261, 0.04356365534955261, 0.04356365534955261,
           0.04356365534955261, 0.04356365534955261]
x=choices(files, weights)
print(x[0])


# In[ ]:




