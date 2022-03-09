from os import listdir
from posixpath import dirname
from os.path import join
from sssom.parsers import read_sssom_table
from sssom.writers import write_table
from sssom.util import merge_msdf

INPUT_DIR = join(dirname(dirname(__file__)), "data/input")
OUT_PREFIX = 'confident_'
TSVS = [x for x in listdir(INPUT_DIR) if x.endswith('.tsv') and not x.startswith(OUT_PREFIX)]
msdf_list = []
for fn in TSVS:
    fp = join(INPUT_DIR, fn)
    print(f"Loading file:{fn} ")
    msdf = read_sssom_table(fp)
    msdf.df['confidence'] = 0.8
    msdf_list.append(msdf)
    out_fn = OUT_PREFIX+fn
    write_table(msdf,join(INPUT_DIR, out_fn))
