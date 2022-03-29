import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# create a folder for output in task1
import os
if not os.path.exists('task1-output'):
    os.makedirs('task1-output')

# find csv file names in lab1-data folder...
def find_filename(path):
    import os
    return [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]


# func for reading and parsing csv...
def read_csv(path, filename, codec, sep=','):
    data = []
    with open(path + filename, 'r', encoding=codec) as f:
        # A missing header...
        header = f.readline().replace('"', '').strip('\n').split(sep)

        lst_sep = []

        # next(f)
        for line in f.readlines():
            # deal with mal-informed input...
            line = line.replace("'","").strip('\n')

            # reject line if any anomalies exist - no generation of exceptions...
            # A missing field e.g.) two delimiters next to each other...
            if str(sep*2) in line:
                print('{}: A missing field - line ignored.'.format(line))
                continue

            # double quotes in wrong place or missing...
            line_sep = [v.replace('"', '') for v in line.split(sep)]
            lst_sep.append(len(line_sep))
            avg_sep = int(sum(lst_sep) / len(lst_sep))

            # less or more fields than expected...
            if (len(line_sep) < avg_sep) or (len(line_sep) > avg_sep):
                print('{}: Less or more fields than expected - line ignored.'.format(line_sep))
                continue

            data.append(line_sep)

    # func to check if unexpected character in a numeric field...
    def is_valid_decimal(num):
        try:
            float(num)
        except ValueError:
            return False
        else:
            return True

    data = np.array(data)

    for i in range(data.shape[1]):
        lst_bool = [is_valid_decimal(s) for s in data[:,i]]

        # if there is more True values than False in lst_bool, the column is numeric
        # remove all the rows that returns False for is_valid_decimal(num)
        unique, counts = np.unique(lst_bool, return_counts=True)
        if False and True in lst_bool:
            if lst_bool.count(True) > lst_bool.count(False):
                data = data[lst_bool,:]

    return header, data


# func for computing min, max, mean and std for each component of weather data...
def feature(data):
    data = data.astype(np.float)
    minimum = np.amin(data)
    maximum = np.amax(data)
    mean = np.mean(data)
    std = np.std(data)

    return minimum, maximum, mean, std


# calculating and printing features of each component to a report...
f = open("./task1-output/task1-min-max-mean-std-features-report.txt", 'w')
path = './lab1-data/'
filenames = find_filename(path)
label = 'Minimum, maximum, mean and standard deviation for each component:'
f.write(label)
print(label)

# writing minimum, maximum, mean and standard deviation for each component to the report
for filename in filenames:
    header, data = read_csv(path, filename, 'utf-8-sig')
    for i in range(1, data.shape[1]):
        write_data = '\n{} {} Min: {} Max: {} Mean: {} Std: {}'\
            .format(filename.strip('.csv'), header[i], round(feature(data[:,i])[0], 2), round(feature(data[:,i])[1], 2),
                    round(feature(data[:,i])[2], 2), round(feature(data[:,i])[3], 2))
        f.write(write_data)
        print(write_data)

f.close()

# Parse and collect all the data columns in several files in one pandas dataframe...
df = pd.DataFrame()
for filename in filenames:
    header, data = read_csv(path, filename, 'utf-8-sig')

    # indoor and outdoor temp columns have same column names. Fix this...
    if 'indoor' in filename:
        new_header = []
        for i in header:
            if i != 'DateTime':
                new_header.append(i + ' ' + 'indoor')
            else:
                new_header.append(i)
        header = new_header

    elif 'outside' in filename:
        new_header = []
        for i in header:
            if i != 'DateTime':
                new_header.append(i + ' ' + 'outside')
            else:
                new_header.append(i)
        header = new_header

    data = pd.DataFrame(data, columns=header)
    data['DateTime'] = pd.to_datetime(data['DateTime'])

    if df.shape[0] == 0:
        df = data
    else:
        df = df.merge(data, on='DateTime')


# numeric values are in string format. Fix to numeric format...
df.loc[:, 'Baro':'mm'] = df.loc[:, 'Baro':'mm'].astype('float')
# print(df.describe())
# print(df.columns)
# Change column name mm and Baro to Rainfall and Barometer respectively
df.columns = [column_name.replace('mm', 'Rainfall').replace('Baro', 'Barometer') for column_name in df.columns]

# create separate dataframe, df_corr for creating correlation matrix...
df_corr = df.loc[:, ['DateTime', 'Barometer', 'Humidity indoor', 'Temperature indoor', 'Temperature outside', 'Rainfall']]
# print('Features:\n', df_corr.describe())
corr = df_corr.corr()

# export df and df_corr for task2...
df.columns = [i.replace('_range', '') for i in df.columns]
df.to_csv('df.csv', index=False)

df_corr.to_csv('df_corr.csv', index=False)

# set of plots for identification of correlations between variables
# plot correlation matrix (no min and max values)...
sns.pairplot(df_corr, markers='o')
plt.tight_layout()
plt.savefig('./task1-output/corr_scatter_5x5.png')
plt.show()

# plot correlation heatmap...
# get correlation matrix
sns.heatmap(round(df_corr.corr(), 2), annot=True)
plt.tight_layout()
plt.savefig('./task1-output/corr_heatmap_5x5.png')
plt.show()

# ''' another correlation matrix with min and max temp values '''
# sns.pairplot(df, markers='o')
# plt.tight_layout()
# plt.savefig('corr_scatter_9x9.png', dpi=300)
# plt.show()
#
# df.columns = [i.replace('_range', '') for i in df.columns]
#
# sns.heatmap(round(df.corr(), 2), annot=True)
# plt.tight_layout()
# plt.savefig('corr_heatmap_9x9.png', dpi=300)
# plt.show()