import matplotlib.pyplot as plt
import matplotlib.cm as cm
import pandas as pd
import numpy as np
import os

from utils.utils import check_sep_n_header
from matplotlib.lines import Line2D

plt.style.use('ggplot')

"""This modules contain code used to create graphics plot showing the running time of the algorithm"""


def getfiles(dirpath):
    """
    Given a valid path of a directory, it return a list with all the CSV files' names contained in the directory ordered
    by last modification time.
    :param dirpath: valid path to a directory
    :type dirpath: str
    :return: list of all the CSV files in dirpath
    :rtype: list
    """
    a = [s for s in os.listdir(dirpath)
         if os.path.isfile(os.path.join(dirpath, s)) and s.endswith(".csv")]
    a.sort(key=lambda s: os.path.getmtime(os.path.join(dirpath, s)))
    a.reverse()
    return a


def plot():
    """
    Given a set of CSV files produced by the module time_counting_test in the directory resources/test, it use the content of
    the most recent file to produce four plots.
    Three plots are scatterplots that shows the relation between the elapsed times, the dataset's rows number and
    the dataset's attributes number for each dataset. Each plot place two of this attributes on the two axis,
    and use the third one as the point radius, where each point corresponds to a dataset.
    The fourth graph show the increasing of the running time respect the increasing of the RFDs found.
    """
    dirpath = os.path.abspath("../resources/test")
    files = getfiles(dirpath)
    file_path = os.path.join(dirpath, files[0])
    try:
        sep, _ = check_sep_n_header(file_path)
    except TypeError:
        print("Unable to find separator in file ", files[0])
        return


    test_df = pd.read_csv(file_path, sep=sep, decimal=',')
    grouped_df = test_df.groupby(['ds_name']).mean()
    datasets = list(grouped_df.index)

    print(grouped_df)


    attr_param = pd.DataFrame({
        "label": ['numero di attributi', 'numero di righe', 'tempo impiegato in ms'],
        "incr_factor" : [1000, 10, 1.5],
        "limits": [(1, 7), (-500, 3000), (-5000, 40000)]
    }, index=['ds_attr_size', 'ds_len', 'time_elapsed'])

    ds_color = pd.DataFrame(cm.RdYlGn(np.linspace(0, 1, len(grouped_df))), index=list(grouped_df.index))

    combinations = pd.DataFrame([
                ['ds_attr_size', 'ds_len', 'time_elapsed', 'numero di righe rispetto al numero di attributi'],
                ['ds_attr_size', 'time_elapsed', 'ds_len', 'tempo impiegato rispetto al numero di attributi'],
                ['ds_len', 'time_elapsed', 'ds_attr_size', 'tempo impiegato rispetto al numero di righe']],
                columns=["x", "y", "shape", "title"])

    for index in range(len(attr_param.index)):
        _, ax = plt.subplots()

        ax.set_facecolor('white')
        plt.grid(color='grey')
        ax.spines['bottom'].set_color('grey')
        ax.spines['top'].set_color('grey')
        ax.spines['right'].set_color('grey')
        ax.spines['left'].set_color('grey')

        comb = combinations.iloc[index]

        plt.xlim(attr_param["limits"][comb['x']])
        plt.xlabel(attr_param["label"][comb['x']])
        plt.ylim(attr_param["limits"][comb['y']])
        plt.ylabel(attr_param["label"][comb['y']])
        plt.title(comb["title"])

        grouped_df = grouped_df.sort_values(by=[comb['shape']], ascending=False)
        for ds_name, row in grouped_df.iterrows():
            xval = grouped_df[comb['x']][ds_name]
            yval = grouped_df[comb['y']][ds_name]
            sval = grouped_df[comb['shape']][ds_name] * attr_param["incr_factor"][comb['shape']]
            ax.scatter(x=xval, y=yval, s=sval, c=ds_color.loc[ds_name],
                       label="{}: time {} ms".format(ds_name[:-4], int(grouped_df["time_elapsed"][ds_name])))

        lgnd = plt.legend(scatterpoints=1, fontsize=10)
        for i in range(len(grouped_df)):
            lgnd.legendHandles[i]._sizes = [75]

    for ds in datasets:
        _, ax = plt.subplots()
        grouped_rfd =  test_df[test_df.ds_name == ds][['rfd_count','time_elapsed']]\
                            .groupby(by=['rfd_count']).mean()


        plot = grouped_rfd.plot(y="time_elapsed", marker='.', markersize=10,
                        title="Tempo impiegato rispetto al numero di RFD trovate nel dataset {}".format(ds[:-4]), ax=ax, legend=False)

        legend_dots = []
        for rfd_count, row in grouped_rfd.iterrows():
            legend_text = "{} RFD: tempo {} ms".format(int(rfd_count), row['time_elapsed'])
            legend_dots.append(Line2D(range(1), range(1), linewidth=0, color="white", marker='o', markerfacecolor="red", label=legend_text))

        plot.set(xlabel="RFD trovate", ylabel='Tempo impiegato in ms')
        ax.legend(handles=legend_dots)
    plt.show()


if __name__ == "__main__":
    plot()
