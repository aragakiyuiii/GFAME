# import os
# import torch
# import grb.utils as utils
# import os.path as osp
# from torch_geometric.datasets import Planetoid
# # from main import args
# import torch_geometric.transforms as T
# from torch_geometric.utils import negative_sampling
# from torch.nn.utils import clip_grad_norm, clip_grad_value_
# from torch_geometric.nn import GCNConv
# from grb.dataset import Dataset
# from grb.model.dgl import GAT
# from grb.model.torch import GCN
# from grb.utils.normalize import GCNAdjNorm
# from grb.defense import AdvTrainer
# from model.gnn import GCN, GCN_moe
# import numpy as np
# import torch.nn.functional as F
# from sklearn.metrics import roc_auc_score, accuracy_score
# from model.gnn import GCN, GCN_moe
# from utils import get_link_labels, prediction_fairness, Loss_contrastive, Loss_cosine
# from torch_geometric.utils import train_test_split_edges
# import argparse
# import grafog.transforms as grafog_T
#
# dataset_name = 'cora'
# model_name = "fair-drop-gcn"
# # model_name = "normal-gcn"
#
#
# lr = 0.01
#
# save_dir = "../saved_models/{}/{}".format(dataset_name, model_name)
# save_name = "model.pt"
# device = "cuda:0"
#
# path = osp.join(osp.dirname(osp.realpath('__file__')), "../..", "data", 'cora')
# dataset = Planetoid(path, 'cora', transform=T.NormalizeFeatures())
# data = dataset[0]
# protected_attribute = data.y
# # data.train_mask = data.val_mask = data.test_mask = data.y = None
# data = train_test_split_edges(data, val_ratio=0.1, test_ratio=0.2)
# data = data.to(device)
# num_classes = len(np.unique(protected_attribute))
# N = data.num_nodes
# acc_auc = []
# fairness = []
#
#
# model = GCN(data.num_features,64, 64).to(device)
# optimizer = torch.optim.Adam(model.parameters(), lr=lr)
#
# Y = torch.LongTensor(protected_attribute).to(device)
# Y_aux = (Y[data.train_pos_edge_index[0, :]] != Y[data.train_pos_edge_index[1, :]]).to(device)
# randomization = (torch.FloatTensor(1000, Y_aux.size(0)).uniform_() < 0.5 + 0.16).to(device)
#
# best_val_perf = test_perf = 0
# for epoch in range(1, 1000):
#     # TRAINING
#     neg_edges_tr = negative_sampling(
#         edge_index=data.train_pos_edge_index,
#         num_nodes=N,
#         num_neg_samples=data.train_pos_edge_index.size(1) // 2,
#     ).to(device)
#
#     if epoch == 1 or epoch % 10 == 0:
#         keep = torch.where(randomization[epoch], Y_aux, ~Y_aux)
#
#     model.train()
#     optimizer.zero_grad()
#     z = model(data.x, data.train_pos_edge_index)
#
#     link_logits, _ = model.decode(
#         z, data.train_pos_edge_index[:, keep], neg_edges_tr
#     )
#     tr_labels = get_link_labels(
#         data.train_pos_edge_index[:, keep], neg_edges_tr
#     ).to(device)
#
#
#     loss = F.binary_cross_entropy_with_logits(link_logits, tr_labels)
#     loss.backward()
#     cur_loss = loss.item()
#     optimizer.step()
#
#     # EVALUATION
#     model.eval()
#     perfs = []
#     for prefix in ["val", "test"]:
#         pos_edge_index = data[f"{prefix}_pos_edge_index"]
#         neg_edge_index = data[f"{prefix}_neg_edge_index"]
#         with torch.no_grad():
#             z = model(data.x, data.train_pos_edge_index)
#             link_logits, edge_idx = model.decode(z, pos_edge_index, neg_edge_index)
#         link_probs = link_logits.sigmoid()
#         link_labels = get_link_labels(pos_edge_index, neg_edge_index)
#         auc = roc_auc_score(link_labels.cpu(), link_probs.cpu())
#         perfs.append(auc)
#
#     val_perf, tmp_test_perf = perfs
#     if val_perf > best_val_perf:
#         best_val_perf = val_perf
#         test_perf = tmp_test_perf
#     if epoch % 10 == 0:
#         log = "Epoch: {:03d}, Loss: {:.4f}, Val: {:.4f}, Test: {:.4f}"
#         print(log.format(epoch, cur_loss, best_val_perf, test_perf))
#
# # FAIRNESS
# auc = test_perf
# cut = [0.45, 0.50, 0.55, 0.60, 0.65, 0.70, 0.75]
# best_acc = 0
# best_cut = 0.5
# for i in cut:
#     acc = accuracy_score(link_labels.cpu(), link_probs.cpu() >= i)
#     if acc > best_acc:
#         best_acc = acc
#         best_cut = i
# f = prediction_fairness(edge_idx.cpu(), link_labels.cpu(), link_probs.cpu() >= best_cut, Y.cpu())
# acc_auc.append([best_acc * 100, auc * 100])
# fairness.append([x * 100 for x in f])
#
# #Record bn parameters
# # running_variance_1st, running_mean_1st = model.norm_layer_1.running_var.cpu().detach().numpy(), model.norm_layer_1.running_mean.cpu().detach().numpy()
# running_variance_mid, running_mean_mid = model.norm_layer_2.running_var.cpu().detach().numpy(), model.norm_layer_2.running_mean.cpu().detach().numpy()
# running_variance_last, running_mean_last = model.norm_layer_3.running_var.cpu().detach().numpy(), model.norm_layer_2.running_mean.cpu().detach().numpy()
#
# # save running variance and mean in numpy array
# # np.save(os.path.join(save_dir, "running_variance_1st.npy"), running_variance_1st)
# # np.save(os.path.join(save_dir, "running_mean_1st.npy"), running_mean_1st)
# np.save(os.path.join(save_dir, "running_variance_mid.npy"), running_variance_mid)
# np.save(os.path.join(save_dir, "running_mean_mid.npy"), running_mean_mid)
# np.save(os.path.join(save_dir, "running_variance_last.npy"), running_variance_last)
# np.save(os.path.join(save_dir, "running_mean_last.npy"), running_mean_last)
#
# print('saved in {}'.format(save_dir))



import os
import torch
import grb.utils as utils
import os.path as osp
from torch_geometric.datasets import Planetoid
# from main import args
import torch_geometric.transforms as T
from torch_geometric.utils import negative_sampling
from torch.nn.utils import clip_grad_norm, clip_grad_value_
from torch_geometric.nn import GCNConv
from grb.dataset import Dataset
from grb.model.dgl import GAT
from grb.model.torch import GCN
from grb.utils.normalize import GCNAdjNorm
from grb.defense import AdvTrainer
from model.gnn import GCN, GCN_moe
import numpy as np
import torch.nn.functional as F
from sklearn.metrics import roc_auc_score, accuracy_score
from model.gnn import GCN, GCN_moe
from utils import get_link_labels, prediction_fairness, Loss_contrastive, Loss_cosine
from torch_geometric.utils import train_test_split_edges
import argparse
import grafog.transforms as grafog_T

dataset_name = 'cora'
model_name = "fair-drop-gcn"
# model_name = "normal-gcn"


lr = 0.0001

save_dir = "../saved_models/{}/{}".format(dataset_name, model_name)
save_name = "model.pt"
device = "cuda:0"

path = osp.join(osp.dirname(osp.realpath('__file__')), "../..", "data", 'cora')
dataset = Planetoid(path, 'cora', transform=T.NormalizeFeatures())
data = dataset[0]
protected_attribute = data.y
# data.train_mask = data.val_mask = data.test_mask = data.y = None
data = train_test_split_edges(data, val_ratio=0.1, test_ratio=0.2)
data = data.to(device)
num_classes = len(np.unique(protected_attribute))
N = data.num_nodes
acc_auc = []
fairness = []


model = GCN(data.num_features,96, 96).to(device)
optimizer = torch.optim.Adam(model.parameters(), lr=lr)

Y = torch.LongTensor(protected_attribute).to(device)
Y_aux = (Y[data.train_pos_edge_index[0, :]] != Y[data.train_pos_edge_index[1, :]]).to(device)
randomization = (torch.FloatTensor(500, Y_aux.size(0)).uniform_() < 0.5 + 0.16).to(device)

best_val_perf = test_perf = 0
for epoch in range(1, 500):
    # TRAINING
    neg_edges_tr = negative_sampling(
        edge_index=data.train_pos_edge_index,
        num_nodes=N,
        num_neg_samples=data.train_pos_edge_index.size(1) // 2,
    ).to(device)

    if epoch == 1 or epoch % 10 == 0:
        keep = torch.where(randomization[epoch], Y_aux, ~Y_aux)

    model.train()
    optimizer.zero_grad()
    z = model(data.x, data.train_pos_edge_index)

    link_logits, _ = model.decode(
        z, data.train_pos_edge_index[:, keep], neg_edges_tr
    )
    tr_labels = get_link_labels(
        data.train_pos_edge_index[:, keep], neg_edges_tr
    ).to(device)


    loss = F.binary_cross_entropy_with_logits(link_logits, tr_labels)
    loss.backward()
    cur_loss = loss.item()
    optimizer.step()

    # EVALUATION
    model.eval()
    perfs = []
    for prefix in ["val", "test"]:
        pos_edge_index = data[f"{prefix}_pos_edge_index"]
        neg_edge_index = data[f"{prefix}_neg_edge_index"]
        with torch.no_grad():
            z = model(data.x, data.train_pos_edge_index)
            link_logits, edge_idx = model.decode(z, pos_edge_index, neg_edge_index)
        link_probs = link_logits.sigmoid()
        link_labels = get_link_labels(pos_edge_index, neg_edge_index)
        auc = roc_auc_score(link_labels.cpu(), link_probs.cpu())
        perfs.append(auc)

    val_perf, tmp_test_perf = perfs
    if val_perf > best_val_perf:
        best_val_perf = val_perf
        test_perf = tmp_test_perf
    if epoch % 10 == 0:
        log = "Epoch: {:03d}, Loss: {:.4f}, Val: {:.4f}, Test: {:.4f}"
        print(log.format(epoch, cur_loss, best_val_perf, test_perf))

# FAIRNESS
auc = test_perf
cut = [0.45, 0.50, 0.55, 0.60, 0.65, 0.70, 0.75]
best_acc = 0
best_cut = 0.5
for i in cut:
    acc = accuracy_score(link_labels.cpu(), link_probs.cpu() >= i)
    if acc > best_acc:
        best_acc = acc
        best_cut = i
f = prediction_fairness(edge_idx.cpu(), link_labels.cpu(), link_probs.cpu() >= best_cut, Y.cpu())
acc_auc.append([best_acc * 100, auc * 100])
fairness.append([x * 100 for x in f])

#Record bn parameters
# running_variance_1st, running_mean_1st = model.norm_layer_1.running_var.cpu().detach().numpy(), model.norm_layer_1.running_mean.cpu().detach().numpy()
running_variance_mid, running_mean_mid = model.norm_layer_2.running_var.cpu().detach().numpy(), model.norm_layer_2.running_mean.cpu().detach().numpy()
running_variance_last, running_mean_last = model.norm_layer_3.running_var.cpu().detach().numpy(), model.norm_layer_2.running_mean.cpu().detach().numpy()

# save running variance and mean in numpy array
# np.save(os.path.join(save_dir, "running_variance_1st.npy"), running_variance_1st)
# np.save(os.path.join(save_dir, "running_mean_1st.npy"), running_mean_1st)
np.save(os.path.join(save_dir, "running_variance_mid.npy"), running_variance_mid)
np.save(os.path.join(save_dir, "running_mean_mid.npy"), running_mean_mid)
np.save(os.path.join(save_dir, "running_variance_last.npy"), running_variance_last)
np.save(os.path.join(save_dir, "running_mean_last.npy"), running_mean_last)

print('saved in {}'.format(save_dir))
