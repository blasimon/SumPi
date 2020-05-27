import pandas as pd

# This function reads a .csv file. 'n' is the minimum number of piles repetitions to be considered. 
# It removes piles with less than 'n' repetitions.

def load_csv(filepath, n):
    raw_data = {}

    df = pd.read_csv(filepath)
    raw = df
    products = df.columns[5:]
    IDs = df.Uniqid.unique()
    categories = []
    for i in IDs:
        categories.append(df[df['Uniqid']==i].shape[0])

    raw_data['products'] = products
    raw_data['IDs'] = IDs
    raw_data['categories'] = categories
    raw_data['raw'] = raw

    val = df.select_dtypes(include='number')
    matrix = list(val.iloc[:,2:-1].values)

    for i in range(len(matrix)):
        matrix[i] = tuple(matrix[i])


    raw_weights = []
    raw_yilij = []
    for i in range(len(matrix)):
        row = matrix[i]
        if row in raw_yilij:
            continue
        else:
            raw_yilij.append(row)
            raw_weights.append(matrix.count(row))

    yilij=[]
    weights=[]

    for i in range(len(raw_weights)):
        if raw_weights[i] >= n:
            yilij.append(raw_yilij[i])
            weights.append(raw_weights[i])
    
    new_ids = []
    categories = []
    id_yilij = []
    for i in IDs:
        tmp = df[df['Uniqid']==i].select_dtypes(include='number').iloc[:,2:-1].values
        count = 0
        tmp_y = []
        for r in tmp:
            row = tuple(r)
            if row in yilij:
                tmp_y.append(row)
                count = count + 1
        if count > 0:
            new_ids.append(i)
            categories.append(count)
            id_yilij.append(tmp_y)

    raw_data['IDs'] = new_ids
    raw_data['categories'] = categories
    raw_data['yilij'] = id_yilij
    ci = len(yilij)
    return ci,len(yilij[0]),raw_data,weights,yilij


def load_xlsx(filepath, n):
    raw_data = {}

    df = pd.read_excel(filepath, index_col=None)
    raw = df
    products = df.columns[5:]
    IDs = df.Uniqid.unique()
    categories = []
    for i in IDs:
        categories.append(df[df['Uniqid']==i].shape[0])

    raw_data['products'] = products
    raw_data['IDs'] = IDs
    raw_data['categories'] = categories
    raw_data['raw'] = raw

    val = df.select_dtypes(include='number')
    matrix = list(val.iloc[:,2:-1].values)

    for i in range(len(matrix)):
        matrix[i] = tuple(matrix[i])


    raw_weights = []
    raw_yilij = []
    for i in range(len(matrix)):
        row = matrix[i]
        if row in raw_yilij:
            continue
        else:
            raw_yilij.append(row)
            raw_weights.append(matrix.count(row))

    yilij=[]
    weights=[]

    for i in range(len(raw_weights)):
        if raw_weights[i] >= n:
            yilij.append(raw_yilij[i])
            weights.append(raw_weights[i])
    
    new_ids = []
    categories = []
    id_yilij = []
    for i in IDs:
        tmp = df[df['Uniqid']==i].select_dtypes(include='number').iloc[:,2:-1].values
        count = 0
        tmp_y = []
        for r in tmp:
            row = tuple(r)
            if row in yilij:
                tmp_y.append(row)
                count = count + 1
        if count > 0:
            new_ids.append(i)
            categories.append(count)
            id_yilij.append(tmp_y)

    raw_data['IDs'] = new_ids
    raw_data['categories'] = categories
    raw_data['yilij'] = id_yilij
    ci = len(yilij)
    return ci,len(yilij[0]),raw_data,weights,yilij

