# Tensorflow
import tensorflow as tf

# print("Num GPUs Available: ", len(tf.config.experimental.list_physical_devices('GPU')))

# I/O libraries
import os
import tarfile

# Helper libraries
import numpy as np
from PIL import Image
import cv2

# Comment this out if you want to see Deprecation warnings
import warnings

warnings.simplefilter("ignore", DeprecationWarning)




class DeepLabmodel(object):
    FROZEN_GRAPH_NAME = 'frozen_inference_graph'

    def __init__(self, tarball_path):
        # Creates and loads pretrained deeplab model
        self.graph = tf.Graph()
        graph_def = None

        # Extract frozen graph from tar archive.
        tar_file = tarfile.open(tarball_path)
        for tar_info in tar_file.getmembers():
            if self.FROZEN_GRAPH_NAME in os.path.basename(tar_info.name):
                file_handle = tar_file.extractfile(tar_info)
                graph_def = tf.compat.v1.GraphDef.FromString(file_handle.read())
                break
        tar_file.close()

        if graph_def is None:
            raise RuntimeError('Cannot find inference graph in tar archive.')

        with self.graph.as_default():
            tf.import_graph_def(graph_def, name='')
        self.sess = tf.compat.v1.Session(graph=self.graph)

    def run(self, image, input_tensor_name='ImageTensor:0', output_tensor_name='SemanticPredictions:0'):
        # Runs inference on a single image
        # Args:
        #   image: A PIL.Image object, raw input image.
        #   INPUT_TENSOR_NAME: The name of input tensor, default to ImageTensor.
        #   OUTPUT_TENSOR_NAME: The name of output tensor, default to SemanticPredictions.
        # Returns:
        #   resized_image: RGB image resized from original input image.
        #   seg_map: Segmentation map of `resized_image`.

        width, height = image.size
        target_size = (2049, 1025)  # size of Cityscapes images
        resized_image = image.convert('RGB').resize(target_size, Image.ANTIALIAS)
        batch_seg_map = self.sess.run(
            output_tensor_name,
            feed_dict={input_tensor_name: [np.asarray(resized_image)]})
        seg_map = batch_seg_map[0]  # expected batch size = 1
        if len(seg_map.shape) == 2:
            seg_map = np.expand_dims(seg_map, -1)  # need an extra dimension for cv.resize
        seg_map = cv2.resize(seg_map, (width, height), interpolation=cv2.INTER_NEAREST)
        return seg_map


def create_label_colormap():
    # Create a label colormap used in Cityscapes segmentation benchmark
    # Returns:
    #   A Colormap for visualizing segmentation results
    colormap = np.array([
        [128, 64, 128], [244, 35, 232],
        [70, 70, 70], [102, 102, 156],
        [190, 153, 153], [153, 153, 153],
        [250, 170, 30], [220, 220, 0],
        [107, 142, 35], [152, 251, 152],
        [70, 130, 180], [220, 20, 60],
        [255, 0, 0], [0, 0, 142],
        [0, 0, 70], [0, 60, 100],
        [0, 80, 100], [0, 0, 230],
        [119, 11, 32], [0, 0, 0]], dtype=np.uint8)
    return colormap


def label_to_color_image(label):
    # Adds a color defined by the dataset colormap to the label
    # Args:
    #   label: A 2D array with integer type, storing the segmentation label
    # Returns:
    #   result: A 2D array with floating type. The element of the array
    #             is the color indexed by the corresponding element in the input label
    #             to the PASCAL color map.
    # Raises:
    #   ValueError: If label is not of rank 2 or its value is larger than color
    #             map maximum entry.
    if label.ndim != 2:
        raise ValueError('Expect 2-D input label')

    colormap = create_label_colormap()

    if np.max(label) >= len(colormap):
        raise ValueError('label value too large.')

    return colormap[label]


# def vis_segmentation(image, seg_map):
#     """Visualizes input image, segmentation map and overlay view."""
#     plt.figure(figsize=(20, 4))
#     grid_spec = gridspec.GridSpec(1, 4, width_ratios=[6, 6, 6, 1])
#
#     plt.subplot(grid_spec[0])
#     plt.imshow(image)
#     plt.axis('off')
#     plt.title('input image')
#
#     plt.subplot(grid_spec[1])
#     seg_image = label_to_color_image(seg_map).astype(np.uint8)
#     plt.imshow(seg_image)
#     plt.axis('off')
#     plt.title('segmentation map')
#
#     plt.subplot(grid_spec[2])
#     plt.imshow(image)
#     plt.imshow(seg_image, alpha=0.7)
#     plt.axis('off')
#     plt.title('segmentation overlay')
#
#     unique_labels = np.unique(seg_map)
#     ax = plt.subplot(grid_spec[3])
#     plt.imshow(full_color_map[unique_labels].astype(np.uint8), interpolation='nearest')
#     ax.yaxis.tick_right()
#     plt.yticks(range(len(unique_labels)), label_names[unique_labels])
#     plt.xticks([], [])
#     ax.tick_params(width=0.0)
#     plt.grid('off')
#     plt.show()


label_names = np.asarray(
    ['road', 'sidewalk', 'building', 'wall', 'fence', 'pole', 'traffic light', 'traffic sign', 'vegetation', 'terrain',
     'sky', 'person', 'rider', 'car', 'truck', 'bus', 'train', 'motorcycle', 'bicycle', 'void'])

full_label_map = np.arange(len(label_names)).reshape(len(label_names), 1)
full_color_map = label_to_color_image(full_label_map)

model = DeepLabmodel('./model/deeplab_model.tar.gz')
print('model loaded successfully!')


def run_visualization(image):
    """Inferences DeepLab model and visualizes result."""
    original_im = Image.fromarray(image)
    seg_map = model.run(original_im)
    seg_image = label_to_color_image(seg_map).astype(np.uint8)

    return seg_image


if __name__ == "__main__":
    cap = cv2.VideoCapture('./sample/mit_driveseg_sample.mp4')

    while cap.isOpened():
        ret, frame = cap.read()

        if ret:

            alpha = 0.5
            # create two copies of the original image -- one for
            # the overlay and one for the final output image
            # overlay = frame.copy()

            overlay = run_visualization(frame)

            # # draw a red rectangle surrounding Adrian in the image
            # # along with the text "PyImageSearch" at the top-left
            # # corner
            # cv2.rectangle(overlay, (420, 205), (595, 385),
            #               (0, 0, 255), -1)
            #
            # apply the overlay
            cv2.addWeighted(overlay, alpha, frame, 1 - alpha,
                            0, frame)

            cv2.imshow("Output", frame)
        else:
            print('no video')
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
