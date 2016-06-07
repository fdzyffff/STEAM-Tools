import math
def Bias(no1,no2,e1,e2):
    t = 0
    bia = 0
    error = 0
    if no1 < no2:
        t=no1
        no1=no2
        no2=t
    if no1 > 0:
        bia = ((no1 - no2)/no1) * 100
        error = ((1/no1)**2) * (e2**2)
        error += ((no2/(no1*no1))**2) * (e1**2)
        error = math.sqrt(error)*100
    return bia, error

print Bias(98.81,117.57,0.09,1.02)
