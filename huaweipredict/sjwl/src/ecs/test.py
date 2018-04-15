from collections import defaultdict
#default define the all flavors into input_flavor
input_flavor = {'flavor1': [1, 4096],
                'flavor2': [1, 2048], 
                'flavor3': [1, 1024], 
                'flavor4': [2, 4096], 
                'flavor5': [2, 2048],
                'flavor6': [1, 4096],
                'flavor7': [1, 2048], 
                'flavor8': [1, 1024], 
                'flavor9': [2, 4096], 
                'flavor10': [2, 2048],
                'flavor11': [1, 4096],
                'flavor12': [1, 2048], 
                'flavor13': [1, 1024], 
                'flavor14': [2, 4096], 
                'flavor15': [2, 2048]
                }
array = []
longdata = defaultdict(list)
#split data into train and label
with open('data/jiaochayanzheng/long', 'r') as lines:
    for line in lines:
        array.append(line)
for everydat in array:
    everydat = everydat.split('\t')
    daytime = str(everydat[-1].split(' ')[0])
    cloudserve =  everydat[1]
    longdata[daytime].append(cloudserve) 
data = sorted(longdata.items(),reverse=True)
datacv = [[0,0] for i in range(12)]
for _,i in enumerate(range(0,120,10)):
    datacv[_][0] = data[i:i+35]
    datacv[_][1] = data[i+35:i+42]
datacv.remove(datacv[-1])

labellist = []
cvlist = []
for _,onedata in enumerate(datacv):
    #get label dict
    cvmean = defaultdict(list)
    labedic = {}

    label_period = [ i[1] for i in onedata[1]]
    p = []
    for _i in label_period:
        p += _i
    for flavorstr in input_flavor.items():
        labelmean = p.count(flavorstr[0]) / 7.0 
        labedic[flavorstr[0]] = labelmean
    labedic = sorted(labedic.items())
    labedic = [i[1] for i in labedic]
    #get cv data
    for _ in range(0,len(onedata[0])-7,2):
        data_period = onedata[0][_:_+7]
        data_period = [ i[1] for i in data_period]
        p = []
        for _i in data_period:
            p += _i
        for flavorstr in input_flavor.items():
            mean = p.count(flavorstr[0]) / 7.0 
            cvmean[flavorstr[0]].append(mean)
    cvmean = sorted(cvmean.items())
    cvmean = [i[1] for i in cvmean]
    labellist.append(labedic)
    cvlist.append(cvmean)
#get weight
def getweight():
    w = [ 0  for _ in range(10)]
    b = 0
    h = []
    a = gradientDescent(cvlist,labellist,w,b)
    '''for mean_s in cvlist:
        h.append(sum([i * j for i,j in zip(mean_s,a[0])])+a[1])
    return h'''
#computer the cv loss
def computerCost(x,y,w,b):
    m = len(x)
    J = 0
    h = []
    for mean_s in x:
        h.append(sum([i * j for i,j in zip(mean_s,w)])+b)
    J = sum([(hi - yi)**2 for hi,yi in zip(h,y)]) * 1.0 / (2 * m)
    return J

#use the gradientDescent method to optimize the loss function
def gradientDescent(x_iter,y_iter,w,b,lr=0.0001,num_iters = 30000):
    m = len(x_iter[0])
    J_history = list(range(num_iters))
    for i in range(num_iters):
        for x,y in zip(x_iter,y_iter):
            h = []
            for mean_s in x:
                h.append(sum([i * j for i,j in zip(mean_s,w)])+b)
            for i in range(len(w)): 

                w[i] = w[i]- lr * (1.0/m)*sum([ii[i] * (hi - yi) for ii,hi,yi in zip(x,h,y)])
            b -= lr  * (1.0/m)*sum([(hi - yi) for hi,yi in zip(h,y) ])
            J_history[i] += computerCost(x,y,w,b)
            c = computerCost(x,y,w,b)
            if c > 1:
                print(c)
    print(len(w),w,b)
    return(w,b)
res = getweight()