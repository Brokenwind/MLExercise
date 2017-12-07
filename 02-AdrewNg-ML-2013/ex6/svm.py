import sys
sys.path.append('..')
import numpy as np
import scipy.optimize as op

def linearKernel(x1,x2):
    """returns a linear kernel between x1 and x2
    """
    return sum(x1*x2)

def gaussianKernel(x1,x2,sigma=1.0):
    """returns a gaussian kernel between x1 and x2
    """
    dis = x1-x2
    return np.exp(- np.sum(dis * dis)/(2.0*sigma*sigma) )

def kernels(x,kernelFunc,**args):
    m,n = x.shape
    k = np.zeros((m,m))
    for i in range(0,m):
        for j in range(i,m):
            k[i,j] = kernelFunc(x[i],x[j],**args)
            k[j][i] = k[i,j]
    return k

def svmtrain(x, y, c, kernelFunc, args={},tol=1e-3, iters=5):
    """[model] = svmtrain(X, Y, C, kernelFunc, tol, iters)
    svmtrain trains an SVM classifier using a simplified version of the SMO algorithm. 
    PARAMETERS:
    X is the matrix of training examples.  Each row is a training example, and the jth column holds the  jth feature.
    Y is a column matrix containing 1 for positive examples and 0 for negative examples.
    C is the standard SVM regularization parameter.  
    tol is a tolerance value used for determining equality of floating point numbers. 
    iters controls the number of iterations over the dataset (without changes to alpha) before the algorithm quits.
    RETURN:
        model is the result parameters
    """
    m,n = x.shape
    # map 0 to -1
    y[y==0] = -1
    alphas = np.zeros(m)
    b = 0
    E = np.zeros(m)
    eta = 0
    L = 0
    H = 0
    iter = 0
    k = kernels(x,kernelFunc,**args)
    while iter < iters:
        changed = 0
        for i in range(0,m):
            E[i] = b + np.sum(alphas * y * k[i]) - y[i]
            dis = np.sum(y[i] * E[i])
            if ( dis < -tol and alphas[i] < c ) or ( dis > tol and alphas[i] > 0 ):
                j = np.floor(m*np.random.random())
                # make sure i is not equal to j
                while j == i:
                    j = np.floor(m*np.random.random())
                j = int(j)
                E[j] = b + sum(alphas * y * k[j]) - y[j]
                # save old alphas
                iold = alphas[i]
                jold = alphas[j]
                # compute L and H
                if  y[i] == y[j] :
                    L = max(0,alphas[i]+alphas[j]-c)
                    H = min(c,alphas[i]+alphas[j])
                else:
                    L = max(0,alphas[j]-alphas[i])
                    H = min(c,c+alphas[j]-alphas[i])
                if L == H:
                    continue
                eta = k[i,i] + k[j,j] - 2*k[i,j]
                if eta <= 0:
                    continue
                # compute and clip new value for alpha j
                alphas[j] = alphas[j] + (y[j] *(E[i] - E[j]))/eta
                # clip
                alphas[j] = min(H,alphas[j])
                alphas[j] = max(L,alphas[j])
                # check if change in alpha is significant
                if abs(alphas[j] - jold) < tol :
                    alphas[j] = jold
                    continue
                # determin value for alpha i 
                alphas[i] = alphas[i] + y[i]*y[j]*(jold - alphas[j])
                # compute b1 and b2
                b1 = b - E[i] - y[i] * (alphas[i] - iold) *  k[i,i]  - y[j] * (alphas[j] - jold) *  k[i,j]
                b2 = b - E[j] - y[i] * (alphas[i] - iold) *  k[i,j]  - y[j] * (alphas[j] - jold) *  k[j,j]
                # Compute b
                if 0 < alphas[i] and alphas[i] < c :
                    b = b1
                elif 0 < alphas[j] and alphas[j] < c :
                    b = b2
                else:
                    b = (b1+b2)/2
                changed += 1
                # end if
        # end for loop
        if changed == 0:
            iter += 1
        else:
            iter = 0
    # end of while
    sel = alphas > 0
    model = {}
    model['x'] = x[sel]
    model['y'] = y[sel]
    model['kernelFunc'] = kernelFunc
    model['b'] = b
    model['alphas'] = alphas[sel]
    model['w'] = (alphas * y).dot(x)
    return model

if __name__ == '__main__':
    x1 = np.array([1,2,1])
    x2 = np.array([0,4,-1])
    print gaussianKernel(x1,x2,2)
    print gaussianKernel(1,0)
    x1 = np.arange(1,13).reshape((4,3))
    print kernels(x1,gaussianKernel,sigma=4.0)
    print kernels(x1,linearKernel)
