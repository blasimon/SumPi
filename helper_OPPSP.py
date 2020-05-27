import numpy as np

def shaking(ximli,pmj,yilij,k):
    K,J = pmj[0].shape
    I = len(ximli)
    ci = np.zeros(shape=(I,1))
    for i in range(I):
        ci[i] = len(ximli[i][0])

    new_ximli = ximli

    for kk in range(k):
        i = np.random.randint(I)
        while K <= ci[i]:
            i = np.random.randint(I)

        li = np.random.randint(ci[i])

        y = np.asarray(yilij[int(li)])
        print("y",y.shape)
        print("pmj",pmj[0].shape)
        miscoverings_li = J - (pmj[0]@y.T+(1-pmj[0])@(1-y).T)

        for m_ in range(len(ximli[i])): # find li's covering summary pile
            if ximli[i][m_][li]==1:
                m = m_
                break
        
        candidates = np.zeros(int(K))
        c = 0
        for mm in range(K):
            if sum(ximli[i][mm]) == 0:
                candidates[c] = mm
                c = c+1

        new_m = roulette(miscoverings_li,candidates)
        new_ximli[i][m][li]=0
        new_ximli[i][new_m][li]=1
    return new_ximli



def roulette(miscoverings,candidates):
    K = len(miscoverings)
    m = 0
    if K == 1:
        return m
    candidates = candidates.astype(int)
    #print("miscoverings",miscoverings)
    miscoverings = miscoverings[candidates]
    total= np.sum(miscoverings)
    int_probs=total-miscoverings

    
    ac = np.zeros(len(candidates))
    #print("miscoverings",miscoverings,len(ac))
    #print("int_probs",int_probs)
    if np.sum(int_probs) != 0:
        probs=int_probs/np.sum(int_probs)
        print(np.sum(int_probs),probs)
        if len(probs.shape)>1:
            ac[0] = probs[0][0]
            for i in range(1,len(candidates)):
                ac[i] = ac[i-1]+probs[i][0]
        else:
            ac[0] = probs[0]
            for i in range(1,len(candidates)):
                ac[i] = ac[i-1]+probs[i]
    else:
        probs = 1
        ac[0] = 1 

    random_val=np.random.rand()
    for i in range(len(candidates)):
        if ac[i]>=random_val:
            m=candidates[i]
            break
    return m

def local_search(ximli,pmj,yilij):
    K,J = pmj[0].shape
    I=len(yilij)
    ci=np.zeros(I)
    for i in range(I):
        ci[i] = len(yilij[i])

    localBestPmj=pmj
    localBestZ=10**15

    no_change = False
    while no_change == False:
        count_mj=np.zeros(shape=(K,J))
        covering_count_m=np.zeros(shape=(K,1))

        for m in range(K):
            for i in range(I):
                for li in range(int(ci[i])):
                    if ximli[i][m][li]==1:
                        covering_count_m[m]=covering_count_m[m]+1
                        for j in range(J):
                            if yilij[i][li][j] == 1:
                                count_mj[m][j] = count_mj[m][j] + 1

        for m in range(K):
            for j in range(J):
                if covering_count_m[m] != 0:
                    count_mean = count_mj[m][j]/covering_count_m[m]
                    if count_mean >= 0.5:
                        pmj[0][m][j] = 1
                    else:
                        pmj[0][m][j] = 0 

        new_ximli = [0]*I
        Z = 0

        for i in range(I):

            y = np.asarray(yilij[i])
            mismatches = J - (pmj[0]@y.T+(1-pmj[0])@(1-y).T)
            new_ximli[i] = np.zeros(shape = (K,int(ci[i])))
            visited_yilij = np.zeros(int(ci[i]))
            visited_pmj = np.zeros(K)
            
            mismatches_row = np.zeros(shape=(int(ci[i]*K),3)) #every row means: [cost to assign li to m, li, m]

            for li in range(int(ci[i])):
                for m in range(K):
                    #print(mismatches.shape,m,li)
                    mismatches_row[m+K*li] = np.array([mismatches[m][li],li,m])

            perm = np.argsort(mismatches_row[:,0])
            mismatches_row = mismatches_row[perm].astype(int)
            ii = 0

            while np.sum(visited_yilij) < ci[i]:
                print("visited",visited_yilij,ci[i])
                if visited_yilij[mismatches_row[ii][1]] == 0 and visited_pmj[mismatches_row[ii][2]] == 0:
                    visited_pmj[mismatches_row[ii][2]] = 1
                    visited_yilij[mismatches_row[ii][1]] = 1
                    Z = Z + mismatches_row[ii][0]
                    new_ximli[i][mismatches_row[ii][2]][mismatches_row[ii][1]] = 1
                
                ii = ii+1
        print("For end")
        no_change = True
        for i in range(I):
            if new_ximli[i].all() != ximli[i].all():
                no_change = False
                ximli = new_ximli
        print("no_change:",no_change)
        if Z < localBestZ:
            localBestZ = Z
            localBestPmj = pmj
    
    for m in range(K):
        if np.sum(localBestPmj[0][m]) == 0:
            s = np.zeros(J)
            for i in range(I):
                for li in range(int(ci[i])):
                    if ximli[i][m][li] == 1:
                        for j in range(J):
                            s[j] = s[j] + yilij[i][li][j]
            
            j = np.argmax(s)
            localBestPmj[0][m][j] = 1

    print("another for end")
    localBestXimli, localBestZ = get_cost(localBestPmj,yilij)
            
    return localBestZ,localBestPmj,localBestXimli


def get_cost(pmj,yilij):
    Z = 0
    K,J = pmj[0].shape
    I = len(yilij)
    ci = np.zeros(I)

    for i in range(I):
        ci[i] = len(yilij[i])
    
    ximli = [0]*I

    for i in range(I):
        y = np.asarray(yilij[i])
        mismatches = J - (pmj[0]@y.T+(1-pmj[0])@(1-y).T)

        ximli[i] = np.zeros(shape=(K,int(ci[i])))

        visited_yilij = np.zeros(int(ci[i]))
        visited_pmj = np.zeros(K)

        mismatches_row = np.zeros(shape=(int(ci[i]*K),3)) #every row means: [cost to assign li to m, li, m]

        for li in range(int(ci[i])):
            for m in range(K):
                mismatches_row[m+K*li] = np.array([mismatches[m][li],li,m])

        perm = np.argsort(mismatches_row[:,0])
        mismatches_row = mismatches_row[perm]
        ii = 0
        while np.sum(visited_yilij) < ci[i]:
            if visited_yilij[int(mismatches_row[ii][1])] == 0 and visited_pmj[int(mismatches_row[ii][2])] == 0:
                visited_pmj[int(mismatches_row[ii][2])] = 1
                visited_yilij[int(mismatches_row[ii][1])] = 1
                Z = Z + mismatches_row[ii][0]
                ximli[i][int(mismatches_row[ii][2])][int(mismatches_row[ii][1])] = 1
            
            ii = ii+1

    return ximli, Z

def check_piles(pmj,yilij,ximli):
    text = ''
    K = len(pmj[0])
    I = len(yilij)
    ci = np.zeros(I)
    for i in range(I):
        ci[i] = len(yilij[i])
    
    for m in range(K):
        cover_sum = 0
        equal_li = 0
        equal_i = 0

        for i in range(I):
            for li in range(int(ci[i])):
                if ximli[i][m][li] == 1:
                    cover_sum=cover_sum+1
                    if equal_li == 0:
                        if pmj[0][m].all() == np.asarray(yilij[i][li]).all():
                            equal_li = li
                            equal_i = i

        if equal_li != 0:
            text = '%sSummary pile %d equals pile %d of individual %d, and covers a sum of %d piles.\n'%(text,m,equal_li,equal_i,cover_sum)
        else:
            text = '%sSummary pile %d doesnt equal any pile, but covers %d piles.\n'%(text,m,cover_sum)

    return text

def rating(pmj,yilij,ximli):
    K,J = pmj[0].shape
    I = len(yilij)
    ci = np.zeros(I)

    for i in range(I):
        ci[i] = len(yilij[0])

    count_mj = np.zeros(shape=(K,J))
    count_mj_neg = np.zeros(shape=(K,J))
    covering_count = np.zeros(K)

    for m in range(K):
        for i in range(I):
            for li in range(int(ci[i])):
                if ximli[i][m][li] == 1:
                    covering_count[m] = covering_count[m]+1
                    for j in range(J):
                        if yilij[i][li][j] == 1 and pmj[0][m][j] == 1:
                            count_mj[m][j] = count_mj[m][j]+1

                        if yilij[i][li][j] == 0 and pmj[0][m][j] == 0:
                            count_mj_neg[m][j] = count_mj_neg[m][j]+1

    truePos = np.zeros(shape=(K,J))
    trueNeg = np.zeros(shape=(K,J))
    covRate = np.zeros(K)

    for m in range(K):
        if covering_count[m] != 0:
            truePos[m] = count_mj[m]/covering_count[m]
            trueNeg[m] = count_mj_neg[m]/covering_count[m]
        else:
            truePos[m] = np.zeros(J)
            trueNeg[m] = np.zeros(J)

        covRate[m] = covering_count[m]/sum(covering_count)

    return truePos,trueNeg,covRate

