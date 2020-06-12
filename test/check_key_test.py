import pandas as pd
from nltk import edit_distance


def hamming_distance(s1, s2):
    distance = 0
    if s1 != s2:
        distance += max(len(s1), len(s2)) - min(len(s1), len(s2))
        for i in range(min(len(s1), len(s2))):
            if s1[i] != s2[i]:
                distance += 1
    return distance


keys = pd.read_csv('extras\\claves.csv', header=None)
keys.columns = ['execution', 'date', 'K']
keys['K'] = keys['K'].str[1:-1]
# keys = pd.concat([keys, keys['K'].str.split(';', expand=True)], axis=1)
# keys.drop(columns='K', inplace=True)
# keys.drop(columns='execution', inplace=True)
# keys.drop(columns=keys.columns[-1], inplace=True)
# keys[0] = keys[0].str[1:]
equals_keys = keys.groupby(['date'], as_index=True)['K'].apply(lambda x: (x == x.iloc[0]).all()).reset_index()

malfunction_days = equals_keys[equals_keys.K == False]
good_keys = keys[keys['date'].isin(equals_keys.loc[equals_keys.K == True, 'date'].unique())].groupby(['date'],
                                                                                                     as_index=False)['K'].min()
good_keys = pd.concat([good_keys, good_keys['K'].str.split(';', expand=True)], axis=1)

for index, row in malfunction_days.iterrows():
    print(f"The key of the users of date {row['date']} are distinct")


hamming_distance_list = []
length_list = []

for i in range(good_keys.shape[0]):
    row_hamming = []
    row_length = []
    for j in range(good_keys.shape[0]):
        row_hamming.append(hamming_distance(good_keys['K'].iloc[i], good_keys['K'].iloc[j]))
        row_length.append(max(len(good_keys['K'].iloc[i]), len(good_keys['K'].iloc[j])))
    hamming_distance_list.append(row_hamming)
    length_list.append(row_length)
pd.DataFrame(hamming_distance_list).to_csv('extras\\hamming_distance.csv', header=None)
pd.DataFrame(length_list).to_csv('extras\\string_lenght.csv', header=None)
print("End")
