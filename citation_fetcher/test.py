import re

import pybtex

cite = """
@inproceedings{moura2021fragmentation,
  title={Fragmentation, truncation, and timeouts: are large DNS messages falling to bits?},
  author={Moura, Giovane CM and M{\\"u}ller, Moritz and Davids, Marco and Wullink, Maarten and Hesselman, Cristian},
  booktitle={Passive and Active Measurement: 22nd International Conference, PAM 2021, Virtual Event, March 29--April 1, 2021, Proceedings 22},
  pages={460--477},
  year={2021},
  organization={Springer}
}
"""
mts = re.findall(r'(\{\\"(.*?)})', cite)
for mt in mts:
    cite = cite.replace(mt[0], mt[1])
print(cite)

text = pybtex.format_from_file("result/1.bib", style="plain")
print(text)