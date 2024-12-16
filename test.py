with open('result/cites.txt', 'r', encoding='utf-8') as f:
    cites = f.readlines()

for i, cite in enumerate(cites):
    left = cite.split('. ')[1:]
    print(left)