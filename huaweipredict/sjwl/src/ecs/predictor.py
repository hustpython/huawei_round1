from collections import defaultdict

def predict_vm(ecs_lines, input_lines):
    # Do your work from here#
    result = []
    if ecs_lines is None:
        print 'ecs information is none'
        return result

    if input_lines is None:
        print 'input file information is none'
        return result
    
    #========================Yzw 20180318=========
    #=====get inputinrfo
    #01 [56,128]
    server_norms = input_lines[0].split(' ')[:2]
    timeinfo = input_lines[-2:]
    #02 7/14
    timeperiod = int(timeinfo[1].split(' ')[0][-2:]) - int(timeinfo[0].split(' ')[0][-2:])
    #03 CPU/MEM
    dimopti = input_lines[-4]
    #04 {'flavor1:[1,2]'}
    input_flavor = {}
    for flavor in input_lines[3:-5]:
        if flavor:
           flavor = flavor.split(' ')
           input_flavor[flavor[0]] = [eval(i) for i in flavor[1:]]
    
    #=========================get esarray===============
    data_label = defaultdict(list)
    for everydat in ecs_lines:
        everydat = everydat.split('\t')
        daytime = str(everydat[-1].split(' ')[0])
        cloudserve =  everydat[1]
        data_label[daytime].append(cloudserve) 
    data_label = sorted(data_label.items(),reverse=True)
    if timeperiod == 7:
       h = get7h(data_label,input_flavor)
       f = [0 if i<0 else int(i * 7.0) for i in h]
    else:
       h = get7h(data_label,input_flavor)
       f = [0 if i<0 else int(i * 14.0) for i in h]
    print(f)
    pred_res = {}
    for i,flavorstr in enumerate(sorted(input_flavor.items())):
        pred_res[flavorstr[0]] = f[i]
    res = put(server_norms,input_flavor,dimopti,pred_res)
    result = res
    return result
def get7h(data_label,input_flavor):
    true_mean = {
                 'flavor2':4,
    
                 'flavor4':2,
                 
                 'flavor6':25,
                
                 'flavor8':31,
                 'flavor9':11,
                 
                }
    
    true_mean = sorted(true_mean.items())
    true_mean = [i[1] for i in true_mean]
    print(true_mean)
    period_mean = defaultdict(list)
    for _ in range(0,len(data_label)-7,2):
        #data_period = data_label[_*timeperiod:_*timeperiod+timeperiod]
        data_period = data_label[_:_+7]
        data_period = [ i[1] for i in data_period]
        p = []
        for _ in data_period:
            p += _
        for flavorstr in input_flavor.items():
            mean = p.count(flavorstr[0]) / 7.0
            period_mean[flavorstr[0]].append(mean)
    pred_mean = {}
    pred_mean = sorted(period_mean.items())
    pred_mean = [i[1] for i in pred_mean]
    w = [ 0  for _ in range(len(pred_mean[0]))]
    b = 0
    h = []
    a = [[0.02106140414717654, -0.21660572532393896, 0.26361827944192073, -0.05537504638583997, 0.17708221807366442, 0.5028694800242299, -0.6379272317290113, 0.1915969801461704, 0.17388751206562036, 0.051824204460593715], 0.1335085162239711]
    #a = gradientDescent(pred_mean[:15],true_mean[:15],w,b)
    for mean_s in pred_mean:
        h.append(sum([i * j for i,j in zip(mean_s,a[0])])+a[1])
    return h
#============
def get14h(data_label,input_flavor):
    true_mean = {'flavor1':1,
                 'flavor2':15,
                 'flavor3':4,
                 'flavor4':0,
                 'flavor5':5,
                 'flavor6':3,
                 'flavor7':13,
                 'flavor8':34,
                 'flavor9':23,
                 'flavor10':6,
                 'flavor11':9,
                 'flavor12':2,
                 'flavor13':7,
                 'flavor14':7,
                 'flavor15':2
                }
    
    true_mean = sorted(true_mean.items())
    true_mean = [i[1] for i in true_mean]
    print(true_mean)
    period_mean = defaultdict(list)
    for _ in range(0,len(data_label),6):
        #data_period = data_label[_*timeperiod:_*timeperiod+timeperiod]
        data_period = data_label[_:_+14]
        data_period = [ i[1] for i in data_period]
        p = []
        for _ in data_period:
            p += _
        for flavorstr in input_flavor.items():
            mean = p.count(flavorstr[0])
            period_mean[flavorstr[0]].append(mean)
    pred_mean = {}
    pred_mean = sorted(period_mean.items())
    pred_mean = [i[1] for i in pred_mean]
    w = [ 0  for _ in range(len(pred_mean[0]))]
    b = 0
    h = []
    a = [0.02106140414717654, -0.21660572532393896, 0.26361827944192073, -0.05537504638583997, 0.17708221807366442, 0.5028694800242299, -0.6379272317290113, 0.1915969801461704, 0.17388751206562036, 0.051824204460593715], 0.1335085162239711    #a = gradientDescent(pred_mean[:15],true_mean[:15],w,b)
    for mean_s in pred_mean:
        h.append(sum([i * j for i,j in zip(mean_s,a[0])])+a[1])
    return h

#============
def computerCost(x,y,w,b):
    m = len(x)
    J = 0
    h = []
    for mean_s in x:
        h.append(sum([i * j for i,j in zip(mean_s,w)])+b)
    J = sum([(hi - yi)**2 for hi,yi in zip(h,y)]) * 1.0 / (2 * m)
    return J

def gradientDescent(x,y,w,b,lr=0.001,num_iters = 40000):
    m = len(x)
    J_history = list(range(num_iters))
    for i in range(num_iters):
        h = []
        for mean_s in x:
            h.append(sum([i * j for i,j in zip(mean_s,w)])+b)
        for i in range(len(w)): 
            w[i] = w[i]- lr * (1.0/m)*sum([ii[i] * (hi - yi) for ii,hi,yi in zip(x,h,y)])
        b -= lr  * (1.0/m)*sum([(hi - yi) for hi,yi in zip(h,y) ])
        J_history[i] = computerCost(x,y,w,b)
    print(computerCost(x,y,w,b))
    print(len(w),w,b)
    return(w,b)
def put(server_norms,input_flavor,dimopti,pred_res):
    
    #server({'flavor':1})
    #norm['56', '128'], 'CPU\r\n'
    #server_norms
    #dimopti
    #input_flavor
    dimopti = dimopti.strip('\r\n')
    totalcpu = int(server_norms[0])
    totalmem = int(server_norms[1])
    #totalcpu = 3
    #totalmem = 8
    if dimopti == 'CPU':
       sorted_flavor = sorted(input_flavor.items(),reverse = True,key=lambda v:v[1][0] + (v[1][0]*1.0 / (v[1][1]/1024)))
    else:
       sorted_flavor = sorted(input_flavor.items(),reverse = True,key=lambda v:v[1][1] + (v[1][1]*1.0 / 1024 / (v[1][0])))
    need_put = []
    for x in sorted_flavor:
        num = pred_res[x[0]]
        for i in range(num):
            need_put.append(x[0])
    from copy import deepcopy
    copy_need_put = deepcopy(need_put)
    cpu_num = 0
    mem_num = 0
    put_res = []
    sin_res = []
    while need_put:
        for i in need_put:
            cpu_num  += input_flavor[i][0]
            mem_num  += input_flavor[i][1] // 1024
            if dimopti == 'CPU':
                if cpu_num <= totalcpu:
                    #print(cpu_num)
                    if mem_num <= totalmem:
                    #print(mem_num)
                        need_put.remove(i)
                        sin_res.append(i)
                    else:
                        continue
                else:
                    put_res.append(sin_res)
                    sin_res = []
                    cpu_num = 0
                    mem_num = 0
            else:
                if mem_num <= totalmem:
                    #print(cpu_num)
                    if cpu_num <= totalcpu:
                    #if mem_num <= totalmem:
                    #print(mem_num)
                        need_put.remove(i)
                        sin_res.append(i)
                    else:
                        continue
                else:
                    put_res.append(sin_res)
                    sin_res = []
                    cpu_num = 0
                    mem_num = 0
    if sin_res:
        put_res.append(sin_res) 

    vm_num = [(len(copy_need_put))]
    am = [ 0 for i in range(len(input_flavor))]
    for i ,j in enumerate(sorted(input_flavor.items())):
        countj = copy_need_put.count(j[0])
        am[i] = '%s %d'%(j[0],countj)
    server_num = [(len(put_res))]
    bm = []
    for i,_ in enumerate(put_res):
        sinstr = '%d'%(i+1)
        for j in sorted(input_flavor.items()):
            countd = _.count(j[0])
            if countd:
               kk = ' %s %d'%(j[0],countd)
               sinstr += kk
        bm.append(sinstr)
    result = []
    result.extend(vm_num)
    result.extend(am)
    result.extend(['\r'])
    result.extend(server_num)
    result.extend(bm)
    return result