import numpy as np

images = np.zeros((0, 32, 32))
for i in range(1, 9):
    imgs = np.load('data' + str(i) + '.npy')
    images = np.append(images, imgs, axis=0)

images /= 255;

print(np.mean(images))
