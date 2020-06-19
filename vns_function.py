import loadData
import pandas as pd
import numpy as np
import random
import helper_fun
import helper_OPPSP
import copy

def vns_function(filename,n,minK,maxK,runs,maxIterations,display_interval,random_seed,onePilePerSumPile):
    ok = True
    I = 1 
    # read file
    if filename[-3:] == "csv":
        ci,J,raw_data,weights,yilij = loadData.load_csv(filename,n)
    else:
        ci,J,raw_data,weights,yilij = loadData.load_xlsx(filename,n)

    print(yilij)
    

    # setting some results
    processed_data = {}
    processed_data['yilij'] = yilij
    processed_data['weights'] = weights
    print(weights)

    #If onePilePerSumPile==true then the minimum number of summary piles is 
    #the highest number of piles created by individuals
    if onePilePerSumPile == True:
        yilij = raw_data['yilij']
        I = len(yilij)
        ci = np.zeros(I)
        for i in range(I):
            ci[i] = len(yilij[i])
        
        val = max(ci)
        cid = np.argmax(ci)
        if val>minK:
            print(val,minK)
            ok = False
            processed_data=-1
            results=-1
            return

    # start the algorithm
    # Setting some results and configurations and initializing cells
    results = {}
    results['seed'] = np.zeros(shape=(maxK-minK+1,runs))
    
    for K in range(minK,maxK+1):
        for run in range(runs):
            results['seed'][K-minK][run] = random_seed + run + runs*(K-minK)

    results['minK'] = minK
    results['maxK'] = maxK
    results['runs'] = runs
    a = [0]*runs
    pmj_list = []
    for i in range(minK,maxK+1):
        pmj_list.append(a)
    results['pmj'] = copy.deepcopy(pmj_list)
    results['ximli'] = copy.deepcopy(pmj_list)
    results['Z'] = np.zeros(shape=(maxK-minK+1,runs))
    results['nIterations'] = np.zeros(shape=(maxK-minK+1,runs))
    results['truePos'] =copy.deepcopy(pmj_list)
    results['trueNeg'] = copy.deepcopy(pmj_list)
    results['covRate'] = copy.deepcopy(pmj_list)

    log_msg = ''
    k_max = 20

    #Starting algorithm for each number of summary piles and each replication
    for K in range(minK,maxK+1):
        for run in range(runs):
            random.seed(results['seed'][K-minK][run])
            print('%s\n--- K: %d - Run: %d ---\n\n'%(log_msg,K,run))
            #Start VNS settings ( not time limit here)
            stop_condition = False
            k = 1
            nIterations = 1

            #Initial solution: summary piles (pmj) and linking variables (ximli) are set to random
            pmj = [np.random.randint(1,3,(K,J))-1]
            
            bestPmj = copy.deepcopy(pmj)
            
            ximli = [[]]*I
            for i in range(I):
                if onePilePerSumPile == True:
                    ximli[i] = np.zeros(shape=(K,int(ci[i])))
                    perm = np.random.permutation(K)[:int(ci[i])]
                    for li in range(int(ci[i])):
                        ximli[i][perm[li]][li] = 1
                else:
                    ximli[i] = np.zeros(shape=(K,ci))
                    for li in range(ci):
                        ximli[i][np.random.randint(K)][li] = 1
            bestXimli = copy.deepcopy(ximli)

            bestZ = np.inf
            #print("ximli", ximli)

            #Shaking and local search
            #print(helper_fun.get_cost(bestPmj,yilij,weights)[1])
            while(stop_condition==False):
                if onePilePerSumPile == True:
                    ##to write
                    ximli = helper_OPPSP.shaking(bestXimli,bestPmj,yilij,k)
                    print("local")
                    Z, pmj, ximli = helper_OPPSP.local_search(ximli,pmj,yilij)
                else:
                    ximli=helper_fun.shaking(bestXimli,bestPmj,yilij,k)
                    #print(ximli)
                    Z,pmj,ximli = helper_fun.local_search(ximli,pmj,yilij,weights)
                    
                    
                #Updating best solution
                if Z < bestZ:
                    bestZ = Z
                    bestPmj = copy.deepcopy(pmj)
                    bestXimli = copy.deepcopy(ximli)
                    print("Iteration: %d - Best solution: %d.\n"%(nIterations,bestZ))
                    
                    k = 1
                else:
                    k = k%k_max+1

                if nIterations % display_interval == 0:
                    print("Iteration: %d - Best solution: %d.\n"%(nIterations,bestZ))

                nIterations = nIterations+1
                if nIterations >= maxIterations:
                    stop_condition = True

            #Check if the best solution cost is trully the cost of this solution
            #print(pmj,bestPmj)
            if onePilePerSumPile == True:
                _, Z = helper_OPPSP.get_cost(bestPmj,yilij)
            else:
                _, Z = helper_fun.get_cost(bestPmj, yilij, weights)
                #print("second Z", Z)

            if Z != bestZ:
                print("ERROR",Z,bestZ)

            #Check if summary piles are equal to any pile
            if onePilePerSumPile == True:
                #print("OPPSP")
                print("check piles")
                text = helper_OPPSP.check_piles(bestPmj,yilij,bestXimli)
                print(text)
            else:
                text = helper_fun.check_piles(bestPmj,yilij,bestXimli,weights,raw_data['yilij'])
                print(text)
            
            #Check some statistics and set results
            if onePilePerSumPile == True:
                #print("OPPSP")
                print("rating")
                truePos,trueNeg,covRate = helper_OPPSP.rating(bestPmj,yilij,bestXimli)
            else:
                truePos,trueNeg,covRate = helper_fun.rating(bestPmj,yilij,bestXimli,weights)
                
            
            
            results['pmj'][K-minK][run] = bestPmj[0]
            if onePilePerSumPile == True:
                results['ximli'][K-minK][run] = bestXimli
            else:
                results['ximli'][K-minK][run] = bestXimli[0]

            results['Z'][K-minK][run] = bestZ
            results['nIterations'] = nIterations-1
            results['truePos'][K-minK][run] = truePos
            
            results['trueNeg'][K-minK][run] = trueNeg 
            
            results['covRate'][K-minK][run] = covRate 
            
            #print(results)

    return results

# Run the function:
# vns_function(filename,n,minK,maxK,runs,maxIterations,display_interval,random_seed,onePilePerSumPile)
a = vns_function("test.csv", #filename
                 1, #n
                 10, #minK
                 10, #maxK
                 1, #runs 
                 1000, #maxIterations
                 100, #display_iterval
                 1000, #random seed
                 False) #one pile per summary pile