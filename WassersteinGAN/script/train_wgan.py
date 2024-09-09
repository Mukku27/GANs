# -*- coding: utf-8 -*-
"""train_WGAN.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1wO0xS7u0emjMkKGJVS2q1zqxxMCJ6GFx
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
import torchvision as torchvision
from torchvision import datasets as datasets
import torchvision.transforms as transforms
from torch.utils.tensorboard import SummaryWriter
from model_wgan import Discriminator,Generator,initialize_weights
from utils import gradient_penalty

# Define device (CPU or GPU)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
LEARNING_RATE=1e-4
Batch_size=64
image_size=64
channels_img=1
z_dim=100
num_epochs=10
features_disc=64
features_gen=64
critc_iterations=5
lambda_gp=10
transforms=transforms.Compose(
    [
        transforms.Resize(image_size),
        transforms.ToTensor(),
        transforms.Normalize(
            [0.5 for _ in range(channels_img)],[0.5 for _ in range(channels_img)]
        ),

    ]

)

dataset=datasets.ImageFolder(root='celeb_dataset',transform=transforms)
loader=DataLoader(dataset,batch_size=Batch_size,shuffle=True)
gen=Generator(z_dim,channels_img,features_gen).to(device)
critic=Discriminator(channels_img,features_disc).to(device)
initialize_weights(gen)
initialize_weights(critic)
opt_gen=optim.Adam(gen.parameters(),lr=LEARNING_RATE,betas=(0.5,0.999))
opt_critic=optim.Adam(critic.parameters(),lr=LEARNING_RATE,betas=(0.5,0.999))

fixed_noise=torch.randn(32,z_dim,1,1).to(device)
writer_real=SummaryWriter(f"logs/real")
writer_fake=SummaryWriter(f"logs/fake")
step=0
gen.train()
critic.train()

for epoch in range(num_epochs):
  for batch_idx,(real,_) in enumerate(loader):
    real=real.to(device)

    for _ in range(critic_iterations):
        noise=torch.randn(Batch_size,z_dim,1,1).to(device)
        fake=gen(noise)
        critic_real=critic(real).reshape(-1)
        critic_fake=critic(fake).reshape(-1)
        gp=gradient_penalty(critic,real,fake,device=device)
        loss_critic=(-(torch.mean(critic_real)-torch.mean(critic_fake))+lambda_gp*gp)
        critic.zero_grad()
        loss_critic.backward(retain_graph=True)
        opt_critic.step()



    output=critic(fake).reshape(-1)
    loss_gen=-torch.mean(output)
    gen.zero_grad()
    loss_gen.backward()
    opt_gen.step()


    if batch_idx==0:
       print(f"Epochs[{epoch}\ {num_epochs}]/"
             f"Loss D:{loss_critic :.4f},Loss G:{lossG:.4f}")
       with torch.no_grad():
         fake=gen(fixed_noise)

         img_grid_fake=torchvision.utils.make_grid(fake[:32],normalize=True)
         img_grid_real=torchvision.utils.make_grid(real[:32],normalize=True)


         writer_fake.add_image(
            "MNIST fake images",img_grid_fake,global_step=step
        )
         writer_real.add_image(
            "MNIST real images",img_grid_real,global_step=step
        )
         step+=1
