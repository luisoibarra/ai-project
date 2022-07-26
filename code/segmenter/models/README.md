# Segmenter Models

This folder contains the code to create tensorflow models to perform the argumentative unit segmentation.

## Docker

Tensorflow is constantly changing for that a docker image was created with a specific version (2.9.1) in order to the work can be easly executed in the future. The docker image already comes with jupyter notebook that allows an easy development.

- build_docker_image.sh: Run this script to build the docker image
- run.sh: Run this script to start a container of the created image

## Notebooks

- argument_segmentation.ipynb: This notebook contains all the code to process data, train, test and perform simple evaluation to the models.
- argument_segmentation_metrics.ipynb: This notebook performs a deep analysis of the created models.
