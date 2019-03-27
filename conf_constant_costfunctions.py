def get_constant_costfunctions(dataset_name):
    if "bpic2017_refused" in dataset_name:
        a = 8
        b = 33
        c = 15
        d = 34
        e = 20
        f = 35
    elif "bpic2017_cancelled" in dataset_name:
        a = 10
        b = 35
        c = 13
        d = 32
        e = 18
        f = 40
    else:
        a = 3
        b = 5
        c = 2
        d = 5
        e = 3
        f = 4
    return a,b,c,d,e,f
