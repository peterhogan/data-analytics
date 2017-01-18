import numpy as np

## sigmoid function
def nonlin(x,deriv=False):
    if(deriv == True):
        return x*(1-x)
    return 1/(1+np.exp(-x))

## input data 
X = np.array([  [0,0,0.5],
                [0,0.6,0.1],
                [0.1,0.01,0.4],
                [1,0.78,1]     ])

## output dataset
Y = np.array([[0,0,1,1]]).T

## seed random numbers
np.random.seed(231012)

## initialise random weights with mean 0
syn0 = 2*np.random.random((3,1)) - 1

for i in range(100000):

    # forward propagation
    l0 = X
    l1 = nonlin(np.dot(l0,syn0))

    if i == 1:
        print(l1)
    elif i == (100000-1):
        print(l1)

    # difference?
    l1_error = Y - l1

    # multiply difference by the slope of the sigmoid at l1
    l1_delta = l1_error * nonlin(l1,True)

    # Update weights
    syn0 += np.dot(l0.T, l1_delta)

print("Output after training")
print(l1)
print(l1.round())
