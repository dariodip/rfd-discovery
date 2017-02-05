import matplotlib.pyplot as plt
import pandas as pd
import os
from utils.utils import check_sep_n_header
plt.style.use('ggplot')


def getfiles(dirpath):
    a = [s for s in os.listdir(dirpath)
         if os.path.isfile(os.path.join(dirpath, s)) and s.endswith(".csv")]
    a.sort(key=lambda s: os.path.getmtime(os.path.join(dirpath, s)))
    a.reverse()
    return a


def plot():
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
    print(grouped_df)
    grouped_df = grouped_df.sort_values(by=['ds_file_size_B'])
    plot1 = grouped_df.plot(x='ds_file_size_B', y="time_elapsed", marker='.', markersize=10, title="Time elapsed respect dataset's file size")
    plot1.set(xlabel="dataset's file size", ylabel='time elapsed')
    plot2 = grouped_df.plot(x='ds_len', y='time_elapsed', kind='scatter', s=grouped_df['ds_attr_size']*100, title="Time elapsed respect row's number")
    plot2.set(xlabel="dataset row's number", ylabel='time elapsed')

    coords = []
    for _, row in grouped_df.iterrows():
        coords.append((row['ds_len'], row['time_elapsed'], row.name))

    for x, y, name in coords:
        plot2.text(x, y, name[:-4]) # remove the .csv format from the name
    plt.show()

if __name__ == "__main__":
    plot()
