import numpy as np

## sigmoid function
def nonlin(x,deriv=False):
    if(deriv == True):
        return x*(1-x)
    return 1/(1+np.exp(-x))

## input data 
X = np.array([  [0,0,1],
                [0,1,1],
                [1,0,1],
                [1,1,1]])

## output dataset
Y = np.array([[0,1,1,0]]).T

## seed random numbers
np.random.seed(1)

## initialise random weights with mean 0
syn0 = 2*np.random.random((3,4)) - 1
syn1 = 2*np.random.random((4,1)) - 1

for i in range(100000):

    # forward propagation
    l0 = X
    l1 = nonlin(np.dot(l0,syn0))
    l2 = nonlin(np.dot(l1,syn1))

    if (i % 100000) == 0:
        print("l1,l2")
        print(l1,l2)

    # difference?
    l2_error = Y - l2

    if (i % 10000) == 0:
        print("Error:")
        print(str(np.mean(np.abs(l2_error))))

    # multiply difference by the slope of the sigmoid at l2
    l2_delta = l2_error * nonlin(l2,True)

    l1_error = l2_delta.dot(syn1.T)

    l1_delta = l1_error * nonlin(l1,True)

    # Update weights
    syn1 += l1.T.dot(l2_delta)
    syn0 += l0.T.dot(l1_delta)

print("Output after training")
print(l1)
print(l2)
print(l1.round())
