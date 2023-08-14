__author__ = 'Zhang Juzheng'

from numpy import array,zeros,dot
import numpy as np
import sys
import math
from copy import copy
import heapq

def _diag(_array):
    # build diagonal matrix
    n_dim=_array.shape[0]
    res=zeros((n_dim,n_dim))
    for i in range(0,n_dim):
        res[i,i]=_array[i]
    return res

def matrix_slicing(row_index,mat):
    dim=mat.shape[1]
    num=len(row_index)
    n_coord=zeros((num,dim))
    j=0
    for i in row_index:
        n_coord[j,:]=mat[i,:]
        j=j+1
    return n_coord

def matrix_row(index,mat):
    return matrix_slicing(index,mat)

def matrix_col(index,mat):
    _mat=mat.T
    res=matrix_slicing(index,_mat)
    return res.T

# def matrix_row(index,mat):
#     r_dim=mat.shape[0]
#     idx=[0]*r_dim
#     for i in index:
#         idx[i]=1
#     res=np.compress(idx, mat, axis=0)
#     return res

# def matrix_col(index,mat):
#     r_dim=mat.shape[1]
#     idx=[0]*r_dim
#     for i in index:
#         idx[i]=1
#     res=np.compress(idx, mat, axis=1)
#     res=res.T
#     return res



def matrix_removal(row_index,mat):
    index=[]
    for i in range(0,mat.shape[0]):
        if i not in row_index:
            index.append(i)
    return matrix_slicing(index,mat)

def list_slicing(index,List):
    res=[]
    for i in index:
        res.append(List[i])
    return res

# def matrix_to_array(mat):
#     # transfer (5,1) to (5,)
#     x,y=mat.shape
#     if (not x==1) and (not y==1):
#         return mat
#     else:
#         n=max((x,y))
#         res=mat.reshape((n,))
#         return res

def sum_list_slice(index,List):
    res=0
    for idx in index:
        res+=List[idx]
    return res

def matrix_to_array(mat):
    return mat.flatten()

def array_to_matrix(arr):
    # transfer (5,) to (1,5)
    n=arr.shape[0]
    return arr.reshape((1,n))

def findequal(List,ele):
    # return all the position in the List contains ele
    res_idx=[]
    for i in range(0,len(List)):
        ll=List[i]
        if ll==ele:
            res_idx.append(i)
    if len(res_idx)==0:
        print "Error: the element is not in the list"
        sys.exit(0)
    else:
        return res_idx

def findlarger(List,ele):
    # return all the position in the List larger than ele
    res_idx=[]
    res_val=[]
    for i in range(0,len(List)):
        ll=List[i]
        if ll>ele:
            res_idx.append(i)
            res_val.append(copy(ll))
    if len(res_idx)==0:
        print "Error: there is no larger element in the list"
        sys.exit(0)
    else:
        return res_idx,res_val

def findbetween(List,lower,upper):
    # return all the position in the List between lower and upper
    res_idx=[]
    res_val=[]
    for i in range(0,len(List)):
        ll=List[i]
        if ll>lower and ll<upper:
            res_idx.append(i)
            res_val.append(copy(ll))
    # if len(res_idx)==0:
    #     print "Error: there is no element in between"
    #     sys.exit(0)
    # else:
    return res_idx,res_val

def find_above_threshold(_array,th):
    # _array should be a list
    # return sorted list with element larger than th
    n_dim=len(_array)
    n_max=[]
    n_idx=[]
    for i in range(0,n_dim):
        _arr=_array[i]
        if _arr>th:
            if len(n_max)==0:
                n_max.append(_arr)
                n_idx.append(i)
            else:
                j=0
                while j < len(n_max):
                    if _arr>n_max[j]:
                        n_max.insert(j,_arr)
                        n_idx.insert(j,i)
                        break
                    j=j+1
                if j==len(n_max):
                    n_max.append(_arr)
                    n_idx.append(i)
    return n_idx,n_max

def find_n_max(_array,num):
    # _array should be a list
    # return sorted list with n largest elements
    n_dim=len(_array)
    if n_dim<num:
        num=n_dim
        #print "the number of the returned episodes exceeds the total episodes"

    n_max=[-10]*num
    n_idx=[0]*num
    for i in range(0,n_dim):
        _arr=_array[i]
        for j in range(0,num):
            if _arr>n_max[j]:
                if isinstance(_arr,np.ndarray):
                    n_max.insert(j,_arr.tolist()[0])
                else:
                    n_max.insert(j,_arr)
                n_idx.insert(j,i)
                n_max.pop()
                n_idx.pop()
                break
    return n_idx,n_max

def find_n_max_dict(_dict,num):
    res=[]
    (n_idx,n_max)=find_n_max(_dict.values(),num)
    for idx in n_idx:
        res.append(_dict.keys()[idx])
    return (res,n_max[0:num])

def _cosine(cue,coord_list):
    res_list=[]
    n_dim=coord_list.shape[0]
    cue_norm=math.sqrt(dot(cue,cue.T))
    for i in range(0,n_dim):
        e=coord_list[i,:]
        e=array_to_matrix(e)
        e_norm=math.sqrt(dot(e,e.T))
        res=dot(cue,e.T)
        res=res/(e_norm*cue_norm)
        res_list.append(res[0])
    return res_list

def _cos(cue,e):
    if cue==None or e==None:
        return -1e3
    cue_norm=math.sqrt(dot(cue,cue))
    e_norm=math.sqrt(dot(e,e))
    if cue_norm<1e-3 or e_norm<1e-3:
        return 0
    res=dot(cue,e)
    res=res/(e_norm*cue_norm)
    return res

def _cosine_list(cue_list,coord_list):
    res_list=[]
    n_dim=coord_list.shape[0]
    for i in range(0,n_dim):
        cue=cue_list[i,:]
        e=coord_list[i,:]
        cue=array_to_matrix(cue)
        e=array_to_matrix(e)
        cue_norm=math.sqrt(dot(cue,cue.T))
        e_norm=math.sqrt(dot(e,e.T))
        res=dot(cue,e.T)
        res=res/(e_norm*cue_norm)
        res_list.append(res[0][0])
    return res_list

def _dot(cue,coord_list):
    dot_array=dot(coord_list,cue.T)
    dot_array=(dot_array.T.tolist())[0]
    return dot_array

class Stack:
    "A container with a last-in-first-out (LIFO) queuing policy."
    def __init__(self):
        self.list = []

    def push(self,item):
        "Push 'item' onto the stack"
        self.list.append(item)

    def pop(self):
        "Pop the most recently pushed item from the stack"
        return self.list.pop()

    def isEmpty(self):
        "Returns true if the stack is empty"
        return len(self.list) == 0

class Queue:
    "A container with a first-in-first-out (FIFO) queuing policy."
    def __init__(self):
        self.list = []

    def push(self,item):
        "Enqueue the 'item' into the queue"
        self.list.insert(0,item)

    def pop(self):
        """
          Dequeue the earliest enqueued item still in the queue. This
          operation removes the item from the queue.
        """
        return self.list.pop()

    def isEmpty(self):
        "Returns true if the queue is empty"
        return len(self.list) == 0

class PriorityQueue:
    """
      Implements a priority queue data structure. Each inserted item
      has a priority associated with it and the client is usually interested
      in quick retrieval of the lowest-priority item in the queue. This
      data structure allows O(1) access to the lowest-priority item.

      Note that this PriorityQueue does not allow you to change the priority
      of an item.  However, you may insert the same item multiple times with
      different priorities.
    """
    def  __init__(self):
        self.heap = []
        self.count = 0

    def push(self, item, priority):
        # FIXME: restored old behaviour to check against old results better
        # FIXED: restored to stable behaviour
        entry = (priority, self.count, item)
        # entry = (priority, item)
        heapq.heappush(self.heap, entry)
        self.count += 1

    def pop(self):
        (_, _, item) = heapq.heappop(self.heap)
        #  (_, item) = heapq.heappop(self.heap)
        return item

    def isEmpty(self):
        return len(self.heap) == 0
