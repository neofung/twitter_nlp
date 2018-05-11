import pandas as pd
import numpy
from tqdm import tqdm

city_and_state_raw = pd.read_csv('us_cities_states_counties.csv', sep='|')
us_city_and_state_set = set()
for t in city_and_state_raw['City'].unique():
    if isinstance(t, str):
        us_city_and_state_set.add(t.lower())

for t in city_and_state_raw['State full'].unique():
    if isinstance(t, str) and t.lower() not in us_city_and_state_set:
        if t != numpy.nan:
            us_city_and_state_set.add(t.lower())

common_word_set = set()
with open('20k.txt') as fin:
    for line in fin:
        line = line.strip()
        common_word_set.add(line)

FILTER_LIST = ['O', 'B-facility', 'B-geo-loc', 'B-other']

with open('prediction.txt') as fin:
    with open('train.origin', 'w') as origin:
        with open('train.extraction', 'w') as extraction:
            count = 0
            total = 0
            empty_count = 0
            for line in tqdm(fin):
                total += 1
                line = line.strip()
                items = [item.split('/') for item in line.split(' ')]
                output_lines = [' '.join([t[0] for t in items]) + '\n']

                if any([t for t in items if len(t)!=2]):
                    continue

                if any([t for t in items if t[1] not in FILTER_LIST]):
                    np = []
                    ner_type = None
                    for item in items:
                        if not ner_type and item[1].startswith('B') and item[1] not in FILTER_LIST:
                            ner_type = item[1][2:]
                            np.append(item[0])
                        elif ner_type and item[1].endswith(ner_type):
                            np.append(item[0])
                        elif ner_type and item[1] == 'O':
                            if item[0] == '.' or (
                                    len(np) == 1 and np[0].lower() in common_word_set or 'vegas' in np
                            ):
                                ner_type = None
                                np = []
                                continue
                            np_str = ' '.join(np)
                            if np_str.lower() not in us_city_and_state_set:
                                output_lines.append(np_str + '\n')
                            ner_type = None
                            np = []
                    if np:
                        if len(np) == 1 and np[0] in common_word_set or 'vegas' in np:
                            ner_type = None
                            np = []
                            continue
                        np_str = ' '.join(np)
                        if np_str.lower() not in us_city_and_state_set:
                            output_lines.append(np_str + '\n')
                        np = []

                if len(output_lines) > 1:
                    origin.write(output_lines[0])
                    extraction.write(output_lines[1])
                    count += 1
                else:
                    if empty_count>count/9:
                        continue
                    origin.write(output_lines[0])
                    extraction.write(' \n')
                    empty_count+=1


        print('%d/%d=%f%%' % (count, total, count * 100.0 / total))
