import torch
from torch import nn
from torch.autograd import Function
from torch.autograd.function import once_differentiable
from torch.nn.modules.utils import _pair
from . import tree_filter_cuda as _C 

# import tree_filter_cuda as _C
# from contextlab.layers.tree_filter import tree_filter_cuda as _C 

class _Refine(Function):
    @staticmethod
    def forward(ctx, feature_in, edge_weight, sorted_index, sorted_parent, sorted_child):
        feature_out, feature_aggr, feature_aggr_up, weight_sum, weight_sum_up, =\
            _C.refine_forward(feature_in, edge_weight, sorted_index, sorted_parent, sorted_child)
            
        ctx.save_for_backward(feature_in, edge_weight, sorted_index, sorted_parent,
                sorted_child, feature_out, feature_aggr, feature_aggr_up, weight_sum,
                weight_sum_up)
        return feature_out

    @staticmethod
    @once_differentiable
    def backward(ctx, grad_output):
        feature_in, edge_weight, sorted_index, sorted_parent,\
        sorted_child, feature_out, feature_aggr, feature_aggr_up, weight_sum,\
        weight_sum_up, = ctx.saved_tensors;

        grad_feature = _C.refine_backward_feature(feature_in, edge_weight, sorted_index,
                sorted_parent, sorted_child, feature_out, feature_aggr, feature_aggr_up,
                weight_sum, weight_sum_up, grad_output)
        grad_weight = _C.refine_backward_weight(feature_in, edge_weight, sorted_index,
                sorted_parent, sorted_child, feature_out, feature_aggr, feature_aggr_up,
                weight_sum, weight_sum_up, grad_output)

        return grad_feature, grad_weight, None, None, None

refine = _Refine.apply

