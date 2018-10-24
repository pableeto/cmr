"""
Demo of CMR.

Note that CMR assumes that the object has been detected, so please use a picture of a bird that is centered and well cropped.

Sample usage:

python -m cmr.demo --name bird_net --num_train_epoch 500 --img_path cmr/demo_data/img1.jpg
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from absl import flags, app
import numpy as np
import skimage.io as io

import torch

from .nnutils import test_utils
from .nnutils import predictor as pred_util
from .utils import image as img_util
import glob

flags.DEFINE_string('img_path', 'data/im1963.jpg', 'Image to run')
flags.DEFINE_integer('img_size', 256, 'image size the network was trained on.')

opts = flags.FLAGS


def preprocess_image(img, img_size=256):
    # Scale the max image size to be img_size
    scale_factor = float(img_size) / np.max(img.shape[:2])
    img, _ = img_util.resize_img(img, scale_factor)

    # Crop img_size x img_size from the center
    center = np.round(np.array(img.shape[:2]) / 2).astype(int)
    # img center in (x, y)
    center = center[::-1]
    bbox = np.hstack([center - img_size / 2., center + img_size / 2.])

    img = img_util.crop(img, bbox, bgval=1.)

    # Transpose the image to 3xHxW
    img = np.transpose(img, (2, 0, 1))

    return img


def visualize(img, outputs, renderer):
    vert = outputs['verts'][0]
    cam = outputs['cam_pred'][0]
    texture = outputs['texture'][0]
    shape_pred = renderer(vert, cam)
    img_pred = renderer(vert, cam, texture=texture)

    # Different viewpoints.
    vp1 = renderer.diff_vp(
        vert, cam, angle=30, axis=[0, 1, 0], texture=texture, extra_elev=True)
    vp2 = renderer.diff_vp(
        vert, cam, angle=60, axis=[0, 1, 0], texture=texture, extra_elev=True)
    vp3 = renderer.diff_vp(
        vert, cam, angle=60, axis=[1, 0, 0], texture=texture)

    img = np.transpose(img, (1, 2, 0))
    import matplotlib.pyplot as plt
    plt.ion()
    plt.figure(1)
    plt.clf()
    plt.subplot(231)
    plt.imshow(img)
    plt.title('input')
    plt.axis('off')
    plt.subplot(232)
    plt.imshow(shape_pred)
    plt.title('pred mesh')
    plt.axis('off')
    plt.subplot(233)
    plt.imshow(img_pred)
    plt.title('pred mesh w/texture')
    plt.axis('off')
    plt.subplot(234)
    plt.imshow(vp1)
    plt.title('different viewpoints')
    plt.axis('off')
    plt.subplot(235)
    plt.imshow(vp2)
    plt.axis('off')
    plt.subplot(236)
    plt.imshow(vp3)
    plt.axis('off')
    plt.draw()
    plt.show()
    import ipdb
    ipdb.set_trace()


def main(_):
    predictor = pred_util.MeshPredictor(opts)
    img_list = glob.glob(opts.img_path + r'/*.jpg')
    for filename in img_list:
        img = io.imread(filename) / 255.
        img = preprocess_image(img, img_size=opts.img_size)
        batch = {'img': torch.Tensor(np.expand_dims(img, 0))}
    
        outputs = predictor.predict(batch)
        vert = (outputs['verts'][0].data).cpu().numpy()
        faces = (outputs['faces'].data).cpu().numpy()
        print(faces.shape)
        print(vert.shape)
        input()

    # This is resolution
    # renderer = predictor.vis_rend
    # renderer.set_light_dir([0, 1, -1], 0.4)

    # visualize(img, outputs, predictor.vis_rend)


if __name__ == '__main__':
    opts.batch_size = 1
    app.run(main)
