import torch
import torch.nn as nn
from PIL import Image
import torchvision.transforms as transforms
#import numpy as np
#from skimage import transform



class AppleClassifierNet(nn.Module):
    def __init__(self):
        super(AppleClassifierNet,self).__init__()
        
        self.conv1 = nn.Conv2d(in_channels=3, out_channels=32, kernel_size=(3,3))
        self.conv2 = nn.Conv2d(in_channels=32, out_channels=64, kernel_size=(3,3))
        self.conv3 = nn.Conv2d(in_channels=64, out_channels=128, kernel_size=(3,3))
        self.conv4 = nn.Conv2d(in_channels=128, out_channels=128, kernel_size=(3,3))
        
        self.max = nn.MaxPool2d(kernel_size=(2,2))
        
        self.relu_func = nn.ReLU()
        self.softmax = nn.Softmax()
        
        self.full_connect1 = nn.Linear(in_features=6272, out_features=512)
        self.full_connect2 = nn.Linear(in_features=512, out_features=512)
        self.full_connect3 = nn.Linear(in_features=512, out_features=3)
        
        self.drop = nn.Dropout(0.25)
      
    def forward(self,x):
        
        x = self.conv1(x)
        x = self.relu_func(x)
        x = self.max(x)
        
        x = self.conv2(x)
        x = self.relu_func(x)
        x = self.max(x)
       
        x = self.conv3(x)
        x = self.relu_func(x)
        x = self.max(x)
        
        x = self.conv4(x)
        x = self.relu_func(x)
        x = self.max(x)
        
        x=torch.flatten(x,1) #Flatten
    
        x = self.drop(x)
        x = self.full_connect1(x)
        x = self.relu_func(x)
        
        x = self.full_connect2(x)
        x = self.relu_func(x)
        
        x = self.full_connect3(x)
        x = self.softmax(x)
        
        return x


class AppleClassifier:
    def __init__(self):
        self.yolo_model = torch.hub.load('ultralytics/yolov5', 'yolov5s')
        self.apple_model = torch.load("Apple_Torch_Model.pth").to("cpu").eval()
        self.image_transform = transforms.Compose([
                transforms.ToTensor(),
                transforms.Resize((150,150)),    
                transforms.Normalize((0.5,0.5,0.5),(0.5,0.5,0.5))
        ])
        
        self.classes = ["bad","good","mid"]
        self.good_apple_count = 0
        self.bad_apple_count = 0
        self.mid_apple_count = 0
        self.tot_apple_count = 0
        self.results_count = 0
        self.img_index = -1
        self.img_list = []
        self.results_list = []
        self.apple_list = []
        self.good_apple_list = []
        self.bad_apple_list = []
        self.mid_apple_list = []


    def resize_image(self,im, size=640):
        g = (size / max(im.size))  # gain
        return im.resize((int(x * g) for x in im.size), Image.ANTIALIAS)         

    def yolo(self,im, size=640):
        im = self.resize_image(im)
        results = self.yolo_model(im)  # inference
        results.render()  # updates results.imgs with boxes and labels
        return results, im

    def get_predict(self,image):
        tensor = self.image_transform(image).unsqueeze(0)
        outputs = self.apple_model.forward(tensor)
        _, y_hat = outputs.max(1)
        return y_hat

    def individual_image_apple_model(self,img,tensor_list):
        prediction = self.get_predict(img)
        if prediction == 0:
            self.bad_apple_count += 1
            label = "bad"
            imq_list = [self.img_index, prediction, label]
            t_list = tensor_list + imq_list
            self.bad_apple_list.append(t_list)
        elif prediction == 1:
            self.good_apple_count += 1
            label = "good"
            imq_list = [self.img_index, prediction, label]
            t_list = tensor_list + imq_list
            self.good_apple_list.append(t_list)
        elif prediction == 2:
            self.mid_apple_count += 1
            label = "mid"
            imq_list = [self.img_index, prediction, label]
            t_list = tensor_list + imq_list
            self.mid_apple_list.append(t_list)

        self.tot_apple_count = self.bad_apple_count + self.good_apple_count + self.mid_apple_count 
        self.apple_list.append(t_list)

    def calculateApples(self,img):
        results,im = self.yolo(img)
        self.img_list.append(im)
        self.img_index += 1
        pred_photo_list = [results.pred[0][i] for i in range(len(results.pred[0]))]
        self.results_list.append(results)
        for index,i in enumerate(pred_photo_list):
            tensor_list = i.tolist()    
            image = im.crop(tensor_list[:4]) #individual detected images
            label = tensor_list[-1] #apple label
            if label == 47:
                self.individual_image_apple_model(image,tensor_list)


    def show(self):
        self.results_list[0].show()

    def save_apple_img(self):
        pass