import os
import PIL.Image as Image
import torch
import torch.utils.data as data
import openslide

class Dataset(data.Dataset):
    def __init__(self, test_lib, patch_size, transform=None):
        self.slide = openslide.OpenSlide(test_lib['slides'][0])
        self.grid = test_lib['grid'][0]
        self.level = test_lib['level']
        self.size = patch_size
        self.transform = transform

    def __getitem__(self, index):
        coord = self.grid[index]
        img = self.slide.read_region(coord,self.level,(self.size,self.size)).convert('RGB')
        if self.transform is not None:
            img = self.transform(img)
        width, height = int(coord[0]), int(coord[1])
        coor = torch.Tensor([width, height])
        return img, coor

    def __len__(self):
        return len(self.grid)


class data_prefetcher():
    def __init__(self, loader):
        self.loader = iter(loader)
        self.stream = torch.cuda.Stream()
        self.preload()

    def preload(self):
        try:
            self.next_input = next(self.loader)
        except StopIteration:
            self.next_input = None
            return
        with torch.cuda.stream(self.stream):
            self.next_input = self.next_input.cuda(non_blocking=True)
            self.next_input = self.next_input.float()

    def next(self):
        torch.cuda.current_stream().wait_stream(self.stream)
        input = self.next_input
        self.preload()
        return input