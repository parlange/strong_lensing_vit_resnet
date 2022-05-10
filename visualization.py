import torch 
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

from tqdm import tqdm

from model_vit import (
    get_train_test_dataloaders, 
    get_train_test_datasets,
    prepare_data_and_target,
)




class VisualModel:

    def __init__(self, CONFIG, model_path):

        self.show_targets = ["theta_E", "e1", "e2"]

        self.CONFIG = CONFIG
        self.model_path = model_path

        self.device = torch.device("cpu")

        self.model = torch.load(self.model_path)
        self.model.to(self.device)
        self.model.eval()

        train_dataset, test_dataset = get_train_test_datasets(self.CONFIG)
        _, self.test_loader = get_train_test_dataloaders(self.CONFIG['batch_size'], train_dataset, test_dataset)
        
        self.n_test = test_dataset.__len__()
        
        self.pred_dict, self.truth_dict = self.get_pred_truth_dicts()


    def show_a_few_samples(self, n_batch, n_sample_batch):

        for batch_idx, (data, target_dict) in enumerate(self.test_loader):
            if batch_idx == n_batch:
                break
                
            data, _ = prepare_data_and_target(data, target_dict, self.device)
            pred = self.model(data)[0]
            
            for isample in range(self.CONFIG['batch_size']):
                if isample == n_sample_batch:
                    break
                
                for ikey, key in enumerate(target_dict):
                    if key in self.show_targets:
                        _truth = target_dict[key][isample][0].data
                        _pred = pred[isample][ikey].data
                        _error= (_pred - _truth) / _truth
                        print(f"{key}: truth = {_truth: 0.4f}, pred = {_pred: 0.4f}, error = {100 * _error: 0.2f} %")
            
                plt.imshow(data[isample, 0, :, :])
                plt.show()


    def get_pred_truth_dicts(self):

        pred_dict = {k: [] for k in self.show_targets}
        truth_dict = {k: [] for k in self.show_targets}

        for batch_idx, (data, target_dict) in enumerate(tqdm(self.test_loader, total=len(self.test_loader))):

            # #TODO: remove this
            # if batch_idx == 4:
            #     break
            
            data, _ = prepare_data_and_target(data, target_dict, self.device)
            pred = self.model(data)[0]

            for ikey, key in enumerate(target_dict):
                if key in self.show_targets:
                    _truth = target_dict[key][:, 0].detach().tolist()
                    _pred = pred[:, ikey].detach().tolist()

                    truth_dict[key].extend(_truth)
                    pred_dict[key].extend(_pred)

        for key in self.show_targets:
            truth_dict[key] = np.array(truth_dict[key])
            pred_dict[key] = np.array(pred_dict[key])

        return pred_dict, truth_dict


    def plot_each_pred_truth(self, target_key):
        sns.set(style="white", font_scale=1)
        fig, ax = plt.subplots()

        ax.set_aspect('equal', adjustable='box')
        
        x = self.truth_dict[target_key]
        y = self.pred_dict[target_key]

        xymin = min(min(x), min(y))
        xymax = max(max(x), max(y))

        ax.hexbin(x, y, extent=(xymin, xymax, xymin, xymax))
        ax.plot([xymin, xymax], [xymin, xymax], 'w--', alpha=0.5)

        ax.set_title(target_key)
        ax.set_xlabel('truth')
        ax.set_ylabel('prediction')


