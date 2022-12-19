import pandas as pd


def parse_file(link, filetype):
    if filetype == 'xlsx':
        xd = pd.ExcelFile(link)
        df = xd.parse(xd.sheet_names[0], index_col=0, comment='#')
    else:
        df = pd.read_csv(link)
    pattern = r"_bot|-bot"
    drop_filter = df.str.contains(pattern)
    df = df[~drop_filter]
    emails_lst_ = df['emails'].tolist()
    return emails_lst_
