import sys
import sexp
import pprint
import translator

def Extend(Stmts,Productions):
    ret = []
    for i in range(len(Stmts)):
        if type(Stmts[i]) == list:
            TryExtend = Extend(Stmts[i],Productions)
            if len(TryExtend) > 0 :
                for extended in TryExtend:
                    ret.append(Stmts[0:i]+[extended]+Stmts[i+1:])
        elif type(Stmts[i]) == tuple:
            continue
        elif Stmts[i] in Productions:
            for extended in Productions[Stmts[i]]:
                #if extended[0] == '+' or extended[0] == '-':
                    #continue
                ret.append(Stmts[0:i]+[extended]+Stmts[i+1:])
        if len(ret) > 0:
            break
    return ret

def stripComments(bmFile):
    noComments = '(\n'
    for line in bmFile:
        line = line.split(';', 1)[0]
        noComments += line
    return noComments + '\n)'


if __name__ == '__main__':
    benchmarkFile = open(sys.argv[1])
    bm = stripComments(benchmarkFile)
    #print(bm)
    bmExpr = sexp.sexp.parseString(bm, parseAll=True).asList()[0] #Parse string to python list
    #pprint.pprint(bmExpr)
    checker=translator.ReadQuery(bmExpr)
    #print (checker.check('(define-fun f ((x Int)) Int (mod (* x 3) 10)  )'))
    #raw_input()
    SynFunExpr = []
    # My new add
    Constraints = []
    isLia = 1
    StartSym = 'My-Start-Symbol' #virtual starting symbol
    for expr in bmExpr:
        if len(expr)==0:
            continue
        elif expr[0]=='synth-fun':
            SynFunExpr=expr
        elif expr[0]=='constraint':
            Constraints.append(expr)
        elif expr[0]=='declare-var':
            if expr[2]=='Int':
                #examples.all_consts[expr[1]]=0
                pass
        elif expr[0]=='set-logic':
            if expr[1]=='BV':
                isLia = 0
    FuncDefine = ['define-fun']+SynFunExpr[1:4] #copy function signature
    FuncDefineStr = translator.toString(FuncDefine,ForceBracket = True) # use Force Bracket = True on function definition. MAGIC CODE. DO NOT MODIFY THE ARGUMENT ForceBracket = True.
    #print(FuncDefine)
    BfsQueue = [[StartSym]] #Top-down
    Productions = {StartSym:[]}
    Type = {StartSym:SynFunExpr[3]} # set starting symbol's return type
    for NonTerm in SynFunExpr[4]: #SynFunExpr[4] is the production rules
        NTName = NonTerm[0]
        NTType = NonTerm[1]
        if NTType == Type[StartSym]:
            Productions[StartSym].append(NTName)
        Type[NTName] = NTType
        Productions[NTName] = []
        for NT in NonTerm[2]:
            if type(NT) == tuple:
                Productions[NTName].append(str(NT[1]))
            else:
                Productions[NTName].append(NT)
    # My new add
    if isLia == 0:
        #temp = BVSolver.work(Constraints)
        #Ans = f"(define-fun f ((x (_ BitVec 64))) (_ BitVec 64) (bvor #x0000000000000001 x))"
        import BVsolver
        CurrStr = translator.toString(BVsolver.work(Constraints))
        Ans = FuncDefineStr[:-1]+' '+ CurrStr+FuncDefineStr[-1] # insert Program just before the last bracket ')'
        print(Ans)
        with open('result.txt', 'w') as f:
            f.write(Ans)
        exit()

    Count = 0
    TE_set = set()
    while(BfsQueue!= []):
        Curr = BfsQueue.pop(0)
        #print("extend", Curr)
        TryExtend = Extend(Curr,Productions)
        if(len(TryExtend)==0): # Nothing to
            #print(FuncDefine)
            # print("find", Curr)
            CurrStr = translator.toString(Curr)
            #SynFunResult = FuncDefine+Curr
            #Str = translator.toString(SynFunResult)
            Str = FuncDefineStr[:-1]+' '+ CurrStr+FuncDefineStr[-1] # insert Program just before the last bracket ')'
            Count += 1
            # print (Count)
            # print (Str)
            # if Count % 100 == 1:
                # print (Count)
                # print (Str)
                #raw_input()
            #print '1'
            counterexample = checker.check(Str)
            #print counterexample
            if(counterexample == None): # No counter-example
                Ans = Str
                break
            #print '2'
        #print(TryExtend)
        #raw_input()
        #BfsQueue+=TryExtend
 
        for TE in TryExtend:
            TE_str = str(TE)
            if not TE_str in TE_set:
                #BfsQueue.append(TE) if TE not in BfsQueue else BfsQueue
                BfsQueue.append(TE)
                TE_set.add(TE_str)

    print(Ans)
    with open('result.txt', 'w') as f:
        f.write(Ans)

	# Examples of counter-examples    
	# print (checker.check('(define-fun max2 ((x Int) (y Int)) Int 0)'))
    # print (checker.check('(define-fun max2 ((x Int) (y Int)) Int x)'))
    # print (checker.check('(define-fun max2 ((x Int) (y Int)) Int (+ x y))'))
    # print (checker.check('(define-fun max2 ((x Int) (y Int)) Int (ite (<= x y) y x))'))
