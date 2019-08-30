import re

outpath = '菌' + '_project_leader.xls'
try:
    with open(outpath, 'r', encoding='utf-8') as prefile:
        prepmid = []
        for line in prefile:
            if line:
                # print(line)
                print(re.search('\t([^\t\n]+)$', line).group(1).strip())

except FileNotFoundError:
    prepmid = []

print(prepmid)
