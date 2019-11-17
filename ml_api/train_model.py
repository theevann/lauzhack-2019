import os

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torch.optim import lr_scheduler

import torchvision
from torchvision import datasets, models, transforms

import numpy as np
import colorama


def train_model(model_type, model_name, num_epochs):
    data_dir = "train"

    train_data = datasets.ImageFolder(data_dir,
                                      transform=transforms.Compose([
                                          transforms.RandomResizedCrop(224),
                                          transforms.RandomHorizontalFlip(),
                                          transforms.ToTensor()
                                      ]))

    train_loader = DataLoader(train_data, batch_size=16, shuffle=True)
    class_names = train_data.classes
    num_classes = len(class_names)
    print("Found classes: ", class_names)

    if model_type == "sqnet":
        model_ft = models.squeezenet1_1(pretrained=True)
        model_ft.classifier[1] = nn.Conv2d(512, num_classes, kernel_size=1)
    elif model_type == "mbnet":
        model_ft = models.mobilenet_v2(pretrained=True)
        model_ft.classifier[1] = nn.Linear(
            in_features=1280, out_features=num_classes)
    elif model_type == "resnet18":
        model_ft = models.resnet18(pretrained=True)
        model_ft.fc = nn.Linear(in_features=512, out_features=num_classes)

    for name, param in model_ft.named_parameters():
        if name not in ["fc.weight", "fc.bias", "classifier.weight", "classifier.bias", "classifier.1.weight", "classifier.1.bias"]:
            param.requires_grad = False

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model_ft = model_ft.to(device)

    train(model_ft, train_loader, device, num_epochs=num_epochs)
    torch.save({"model": model_ft, "classes": class_names},
               "models/%s.pth" % model_name)


def train(model, train_loader, device, num_epochs=3, lr=0.1):
    model.train()
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    criterion = torch.nn.CrossEntropyLoss()

    for epoch in range(num_epochs):
        print("=" * 40, "Starting epoch %d" % (epoch + 1), "=" * 40)

        cum_loss = 0

        for batch_idx, (data, labels) in enumerate(train_loader):
            data, labels = data.to(device), labels.to(device)

            optimizer.zero_grad()

            output = model(data)
            loss = criterion(output, labels)
            loss.backward()
            optimizer.step()

            cum_loss += loss.item()

            if batch_idx % 1 == 0:
                print("Batch %d/%d" % (batch_idx, len(train_loader)))

        acc = accuracy(model, train_loader, device)
        print(colorama.Fore.GREEN + "\nEpoch %d/%d, Loss=%.4f, Train-Acc=%d%%"
              % (epoch+1, num_epochs, cum_loss / len(train_loader.dataset), 100 * acc), colorama.Fore.RESET)


def accuracy(model, dataloader, device):
    model.eval()
    num_correct = 0
    num_samples = 0
    with torch.no_grad():
        for data, labels in dataloader:
            data, labels = data.to(device), labels.to(device)
            predictions = model(data).argmax(1)
            num_correct += (predictions == labels).sum().item()
            num_samples += predictions.shape[0]
    return num_correct / num_samples
