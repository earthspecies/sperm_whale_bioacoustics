# AUTOGENERATED! DO NOT EDIT! File to edit: 02_Data_preparation.ipynb (unless otherwise specified).

__all__ = ['dominicana', 'etp', 'get_independent_vars', 'independent_vars_to_targs', 'drop_last_value', 'get_target',
           'get_clan_membership', 'merged_datasets', 'get_ETP_independent_vars', 'dblock_pretrain', 'datasets_pretrain',
           'mask', 'dominicana_clean', 'dominicana_clan', 'dblock_train', 'datasets_clan', 'get_coda_type',
           'dblock_train', 'datasets_coda']

# Cell
from fastai2.data.all import *

dominicana = pd.read_excel('data/Dominicana.xlsx')
etp = pd.read_excel('data/ETP.xlsx')

# Cell
def get_independent_vars(row, start_col=4, n_vals=9):
    vals = [v for v in row[start_col:(start_col+n_vals)].values if v != 0]
    # we want to manually pad the sequence
    # we believe that for a single direction RNN padding the sequence from the left should work better
    return np.pad(vals, (n_vals - len(vals), 0))

# Cell
def independent_vars_to_targs(ary): return ary[-1]

# Cell
def drop_last_value(ary): return ary[:-1]

# Cell
def get_target(row, col_name): return row[col_name]
get_clan_membership = partialler(get_target, col_name='Clan')

# Cell
pd.set_option('display.max_columns', None)
merged_datasets = pd.concat((etp, dominicana)).fillna(0)

# Cell
get_ETP_independent_vars = partial(get_independent_vars, start_col=5, n_vals=11)

# Cell
dblock_pretrain = DataBlock(
    get_x = (get_ETP_independent_vars, drop_last_value),
    get_y = (get_ETP_independent_vars, independent_vars_to_targs),
    splitter=TrainTestSplitter(test_size=0.1, random_state=42) # having a validation set is crucial for any task,
)                                                              # including pretraining!

datasets_pretrain = dblock_pretrain.datasets(merged_datasets)

# Cell
mask = dominicana.CodaType.isin(['1-NOISE', '2-NOISE','3-NOISE','4-NOISE','5-NOISE','6-NOISE','7-NOISE','8-NOISE','9-NOISE','10-NOISE','10i','10R'])
dominicana_clean = dominicana[~mask]

# Cell
dominicana_clan = pd.concat(
    (
        dominicana[dominicana.Clan == 'EC1'].sample(n=949),
        dominicana[dominicana.Clan == 'EC2']
    )
)

# Cell
dblock_train = DataBlock(
    get_x = get_independent_vars,
    get_y = (get_clan_membership, Categorize),
    splitter = TrainTestSplitter(test_size=0.1, random_state=42, stratify=dominicana_clan.Clan.factorize()[0])
)

datasets_clan = dblock_train.datasets(dominicana_clan)

# Cell
get_coda_type = partialler(get_target, col_name='CodaType')

dblock_train = DataBlock(
    get_x = get_independent_vars,
    get_y = (get_coda_type, Categorize),
    splitter = TrainTestSplitter(test_size=0.1, random_state=42, stratify=dominicana_clean.CodaType.factorize()[0])
)

datasets_coda = dblock_train.datasets(dominicana_clean)