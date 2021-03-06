import numpy as np
import pickle
from scipy.io import loadmat
from scipy.optimize import minimize
import time
from sklearn.svm import SVC


def preprocess():
    """ 
     Input:
     Although this function doesn't have any input, you are required to load
     the MNIST data set from file 'mnist_all.mat'.

     Output:
     train_data: matrix of training set. Each row of train_data contains 
       feature vector of a image
     train_label: vector of label corresponding to each image in the training
       set
     validation_data: matrix of training set. Each row of validation_data 
       contains feature vector of a image
     validation_label: vector of label corresponding to each image in the 
       training set
     test_data: matrix of training set. Each row of test_data contains 
       feature vector of a image
     test_label: vector of label corresponding to each image in the testing
       set
    """

    mat = loadmat('mnist_all.mat')  # loads the MAT object as a Dictionary

    n_feature = mat.get("train1").shape[1]
    n_sample = 0
    for i in range(10):
        n_sample = n_sample + mat.get("train" + str(i)).shape[0]
    n_validation = 1000
    n_train = n_sample - 10 * n_validation

    # Construct validation data
    validation_data = np.zeros((10 * n_validation, n_feature))
    for i in range(10):
        validation_data[i * n_validation:(i + 1) * n_validation, :] = mat.get("train" + str(i))[0:n_validation, :]

    # Construct validation label
    validation_label = np.ones((10 * n_validation, 1))
    for i in range(10):
        validation_label[i * n_validation:(i + 1) * n_validation, :] = i * np.ones((n_validation, 1))

    # Construct training data and label
    train_data = np.zeros((n_train, n_feature))
    train_label = np.zeros((n_train, 1))
    temp = 0
    for i in range(10):
        size_i = mat.get("train" + str(i)).shape[0]
        train_data[temp:temp + size_i - n_validation, :] = mat.get("train" + str(i))[n_validation:size_i, :]
        train_label[temp:temp + size_i - n_validation, :] = i * np.ones((size_i - n_validation, 1))
        temp = temp + size_i - n_validation

    # Construct test data and label
    n_test = 0
    for i in range(10):
        n_test = n_test + mat.get("test" + str(i)).shape[0]
    test_data = np.zeros((n_test, n_feature))
    test_label = np.zeros((n_test, 1))
    temp = 0
    for i in range(10):
        size_i = mat.get("test" + str(i)).shape[0]
        test_data[temp:temp + size_i, :] = mat.get("test" + str(i))
        test_label[temp:temp + size_i, :] = i * np.ones((size_i, 1))
        temp = temp + size_i

    # Delete features which don't provide any useful information for classifiers
    sigma = np.std(train_data, axis=0)
    index = np.array([])
    for i in range(n_feature):
        if (sigma[i] > 0.001):
            index = np.append(index, [i])
    train_data = train_data[:, index.astype(int)]
    validation_data = validation_data[:, index.astype(int)]
    test_data = test_data[:, index.astype(int)]

    # Scale data to 0 and 1
    train_data /= 255.0
    validation_data /= 255.0
    test_data /= 255.0

    return train_data, train_label, validation_data, validation_label, test_data, test_label


def sigmoid(z):
    return 1.0 / (1.0 + np.exp(-z))


def blrObjFunction(initialWeights, *args):
    """
    blrObjFunction computes 2-class Logistic Regression error function and
    its gradient.

    Input:
        initialWeights: the weight vector (w_k) of size (D + 1) x 1 
        train_data: the data matrix of size N x D
        labeli: the label vector (y_k) of size N x 1 where each entry can be either 0 or 1 representing the label of corresponding feature vector

    Output: 
        error: the scalar value of error function of 2-class logistic regression
        error_grad: the vector of size (D+1) x 1 representing the gradient of
                    error function
    """
    train_data, labeli = args

    n_data = train_data.shape[0]
    n_features = train_data.shape[1]
    error = 0
    error_grad = np.zeros((n_features + 1, 1))
    
    ##################
    # YOUR CODE HERE #
    ##################
    # HINT: Do not forget to add the bias term to your input data

    #error_grad
    run_sum = np.zeros((n_features + 1, 1))
    for i in range(0,n_data):
        x_bias = np.hstack((1,train_data[i]))
        
        theta = sigmoid(np.dot(initialWeights,x_bias))
        
        error_i = np.multiply((theta - labeli[i][0]),np.transpose(x_bias))
        error_i = error_i.reshape(error_i.shape[0],1)
        run_sum = np.add(run_sum,error_i)
    error_grad = run_sum/n_data
    error_grad =np.squeeze(np.asarray(error_grad))
    
    # Error
    for n in range(0,n_data):
        appended_data = np.hstack((1, train_data[n]));
        theta_n = sigmoid(np.dot(initialWeights,appended_data))
        first_part = labeli[n] * np.log(theta_n)
        second_part = (1 - labeli[n]) * np.log(1 - theta_n)
        error += (first_part + second_part)
        
    error /= -1 * n_data
    
    return error, error_grad


def blrPredict(W, data):
    """
     blrObjFunction predicts the label of data given the data and parameter W 
     of Logistic Regression
     
     Input:
         W: the matrix of weight of size (D + 1) x 10. Each column is the weight 
         vector of a Logistic Regression classifier.
         data: the data matrix of size N x D
         
     Output: 
         label: vector of size N x 1 representing the predicted label of 
         corresponding feature vector given in data matrix

    """
    label = np.zeros((data.shape[0], 1))

    ##################
    # YOUR CODE HERE #
    ##################
    # HINT: Do not forget to add the bias term to your input data
    
    for i in range(0, data.shape[0]):
        
        x_bias = np.hstack((1, data[i]))
        for j in range(0, W.shape[1]):
            c1 = sigmoid(np.dot(W[:,j], x_bias))
            c2 = 1 - c1
            y = 0
            if c1 > c2:
                y = j
                label[i] = y
                break;
            else:
                y = 0

    return label


def mlrObjFunction(params, *args):
    initialWeights_b = params
    train_data, labeli = args
    
    """
    mlrObjFunction computes multi-class Logistic Regression error function and
    its gradient.

    Input:
        initialWeights: the weight vector of size (D + 1) x 1
        train_data: the data matrix of size N x D
        labeli: the label vector of size N x 1 where each entry can be either 0 or 1
                representing the label of corresponding feature vector

    Output:
        error: the scalar value of error function of multi-class logistic regression
        error_grad: the vector of size (D+1) x 10 representing the gradient of
                    error function
    """
    n_data = train_data.shape[0]
    n_feature = train_data.shape[1]
    error = 0
    error_grad = np.zeros((n_feature + 1, n_class))
    

    ##################
    # YOUR CODE HERE #
    ##################
    # HINT: Do not forget to add the bias term to your input data
    #Error Grad
    initialWeights_b = initialWeights_b.reshape((n_feature + 1, n_class))
    for k in range(0,n_class):
        run_sum = np.zeros((1,n_feature + 1))
        for i in range(0, n_data):
            x_bias = np.hstack((1,train_data[i,:]))
            
            wk = initialWeights_b[:,k]
            
            
            theta = sigmoid(np.dot(np.transpose(wk),x_bias))
            
            run_sum = np.add(run_sum,np.multiply((theta -labeli[i][k]),x_bias))
          
        error_grad[:,k] = run_sum
            
        
    
    
    
    #Error
    trans_weights = np.transpose(initialWeights_b)
    for n in range(0, n_data):
        x_bias = np.hstack((1, train_data[n]))
        for k in range(0, n_class):
            error += labeli[n][k] * np.log(sigmoid(np.dot(trans_weights[k], x_bias)))
            
    error *= -1
    
    error_grad = np.ravel(error_grad)
    
    return error, error_grad


def mlrPredict(W, data):
    """
     mlrObjFunction predicts the label of data given the data and parameter W
     of Logistic Regression

     Input:
         W: the matrix of weight of size (D + 1) x 10. Each column is the weight
         vector of a Logistic Regression classifier.
         data: the data matrix of size N x D

     Output:
         label: vector of size N x 1 representing the predicted label of
         corresponding feature vector given in data matrix

    """
    label = np.zeros((data.shape[0], 1))

    ##################
    # YOUR CODE HERE #
    ##################
    # HINT: Do not forget to add the bias term to your input data

    for n in range(0, data.shape[0]):
        x_bias = np.hstack((1, data[n]))
        max_val = -1
        max_index = 0
        for k in range(0, 10):
            num = np.exp(np.dot(W[:,k], x_bias))
            if num > max_val:
                max_val = num
                max_index = k
        label[n] = max_index
            

    return label


"""
Script for Logistic Regression
"""




train_data, train_label, validation_data, validation_label, test_data, test_label = preprocess()

# number of classes
n_class = 10

# number of training samples
n_train = train_data.shape[0]

# number of features
n_feature = train_data.shape[1]

Y = np.zeros((n_train, n_class))
for i in range(n_class):
    Y[:, i] = (train_label == i).astype(int).ravel()

# Logistic Regression with Gradient Descent
print("Logistic Regression with Gradient Descent")
W = np.zeros((n_feature + 1, n_class))
initialWeights = np.zeros((n_feature + 1, 1))

start_time = time.time()
opts = {'maxiter': 100}
for i in range(n_class):
    labeli = Y[:, i].reshape(n_train, 1)
    args = (train_data, labeli)
    nn_params = minimize(blrObjFunction, initialWeights, jac=True, args=args, method='CG', options=opts)
    W[:, i] = nn_params.x.reshape((n_feature + 1,))

pickle.dump( W, open( "params.pickle", "wb" ) )

# Find the accuracy on Training Dataset
predicted_label = blrPredict(W, train_data)
print('\n Training set Accuracy:' + str(100 * np.mean((predicted_label == train_label).astype(float))) + '%')

# Find the accuracy on Validation Dataset
predicted_label = blrPredict(W, validation_data)
print('\n Validation set Accuracy:' + str(100 * np.mean((predicted_label == validation_label).astype(float))) + '%')

# Find the accuracy on Testing Dataset
predicted_label = blrPredict(W, test_data)
print('\n Testing set Accuracy:' + str(100 * np.mean((predicted_label == test_label).astype(float))) + '%')
print('\n Blr time:' + str(time.time()- start_time))

"""
Script for Support Vector Machine
"""

print('\n\n--------------SVM-------------------\n\n')
#Linear Kernel Segment#
X = train_data #reducing elements in here to run faster, CHANGE THIS
y = train_label#change this
y = np.ravel(y)
clf = SVC(C=1.0, cache_size=200, class_weight=None, coef0=0.0,
    decision_function_shape='ovr', degree=3, gamma='auto', kernel='linear',
    max_iter=-1, probability=False, random_state=None, shrinking=True,
    tol=0.001, verbose=True)
clf.fit(X, y)
predictions=clf.predict(X)
Correct=0
Total=predictions.size
for i in range (0,predictions.size):
    if(predictions[i] == y[i]):
        Correct = Correct + 1

Accuracy=(Correct/Total)*100
print("Accuracy: ",Accuracy,"%")
X = test_data #reducing elements in here to run faster, CHANGE THIS
y = test_label#change this
y = np.ravel(y)
clf = SVC(C=1.0, cache_size=200, class_weight=None, coef0=0.0,
    decision_function_shape='ovr', degree=3, gamma='auto', kernel='linear',
    max_iter=-1, probability=False, random_state=None, shrinking=True,
    tol=0.001, verbose=True)
clf.fit(X, y)
predictions=clf.predict(X)
Correct=0
Total=predictions.size
for i in range (0,predictions.size):
    if(predictions[i] == y[i]):
        Correct = Correct + 1

Accuracy=(Correct/Total)*100
print("Accuracy: ",Accuracy,"%")
X = validation_data #reducing elements in here to run faster, CHANGE THIS
y = validation_label#change this
y = np.ravel(y)
clf = SVC(C=1.0, cache_size=200, class_weight=None, coef0=0.0,
    decision_function_shape='ovr', degree=3, gamma='auto', kernel='linear',
    max_iter=-1, probability=False, random_state=None, shrinking=True,
    tol=0.001, verbose=True)
clf.fit(X, y)
predictions=clf.predict(X)
Correct=0
Total=predictions.size
for i in range (0,predictions.size):
    if(predictions[i] == y[i]):
        Correct = Correct + 1

Accuracy=(Correct/Total)*100
print("Accuracy: ",Accuracy,"%")

#Radial Bias segment with Gamma set to .1#
X = train_data #reducing elements in here to run faster, CHANGE THIS
y = train_label#change this
y = np.ravel(y)
clf = SVC(C=1.0, cache_size=200, class_weight=None, coef0=0.0,
    decision_function_shape='ovr', degree=3, gamma=.1, kernel='rbf',
    max_iter=-1, probability=False, random_state=None, shrinking=True,
    tol=0.001, verbose=True)
clf.fit(X, y)
predictions=clf.predict(X)
Correct=0
Total=predictions.size
for i in range (0,predictions.size):
    if(predictions[i] == y[i]):
        Correct = Correct + 1

Accuracy=(Correct/Total)*100
print("Accuracy: ",Accuracy,"%")
X = test_data #reducing elements in here to run faster, CHANGE THIS
y = test_label#change this
y = np.ravel(y)
clf = SVC(C=1.0, cache_size=200, class_weight=None, coef0=0.0,
    decision_function_shape='ovr', degree=3, gamma=.1, kernel='rbf',
    max_iter=-1, probability=False, random_state=None, shrinking=True,
    tol=0.001, verbose=True)
clf.fit(X, y)
predictions=clf.predict(X)
Correct=0
Total=predictions.size
for i in range (0,predictions.size):
    if(predictions[i] == y[i]):
        Correct = Correct + 1

Accuracy=(Correct/Total)*100
print("Accuracy: ",Accuracy,"%")
X = validation_data #reducing elements in here to run faster, CHANGE THIS
y = validation_label#change this
y = np.ravel(y)
clf = SVC(C=1.0, cache_size=200, class_weight=None, coef0=0.0,
    decision_function_shape='ovr', degree=3, gamma=.1, kernel='rbf',
    max_iter=-1, probability=False, random_state=None, shrinking=True,
    tol=0.001, verbose=True)
clf.fit(X, y)
predictions=clf.predict(X)
Correct=0
Total=predictions.size
for i in range (0,predictions.size):
    if(predictions[i] == y[i]):
        Correct = Correct + 1

Accuracy=(Correct/Total)*100
print("Accuracy: ",Accuracy,"%")
#-------------------------------------#

#Radial Bias Segment with default gamma value#
X = train_data #reducing elements in here to run faster, CHANGE THIS
y = train_label#change this
y = np.ravel(y)
clf = SVC(C=1.0, cache_size=200, class_weight=None, coef0=0.0,
    decision_function_shape='ovr', degree=3, gamma='auto', kernel='rbf',
    max_iter=-1, probability=False, random_state=None, shrinking=True,
    tol=0.001, verbose=True)
clf.fit(X, y)
predictions=clf.predict(X)
Correct=0
Total=predictions.size
for i in range (0,predictions.size):
    if(predictions[i] == y[i]):
        Correct = Correct + 1

Accuracy=(Correct/Total)*100
print("Accuracy: ",Accuracy,"%")
X = test_data #reducing elements in here to run faster, CHANGE THIS
y = test_label#change this
y = np.ravel(y)
clf = SVC(C=1.0, cache_size=200, class_weight=None, coef0=0.0,
    decision_function_shape='ovr', degree=3, gamma='auto', kernel='rbf',
    max_iter=-1, probability=False, random_state=None, shrinking=True,
    tol=0.001, verbose=True)
clf.fit(X, y)
predictions=clf.predict(X)
Correct=0
Total=predictions.size
for i in range (0,predictions.size):
    if(predictions[i] == y[i]):
        Correct = Correct + 1

Accuracy=(Correct/Total)*100
print("Accuracy: ",Accuracy,"%")
X = validation_data #reducing elements in here to run faster, CHANGE THIS
y = validation_label#change this
y = np.ravel(y)
clf = SVC(C=1.0, cache_size=200, class_weight=None, coef0=0.0,
    decision_function_shape='ovr', degree=3, gamma='auto', kernel='rbf',
    max_iter=-1, probability=False, random_state=None, shrinking=True,
    tol=0.001, verbose=True)
clf.fit(X, y)
predictions=clf.predict(X)
Correct=0
Total=predictions.size
for i in range (0,predictions.size):
    if(predictions[i] == y[i]):
        Correct = Correct + 1

Accuracy=(Correct/Total)*100
print("Accuracy: ",Accuracy,"%")
#------------------------------------#
cvals = [1,10,20,30,40,50,60,70,80,90,100]
for cvalue in cvals:
    
    print('\n\n--------------SVM-------------------\n\n')
    print("Radial Bias Segment Train C=",cvalue)
    X = train_data #reducing elements in here to run faster, CHANGE THIS
    y = train_label#change this
    y = np.ravel(y)
    
    clf = SVC(C=cvalue, cache_size=200, class_weight=None, coef0=0.0,
        decision_function_shape='ovr', degree=3, gamma='auto', kernel='rbf',
        max_iter=-1, probability=False, random_state=None, shrinking=True,
        tol=0.001, verbose=True)
    clf.fit(X, y)
    predictions=clf.predict(X)
    Correct=0
    Total=predictions.size
    for i in range (0,predictions.size):
        if(predictions[i] == y[i]):
            Correct = Correct + 1
    
    Accuracy=(Correct/Total)*100
    print("Accuracy: ",Accuracy,"%")
    
    
    print("Radial Bias Segment Validation C=",cvalue)
    X = validation_data #reducing elements in here to run faster, CHANGE THIS
    y = validation_label#change this
    y = np.ravel(y)
    
    clf = SVC(C=cvalue, cache_size=200, class_weight=None, coef0=0.0,
        decision_function_shape='ovr', degree=3, gamma='auto', kernel='rbf',
        max_iter=-1, probability=False, random_state=None, shrinking=True,
        tol=0.001, verbose=False)
    clf.fit(X, y)
    #Currently Set to Linear Kernel (1st Problem)
    #For 2nd problem, kernel='rbf' and gamma=1, possibly .1 according to piazza
    #For 3rd problem, set gamma to 'auto'
    #For 4th problem, set C=10,20,30...100 and record all values. Remove prints and run SVC 10x
    predictions=clf.predict(X)
    Correct=0
    Total=predictions.size
    for i in range (0,predictions.size):
        if(predictions[i] == y[i]):
            Correct = Correct + 1
    
    Accuracy=(Correct/Total)*100
    print("Accuracy: ",Accuracy,"%")
    
    print("Radial Bias Segment Testing C=",cvalue)
    X = test_data #reducing elements in here to run faster, CHANGE THIS
    y = test_label#change this
    y = np.ravel(y)
    
    clf = SVC(C=cvalue, cache_size=200, class_weight=None, coef0=0.0,
        decision_function_shape='ovr', degree=3, gamma='auto', kernel='rbf',
        max_iter=-1, probability=False, random_state=None, shrinking=True,
        tol=0.001, verbose=False)
    clf.fit(X, y)
    #Currently Set to Linear Kernel (1st Problem)
    #For 2nd problem, kernel='rbf' and gamma=1, possibly .1 according to piazza
    #For 3rd problem, set gamma to 'auto'
    #For 4th problem, set C=10,20,30...100 and record all values. Remove prints and run SVC 10x
    predictions=clf.predict(X)
    Correct=0
    Total=predictions.size
    for i in range (0,predictions.size):
        if(predictions[i] == y[i]):
            Correct = Correct + 1
    Accuracy=(Correct/Total)*100
    print("Accuracy: ",Accuracy,"%")

"""
Script for Extra Credit Part
"""
# FOR EXTRA CREDIT ONLY
print("Extra Credit")
W_b = np.zeros((n_feature + 1, n_class))
initialWeights_b = np.zeros((n_feature + 1, n_class))
opts_b = {'maxiter': 100}

start_time = time.time()

args_b = (train_data, Y)
nn_params = minimize(mlrObjFunction, initialWeights_b, jac=True, args=args_b, method='CG', options=opts_b)
W_b = nn_params.x.reshape((n_feature + 1, n_class))

# Find the accuracy on Training Dataset
predicted_label_b = mlrPredict(W_b, train_data)
print('\n Training set Accuracy:' + str(100 * np.mean((predicted_label_b == train_label).astype(float))) + '%')

# Find the accuracy on Validation Dataset
predicted_label_b = mlrPredict(W_b, validation_data)
print('\n Validation set Accuracy:' + str(100 * np.mean((predicted_label_b == validation_label).astype(float))) + '%')

# Find the accuracy on Testing Dataset
predicted_label_b = mlrPredict(W_b, test_data)
print('\n Testing set Accuracy:' + str(100 * np.mean((predicted_label_b == test_label).astype(float))) + '%')
print('\n Mlr time:' + str(time.time()- start_time))