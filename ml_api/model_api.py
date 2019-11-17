import torch
from torchvision import transforms

from PIL import Image
import numpy as np
import time


class ModelApi(object):
    def __init__(self, model_path):
        checkpoint = torch.load(model_path)
        self.model = checkpoint["model"]
        self.model.eval()
        self.prepare = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor()
        ])
        self.dic = checkpoint["classes"]

    def get_class(self, image):
        # print("Start")
        seconds = time.time()
        input = self.prepare(image)
        with torch.no_grad():
            prediction = self.model(input.unsqueeze(0)).squeeze()
        max_pred = prediction.argmax().item()
        print(prediction, self.dic[max_pred])
        # print("End: %f" % (time.time() - seconds))
        return self.dic[max_pred]
