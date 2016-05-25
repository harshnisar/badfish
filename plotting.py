
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import gridspec

def plot(self, kind, where = None, columns = None, how = 'any', **kwds):
    """
    One method to interface with different methods of visualizing missing data..

    Inspired by Pandas interface to plots.

    Parameters:
    -----------
    kind: str, required
        Type of visualisation.
        - 'pattern' : Visualize the possible patterns of missing data (default)
    
    where: list of columns
        Use subset of a data where particular columns are missing.

    columns: list of columns
        Only inspect a subset of the columns for analysis.

    how: str{'any'|'all'}
    

    """
    plt_func = {
    'pattern' : pattern_plot
    }

    plt_func[kind](mf = self, where = where, columns = columns, how = how, **kwds)

def pattern_plot(mf, where, columns, how, figsize = (20,10), norm = True, threshold = 0.10,
                 ascending = False , labels = True, fontsize = 12):
    
    

    z_ = mf.pattern(where = where, columns = columns, how = how, norm = norm,
                     threshold = threshold, ascending = ascending)
    # z = z.sort_values(0, ascending = False)
    # Excluding the last column.
    z = z_.iloc[:,:-1]

    # Saving column_labels of xlabels.
    column_labels = z.columns.tolist()

    z = z.values
    height = z.shape[0]
    width = z.shape[1]

    
    
    g = np.zeros((height, width, 3))
    g[z == True] = [1,0,0]
    g[z == False] = [0,0,1]

    fig = plt.figure(figsize=figsize)
    gs = gridspec.GridSpec(1, 1)
    ax0 = plt.subplot(gs[0])
    ax0.imshow(g, interpolation='none')
    ax0.set_aspect('auto')
        
    
    ax0.xaxis.tick_top()
 
    
    if labels:
        ax0.set_xticks(np.arange(0, width, 1))
        ax0.set_xticklabels(column_labels, rotation=90, ha='center', fontsize=fontsize)
    else:
        ax0.set_xticks([])    
    
    ax0.set_yticks(np.arange(0, height, 1))
    ysupports = z_.iloc[:,-1].map(lambda x: np.round(x, 3))
    ax0.set_yticklabels(ysupports, fontsize = fontsize)
    
    
    plt.grid(False)
    
    for yline in np.arange(0-0.5, height - 0.5, 1):
        ax0.axhline(yline, linestyle='-', color='k', alpha = 0.4) # horizontal lines
    for xline in np.arange(0-0.5, width - 0.5, 1):
        ax0.axvline(xline, linestyle='-', color='k', alpha = 0.4) # horizontal lines

    return ax0, fig
        
