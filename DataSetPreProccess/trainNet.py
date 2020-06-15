import GazeModel
import DataSetPreProccess.MPIIDataLoader as MPIIDataLoader
import torch.nn as nn
import torch
import numpy as np
import torchvision
from torch.utils.tensorboard import SummaryWriter
import matplotlib.pyplot as plt

device = 'cuda' if torch.cuda.is_available() else 'cpu'


def convert_to_unit_vector( angles):
    pitches = angles[:, 0]
    yaws = angles[:, 1]
    x = -torch.cos(pitches) * torch.sin(yaws)
    y = -torch.sin(pitches)
    z = -torch.cos(pitches) * torch.cos(yaws)
    norm = torch.sqrt(x**2 + y**2 + z**2)
    x /= norm
    y /= norm
    z /= norm
    return x, y, z


def compute_angle_error(predictions,labels):
    pred_x, pred_y, pred_z = convert_to_unit_vector(predictions)
    label_x, label_y, label_z = convert_to_unit_vector(labels)
    angles = pred_x * label_x + pred_y * label_y + pred_z * label_z
    return torch.acos(angles) * 180 / np.pi


def validate (epoch, model, optimizer, loss_function, val_loader,writer):
    model.eval()
    torch.no_grad()
    for step, (images, poses, gazes) in enumerate(val_loader):

        ## send to Device
        images = images.to(device)
        poses = poses.to(device)
        gazes = gazes.to(device)

        ## use the net!
        outputs = model(images, poses)

        ## caclculate loss function
        loss = loss_function(outputs, gazes)

        angle_error = compute_angle_error(outputs, gazes).mean()
        num = images.size(0)


        if step % 100 == 0:
            writer.add_scalar('Val loss', loss.item() * 100, epoch * len(val_loader) + step)
            writer.add_scalar('Val angle loss', angle_error, epoch * len(val_loader) + step)
            print("Validate: now in epoch " + str(epoch) + " and step number " + str(step) + " loss is " + str(
                loss.item()) + "angle error is:" + str(angle_error.item()))


def train (epoch, model, optimizer, loss_function, train_loader,writer):
    model.train()
    running_loss = 0.0
    for step, (images, poses, gazes) in enumerate(train_loader):
        ## send to Device
        images = images.to(device)
        poses = poses.to(device)
        gazes = gazes.to(device)

        ## init optimizer
        optimizer.zero_grad()

        ## use the net!
        outputs = model(images, poses)

        ## caclculate loss function
        loss = loss_function(outputs, gazes)
        running_loss += loss.item()

        ## backpropogation
        loss.backward()

        ## do a step
        optimizer.step()

        ## compute the angle error
        angle_error = compute_angle_error(outputs, gazes).mean()

        num = images.size(0)

        if step % 25 == 0:
            writer.add_scalar('training loss',loss.item()*100,(epoch) * len(train_loader) + step)
            writer.add_scalar('training angle loss', angle_error , (epoch) * len(train_loader) + step)
            print("Train: now in epoch " + str(epoch) + " and step number " + str(step) + " loss is " + str(loss.item())+ " angle error is: " + str(angle_error.item()))


def train_and_validate_aux (num_ephocs):
    train_loader, val_loader , test_loader = MPIIDataLoader.create_dataloader()

    model = GazeModel.GazeNet().to(device)
    model.init_weights()
    loss_function = nn.MSELoss(reduction='mean')
    optimizer = torch.optim.SGD(model.parameters(),
                                lr=0.001,
                                momentum=0.9,
                                nesterov=True)

    train_writer = SummaryWriter('runs/train')
    for epoch in range(0,num_ephocs):
        train(epoch, model, optimizer ,loss_function, train_loader,train_writer)
    train_writer.close()

    val_writer = SummaryWriter('runs/val')
    for epoch in range(0, num_ephocs ):
        validate(epoch, model, optimizer, loss_function, val_loader,val_writer)
    val_writer.close()

    # torch.save(model.state_dict(),"RES/TRAINED_NET")
