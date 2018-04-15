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
    #02 7/14
    #timeperiod = float(timeinfo[1].split(' ')[0][-2:]) - int(timeinfo[0].split(' ')[0][-2:])
    #====================
    predict_day_num = 0
    #====================
    flavorcount = int(input_lines[2])
    #====================        
    month_info = {
        '01': 31,
        '02': 28, # the year // 4 != 0
        '03': 31,
        '04': 30,
        '05': 31,
        '06': 30,
        '07': 31,
        '08': 31,
        '09': 30,
        '10': 31,
        '11': 30,
        '12': 31
    }
    future_time_range = input_lines[flavorcount + 6:flavorcount + 8]
    start_date = future_time_range[0].split(' ')[0].split('-')
    end_date = future_time_range[1].split(' ')[0].split('-')
    # same year, same month
    if start_date[0] == end_date[0] and start_date[1] == end_date[1]:
        predict_day_num = int(end_date[2]) - int(start_date[2])
    # same year , different month
    elif start_date[0] == end_date[0]:
        predict_day_num = int(end_date[2]) + int(month_info[start_date[1]]) - int(start_date[2])
        if start_date[0] == '2016' and start_date[1] == '02':
            predict_day_num += 1
    #different year and different month
    elif start_date[0] != end_date[0]:
        predict_day_num = 31 + int(end_date[2]) - int(start_date[2])
    
    timeperiod = float(predict_day_num)
    #print(timeperiod)

    #====================
    #03 CPU/MEM
    dimopti = input_lines[flavorcount + 4]

    #04 {'flavor1:[1,2]'}
    input_flavor = {}
    for flavor in input_lines[3:3+flavorcount]:
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
    
    h = getnh(data_label,input_flavor,timeperiod)
    
    f = [0 if i<0 else int(i) for i in h]
    print(f)
    pred_res = {}
    for i,flavorstr in enumerate(sorted(input_flavor.items())):
        pred_res[flavorstr[0]] = f[i]
    res = put(server_norms,input_flavor,dimopti,pred_res)
    result = res
    return result
def getnh(data_label,input_flavor,timeperiod):
    # /data/sample/3test
    true_mean = {'flavor1':4,
                 'flavor2':6,
                 'flavor4':3,
                 'flavor5':11,
                 'flavor6':6,
                 'flavor8':40,
                 'flavor11':11,
                 'flavor12':3,
                 'flavor14':28
                }

    
    true_mean = sorted(true_mean.items())
    true_mean = [i[1] for i in true_mean]
    print(true_mean)
    #================
    period_mean = defaultdict(list)
    
    for _ in range(0,len(data_label),1):
        #data_period = data_label[_*timeperiod:_*timeperiod+timeperiod]
        data_period = data_label[_:_+int(timeperiod)]
        data_period = [ i[1] for i in data_period]
        p = []
        for _i in data_period:
            p += _i
        for flavorstr in input_flavor.items():
            mean = p.count(flavorstr[0]) / timeperiod * 16.65 /(_+1)
            #if period_mean[flavorstr[0]]:
               #mean = period_mean[flavorstr[0]][-1]*0.0005 + 0.9995*mean
            period_mean[flavorstr[0]].append(mean)
    #=============
    pred_mean = {}
    pred_mean = sorted(period_mean.items())
    pred_mean = [i[1] for i in pred_mean ]
    #print(pred_mean[2])
    import math
    for _,i in enumerate(pred_mean):
        m = sum(i)/len(i)
        if m == 0.0:
           m = 0.01
        newbili = [k / m for k in i]
        
        toptwobili = newbili[0] / (newbili[1]+0.0001)
        
        for o,h in enumerate(newbili):
            if h > 25 and toptwobili > 3:
                pred_mean[_][o] /= 2
                break
            elif h < 10 and toptwobili > 3:
                pred_mean[_][o] *= 3
                break
            elif h < 0.01 :  
                pred_mean[_][o] *= 20
                
    pred_mean = [math.ceil(sum(i)/len(i)*timeperiod) for i in pred_mean]
    
    return pred_mean


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
            cout = 0
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