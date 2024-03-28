# Stocks Hierarchical Clustering

Goal of this project is to replicate the hierarchical clustering based on assets' prices proposed in the paper Hierarchical Structure in Financial Markets by Mantegna (1998).
The idea outlined in Mantegna’s work is to create a taxonomy using a metric based solely on the
information provided by the time series of asset prices. He demonstrates that the obtained unsupervised clustering
reflects an aggregation somewhat similar to the one achievable labelling stocks by sector.

The steps of the process are:
- Create a Distance metric $$d$$ from pairwise stocks correlation matrix. The distance is defined as: 

$$d(i,j) = \sqrt{2 \times (1- \rho_{i,j})}$$
