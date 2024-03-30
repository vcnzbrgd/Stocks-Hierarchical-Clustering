import pandas as pd
import numpy as np
import yfinance as yf
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import minimum_spanning_tree
from scipy.sparse.csgraph import dijkstra
from scipy.cluster.hierarchy import dendrogram, linkage
from scipy.spatial.distance import squareform
import matplotlib.pyplot as plt



class HierarchicalClustering():
    """
    A class for performing hierarchical clustering on financial data.

    This class implements hierarchical clustering by first calculating a distance matrix based
    on stock returns correlations, then constructing a minimum spanning tree (MST) from this
    distance matrix, and finally determining the ultrametric distance matrix which is used for
    clustering.

    Attributes:
        tickers (list of str): A list of ticker symbols (from Yahoo! Finance) to be analyzed.
        cache (dict): A cache to store downloaded returns data for efficiency.
    """


    def __init__(self, tickers):
        """
        Initializes the HierarchicalClustering with a list of tickers.

        Parameters:
            tickers (list of str): A list of ticker symbols to be analyzed.
        """

        self.tickers = tickers
        self.cache = {}  # initialize the cache for downloaded returns



    def download_returns(self, start_date, end_date=None, drop_series_with_nans=True):
        """
        Downloads and caches the adjusted close returns from Yahoo! Finance for the given tickers and date range.

        If the data is already cached, it retrieves it from the cache to avoid unnecessary downloads.

        Parameters:
            start_date (str): The start date for the data download (YYYY-MM-DD format).
            end_date (str, optional): The end date for the data download (YYYY-MM-DD format). Defaults to None.
            drop_series_with_nans (bool, optional): Whether to drop series with NaN values. Defaults to True.

        Returns:
            pandas.DataFrame: A DataFrame with the adjusted close returns for the tickers.
        """

        # check if the data is already in the cache, otherwise proceed to download
        cache_key = (tuple(self.tickers), start_date, end_date, drop_series_with_nans)
        if cache_key in self.cache:
            return self.cache[cache_key]
        else:
            df = yf.download(self.tickers, start=start_date, end=end_date)['Adj Close']
            df.columns.name=''

            if drop_series_with_nans == True:
                df.dropna(axis=1, inplace=True)

            self.cache[cache_key] = df

        return df
    


    def distance_matrix(self, start_date, end_date=None):
        """
        Computes the distance matrix for the given tickers based on their returns.

        The distance is calculated as the square root of 2*(1 - correlation), which
        transforms the correlation matrix into a distance matrix.

        Parameters:
            start_date (str): The start date for calculating returns (YYYY-MM-DD format).
            end_date (str, optional): The end date for calculating returns (YYYY-MM-DD format). Defaults to None.

        Returns:
            pandas.DataFrame: A distance matrix for the tickers.
        """

        distance_matrix = (2*(1 - self.download_returns(start_date, end_date, drop_series_with_nans=True).corr()))**0.5
        return distance_matrix
    


    def minimum_spanning_tree(self, start_date, end_date=None):
        """
        Constructs a minimum spanning tree (MST) from the distance matrix of stock returns.

        Parameters:
            start_date (str): The start date for calculating the distance matrix (YYYY-MM-DD format).
            end_date (str, optional): The end date for calculating the distance matrix (YYYY-MM-DD format). Defaults to None.

        Returns:
            pandas.DataFrame: The MST as a DataFrame where the indices and columns are ticker symbols and the values are distances.
        """

        d_matrix = self.distance_matrix(start_date, end_date)

        mst = pd.DataFrame(
            minimum_spanning_tree(
                csr_matrix(d_matrix.mask(np.tril(np.ones(d_matrix.shape).astype(bool))).values)
            ).toarray(), index=d_matrix.index, columns=d_matrix.columns)
        
        return mst
    


    def predecessors_matrix(self, start_date, end_date=None):
        """
        Computes the predecessors matrix from the minimum spanning tree (MST).

        This matrix is used to find the shortest paths between nodes in the MST.

        Parameters:
            start_date (str): The start date for calculating the MST (YYYY-MM-DD format).
            end_date (str, optional): The end date for calculating the MST (YYYY-MM-DD format). Defaults to None.

        Returns:
            pandas.DataFrame: A DataFrame representing the predecessors matrix.
        """
        
        mst = self.minimum_spanning_tree(start_date, end_date)

        _ , predecessors = dijkstra(
            csgraph=csr_matrix(mst.values),    # Calculate distace on MST
            directed=False,    # The MST is undirected, hence must be False
            return_predecessors=True
            )
        predecessors = pd.DataFrame(predecessors, index=mst.index, columns=mst.columns)
        predecessors = predecessors.replace(dict(zip([i for i in range(len(predecessors.columns))], predecessors.columns)))
        
        return predecessors
    
    


    def ultrametric_distance_matrix(self, start_date, end_date=None):
        """
        Calculates the ultrametric distance matrix based on the MST.

        The ultrametric distance between two points is defined as the maximum edge weight on the shortest path between them in the MST.

        Parameters:
            start_date (str): The start date for calculating the ultrametric distance (YYYY-MM-DD format).
            end_date (str, optional): The end date for calculating the ultrametric distance (YYYY-MM-DD format). Defaults to None.

        Returns:
            pandas.DataFrame: The ultrametric distance matrix.
        """


        def find_path_between_stocks(go_from, go_to, predecessors):
            path = []
            path.append(go_to)
            
            if predecessors.loc[go_from, go_to] == -9999:
                raise Exception(f"Trying to go from {go_from} to {go_to}. You can't have have a starting point equal to destination")
            
            while go_from != predecessors.loc[go_from, go_to]:
                go_to = predecessors.loc[go_from, go_to]
                path.append(go_to)

            path.append(go_from)
            path.reverse()
            steps = []
            
            for i in range(1, len(path)):
                steps.append((path[i-1], path[i]))
            
            return steps


        d_matrix = self.distance_matrix(start_date, end_date)
        predecessors = self.predecessors_matrix(start_date, end_date)

        ultra_dist = pd.DataFrame(np.full(d_matrix.shape, np.nan), index=d_matrix.index, columns=d_matrix.columns)
        for i in d_matrix.index:
            for j in d_matrix.columns:
                if i==j:
                    continue
                temp_steps = find_path_between_stocks(i, j, predecessors)

                steps_length = []
                for k in temp_steps:
                    steps_length.append(d_matrix.loc[k[0], k[1]])

                ultra_dist.loc[i, j] = max(steps_length)
                
        np.fill_diagonal(ultra_dist.values, 0)
        ultra_dist.columns.name=None
        ultra_dist.index.name=None
        
        return ultra_dist



def plot_dendrogram(ultra_dist):
    """
    Plots a dendrogram based on the ultrametric distance matrix.

    Parameters:
        ultra_dist (pandas.DataFrame): The ultrametric distance matrix.
    """
    # Convert the ultrametric distance matrix into a condensed distance matrix
    # suitable for use with the linkage function.
    condensed_dist = squareform(ultra_dist, checks=False)
    
    # Perform hierarchical/agglomerative clustering.
    Z = linkage(condensed_dist, 'ward')
    
    # Plot the dendrogram with vertical orientation.
    if len(ultra_dist) < 50:
        plt.figure(figsize=(7, len(ultra_dist)/2))
    elif (len(ultra_dist) >= 50) & (len(ultra_dist) < 250):
        plt.figure(figsize=(10, len(ultra_dist)/3))
    else:
        plt.figure(figsize=(12.5, len(ultra_dist)/4))
    
    dendrogram(Z, labels=ultra_dist.columns, orientation='left', leaf_font_size=10)

    plt.title('Dendrogram of Ultrametric Distances')
    plt.xlabel('Distance')
    plt.show()

