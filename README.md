# Stocks Hierarchical Clustering

Goal of this project is to replicate the hierarchical clustering based on assets' prices proposed in the paper Hierarchical Structure in Financial Markets by Mantegna (1998).
The idea outlined in Mantegna’s work is to create a taxonomy using a metric based solely on the
information provided by the time series of asset prices. He demonstrates that the obtained unsupervised clustering
reflects an aggregation somewhat similar to the one achievable labelling stocks by sector.

The steps of the process are:
- Create a Distance matrix $d$ from the matrix of pairwise stocks correlation. The distance between asset $i$ and asset $j$ is defined as: 

$$d(i,j) = \sqrt{2 \times (1- \rho_{i,j})}$$

- Compute the Minimum Spanning Tree on the Distance matrix

- Build an Ultrametric Distance $d'(i,j)$ starting from $d(i,j)$. The Ultrametric distance between $i$ and $j$ is defined as the maximum value among all the pairwise distances evaluated in the path that connects $i$ and $j$. For example:

$$d'(A,G)=$max(3,2,8,7,4,1,3)=8$$

<img width="372" alt="Screenshot 2024-03-28 at 19 42 15" src="https://github.com/vcnzbrgd/Stocks-Hierarchical-Clustering/assets/127797045/0218708f-10ba-46a6-8515-6522cdf90f7c">
