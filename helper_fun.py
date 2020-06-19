import numpy as np
import copy

def shaking(ximli,pmj,yilij,k):
    J = len(pmj[0])
    I = len(ximli)
    ci = np.zeros(shape=(I,1))
    for i in range(I):
        ci[i] = len(ximli[i][0])
    
    new_ximli = copy.deepcopy(ximli)
    ###print("new_ximli",type(new_ximli),len(new_ximli),len(new_ximli[0]),len(new_ximli[0][0]))

    for kk in range(k):
        i = np.random.randint(I)
        li = np.random.randint(ci[i])

        y = np.asarray(yilij[int(li)])
        miscoverings_li = J - (pmj[0]@y.T+(1-pmj[0])@(1-y).T)
        ###print("covering", miscoverings_li)
        for m_ in range(len(ximli[i])): # find li's covering summary pile
            if ximli[i][m_][li]==1:
                m = m_
                break

        new_m=roulette(miscoverings_li,m)
        new_ximli[i][m][li]=0
        new_ximli[i][new_m][li]=1

    return new_ximli


def roulette(miscoverings,current_pile):
    K = len(miscoverings)
    m = 0
    if K == 1:
        return m

    summary_piles = list(range(K))
    ###print("cp",current_pile)
    miscoverings=list(miscoverings[:current_pile])+list(miscoverings[current_pile+1:])
    summary_piles=summary_piles[:current_pile]+summary_piles[current_pile+1:]
    total=sum(miscoverings)
    int_probs=total-miscoverings
    ac=np.zeros(K-1)
    ##print(len(miscoverings))
    if np.sum(int_probs)!=0:
        probs=int_probs/np.sum(int_probs)
        ac[0] = probs[0]
        for i in range(1,K-1):
            ac[i]=ac[i-1]+probs[i]
    else:
        probs = 1
        ac[0] = probs

    ###print(summary_piles,K-1)
    random_val=np.random.rand()
    for i in range(K-1):
        if ac[i]>=random_val:
            m=summary_piles[i]
            break
    return m

def local_search(ximli,pmj,yilij,weights):
    K,J = pmj[0].shape
    I=1
    ci=np.zeros(1)
    for i in range(I):
        ci[i] = len(yilij)

    ###print(ci)
    localBestPmj=copy.deepcopy(pmj)
    localBestZ=10**15

    no_change = False
    while no_change == False:
        # Computing best summary piles given ximli
        count_mj=np.zeros(shape=(K,J))
        covering_count_m=np.zeros(K)

        for m in range(K):
            for i in range(I):
                ###print(i,ci)
                for li in range(int(ci[i])):
                    if ximli[i][m][li] == 1:
                        covering_count_m[m] = covering_count_m[m]+weights[li]
                        for j in range(J):
                            if yilij[li][j] == 1:
                                count_mj[m][j] = count_mj[m][j] +weights[li]
        
        for m in range(K):
            for j in range(J):
                if covering_count_m[m] != 0:
                    count_mean = count_mj[m][j]/covering_count_m[m]
                    if count_mean >= 0.5:
                        pmj[0][m][j] = 1
                    else:
                        pmj[0][m][j] = 0
     # Rearranging piles according to cost (minimizing miscoverings)
        Z = 0
        y = np.asarray(yilij)
        #print(y.shape)
        mismatches = J - (pmj[0]@y.T+(1-pmj[0])@(1-y).T)
        ###print(mismatches.shape,ci[0])
        new_ximli =[np.zeros(shape = (K,int(ci[0])))]
        for li in range(int(ci[0])):
            val = min(mismatches[:,li])
            cid = int(np.argmin(mismatches[:,li]))
            Z = Z+val*weights[li]
            new_ximli[0][int(cid)][int(li)] = 1
        ###print(new_ximli[0])
        ###print(ximli[0])
        if new_ximli[0].all() == ximli[0].all():
            no_change = True
        else:
            ximli[0] = new_ximli[0]
        
        if Z<localBestZ:
            localBestZ=Z
            localBestPmj=copy.deepcopy(pmj)

    # If there's an empty summary pile then let it be equal to the pile of maximum ocurrence that it covers. Then, rearrange piles one more time
    for m in range(K):
        
        if sum(localBestPmj[0][m]) == 0:
            max_occurrence = 0
            for i in range(I):
                i_max_occurrence=i
            li_max_occurrence=np.random.randint(ci[i])
            for li in range(int(ci[i])):
                if ximli[i][m][li]==1 and weights[li]> max_occurrence:
                    max_occurrence =weights[li]
                    i_max_occurrence=i
                    li_max_occurrence=li

            localBestPmj[0][m]=yilij[li_max_occurrence]

    localBestXimli,localBestZ=get_cost(localBestPmj,yilij,weights)
    return localBestZ,localBestPmj,localBestXimli

def get_cost(pmj,yilij,weights):
    Z=0

    K,J=pmj[0].shape
    ###print(K,J)
    I=1
    ximli=[[]]

    for i in range(I):
        y = np.asarray(yilij)
        mismatches = J - (pmj[0]@y.T+(1-pmj[0])@(1-y).T)
        ci = len(yilij)
        ximli[0] = np.zeros(shape=(K,ci))
        ###print(ci,len(weights))
        for li in range(ci):
            val = min(mismatches[:,li])
            cid = int(np.argmin(mismatches[:,li]))
            Z = Z+val*weights[li]
            ##print(val,cid)
            ximli[0][int(cid)][int(li)] = 1

    return ximli,Z
        
def check_piles(pmj,yilij,ximli,weights,yilij_raw):
    text = ""
    raw = []
    ###print("1",len(yilij_raw))
    ###print('2',len(yilij_raw[0]))
    for i in range(len(yilij_raw)):
        y = list(yilij_raw[i])
        for li in range(len(y)):
            raw.append(y[li])
    
    K = len(pmj[0])
    for m in range(K):
        ci = len(yilij)
        equal_li=-1
        cover_sum=0
        for li in range(ci):
            if ximli[0][m][li] == 1:
                cover_sum=cover_sum+weights[li]
                if np.sum(pmj[0][m]- np.asarray(yilij[li])) == 0:
                    equal_li = li
        if equal_li != -1:
            for li in range(len(raw)):
                if yilij[li] == raw[li]:
                    break
            text = '%sSummary pile %d equals pile %d (appears %d times), and covers other %d piles (%d total).\n'%(text,m,equal_li,weights[equal_li],cover_sum-weights[equal_li],cover_sum)
        else:
            text = '%sSummary pile %d doesnt equal any pile, but covers %d piles.\n'%(text,m,cover_sum)
    return text

def rating(pmj,yilij,ximli,weights):
    K,J = pmj[0].shape
    I = 1
    ci = [0]
    ci[0] = len(yilij)

    count_mj = np.zeros(shape=(K,J))
    count_mj_neg = np.zeros(shape=(K,J))
    covering_count_m = np.zeros(K)

    for m in range(K):
        for i in range(I):
            for li in range(ci[i]):
                if ximli[0][m][li] == 1:
                    covering_count_m[m] = covering_count_m[m]+weights[li]
                    for j in range(J):
                        if yilij[li][j] == 1 and pmj[0][m][j] == 1:
                            count_mj[m][j]=count_mj[m][j]+weights[li]
                        if yilij[li][j] == 0 and pmj[0][m][j] == 0:
                            count_mj_neg[m][j]=count_mj_neg[m][j]+weights[li]
    
    truePos=np.zeros(shape=(K,J))
    trueNeg=np.zeros(shape=(K,J))
    covRate=np.zeros(K)

    for m in range(K):
        if covering_count_m[m] != 0:
            truePos[m] = count_mj[m]/covering_count_m[m]
            trueNeg[m] = count_mj_neg[m]/covering_count_m[m]
        
        covRate[m]=covering_count_m[m]/np.sum(covering_count_m)


    return truePos,trueNeg,covRate

    
    

