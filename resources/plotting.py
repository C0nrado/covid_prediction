"""This is a python modulo for grouping plotting functions."""

def parallelplot(df, category, centroids=False, interval=False, color=None, alpha=None, ax=None):
    """Plot records of DataFrame *df* in parallel coordinates in accordance to the categoriacal field *category*."""

    fields = df.drop(category, axis=1).columns
    cat_values = df[category].unique()
    xs = np.arange(len(fields))
    ymin, ymax = df.min().min() * 1.1, df.max().max() * 1.1
    lineHandle = []
 
    if ax is None:
        _, ax = plt.subplots()
    ax.set_ylim(ymin, ymax)

    if centroids:
        data = df.groupby(category).mean().reindex(cat_values).to_numpy()
        if interval == 'std':
            std = df.groupby(category).std().reindex(cat_values)
            sup = data + std.to_numpy() * 1.96
            low = data - std.to_numpy() * 1.96
        if interval == 'robust':
            pctl = df.groupby(category).apply(lambda s: s.quantile([.05, .95])).reindex(cat_values, level=0).swaplevel()
            sup = pctl.loc[0.95, fields].to_numpy()
            low = pctl.loc[0.05, fields].to_numpy()

        for i, ys in enumerate(data):
            line = ax.plot(xs, ys, color='k', lw=1.5, marker='s', mfc='C'+str(i), ms=7)
            lineHandle.append(line[0])
            if interval:
                ax.fill_between(xs, sup[i], low[i], alpha=alpha, lw=.5, color='C'+str(i))

    else:
        data = [df[df[category] == value][fields].to_numpy() for value in cat_values]
        for i, ys in enumerate(data):
            lines = ax.plot(ys.T, color='C'+str(i), alpha=alpha)
            lineHandle.append(lines[0])
    
    for i in xs[1:-1]:
        ax.vlines(i, ymin, ymax, lw=.5, color='gray')
    ax.set_xlim(xs.min(), xs.max())
    ax.set_xticks(xs)
    ax.set_xticklabels(fields)
    ax.set_ylim(ymin, ymax)
    ax.legend(lineHandle, cat_values, title='Cluster')

    return ax

def _parse_interval(interval):
    """this function parses interval string inputs."""

    if interval is None:
        return None
    else:
        match = re.match(r'([1-3])?(sigma|robust)', interval)
        try:
            match.groups()
        except:
            raise ValueError('Only [n]sigma or robust are valid inputs.')
    return match.groups()