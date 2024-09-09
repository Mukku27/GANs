# -*- coding: utf-8 -*-
"""simple_GAN.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/18m0HR4zBhUIx1EUKzzyazMHBj0Umliqj
"""

!pip install torch
!pip install torchvision

import  torch
import torch.nn as nn
import torch.optim as optim
import torchvision
import torchvision.datasets as datasets
from torch.utils.data import DataLoader
import torchvision.transforms as transforms
from torch.utils.tensorboard import SummaryWriter

class Discriminator(nn.Module):
  def __init__(self, img_dim):
    super().__init__()
    self.disc=nn.Sequential(
        nn.Linear(img_dim,128),
        nn.LeakyReLU(0.1),
        nn.Linear(128,1),
        nn.Sigmoid(),
    )
  def forward (self,x):
       return self.disc(x)

class Generator(nn.Module):
   def __init__(self,z_dim,img_dim):
      super().__init__()
      self.gen=nn.Sequential(
          nn.Linear(z_dim,256),
          nn.LeakyReLU(0.1),
          nn.Linear(256,img_dim),
          nn.Tanh(),
      )
   def forward(self,x):
      return self.gen(x)

device= 'cuda' if torch.cuda.is_available()  else 'cpu'
learning_rate=3e-4
z_dim=64
image_dim =28*28*1
batch_size=64
num_epochs=100

disc=Discriminator(image_dim).to(device)
gen=Generator(z_dim,image_dim).to(device)
fixed_noise=torch.randn(batch_size,z_dim).to(device)
transforms=transforms.Compose([transforms.ToTensor(),transforms.Normalize((0.5,),(0.5, ))])

dataset=datasets.MNIST(root="dataset/",transform=transforms,download=True)
loader=DataLoader(dataset,batch_size=batch_size,shuffle=True)
opt_disc=optim.Adam(disc.parameters(),lr=learning_rate )
opt_gen=optim.Adam(gen.parameters(),lr=learning_rate)
criterion=nn.BCELoss()
writer_fake=SummaryWriter(f"runs/GAN_MNIST/fake")
writer_real=SummaryWriter(f"runs/GAN_MNIST/real")
step=0

for epoch in range(num_epochs):
   for batch_idx,(real,_) in enumerate(loader):
     real=real.view(-1,784).to(device)
     batch_size=real.shape[0]

     #train_discriminator
     noise=torch.randn(batch_size,z_dim).to(device)
     fake=gen(noise)
     disc_real=disc(real).view(-1)
     lossD_real=criterion(disc_real,torch.ones_like(disc_real))
     disc_fake=disc(fake).view(-1)
     lossD_fake=criterion(disc_fake,torch.zeros_like(disc_fake))
     lossD=(lossD_fake+lossD_real)/2
     disc.zero_grad()
     lossD.backward(retain_graph=True)
     opt_disc.step()


     #train_generator
     output=disc(fake).view(-1)
     lossG=criterion(output,torch.ones_like(output))
     gen.zero_grad()
     lossG.backward()
     opt_gen.step()


     if batch_idx==0:
       print(f"Epochs[{epoch}\ {num_epochs}]/"
             f"Loss D:{lossD:.4f},Loss G:{lossG:.4f}")
       with torch.no_grad():
        fake=gen(fixed_noise).reshape(-1,1,28,28)
        data=real.reshape(-1,1,28,28)
        img_grid_fake=torchvision.utils.make_grid(fake,normalize=True)
        img_grid_real=torchvision.utils.make_grid(real,normalize=True)


        writer_fake.add_image(
            "MNIST fake images",img_grid_fake,global_step=step
        )
        writer_real.add_image(
            "MNIST real images",img_grid_real,global_step=step
        )
        step+=1
