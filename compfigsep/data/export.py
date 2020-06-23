"""
#############################
#        CompFigSep         #
# Compound Figure Separator #
#############################

GitHub:         https://github.com/GaetanLepage/compound-figure-separator

Author:         Gaétan Lepage
Email:          gaetan.lepage@grenoble-inp.org
Date:           Spring 2020

Master's project @HES-SO (Sierre, SW)

Supervisors:    Henning Müller (henning.mueller@hevs.ch)
                Manfredo Atzori (manfredo.atzori@hevs.ch)

Collaborator:   Niccolò Marini (niccolo.marini@hevs.ch)


####################################
Export tools for panel-seg datasets.
"""

from typing import Iterable

import csv

from ..utils.figure import Figure
from ..utils.figure.label_class import LABEL_CLASS_MAPPING


def export_figures_to_csv(figure_generator: Iterable[Figure],
                          output_csv_file: str,
                          individual_export: bool = False,
                          individual_export_csv_directory: str = None):
    """
    Export a set of figures to a csv file.
    This may be used for keras-retinanet.

    Args:
        figure_generator (Iterable[Figure]):    A generator yielding figure objects
        output_csv_file (str):                  The path of the csv file containing the
                                                    annotations
        individual_csv (bool):                  If True, also export the annotation to a single
                                                    csv file
        individual_export_csv_directory (str):  The path of the directory whete to store the
                                                    individual csv annotation files."
    """

    with open(output_csv_file, 'w', newline='') as csvfile:

        csv_writer = csv.writer(csvfile, delimiter=',')

        # Looping over Figure objects thanks to generator
        for figure in figure_generator:

            # Looping over SubFigure objects
            for subfigure in figure.gt_subfigures:

                panel = subfigure.panel
                csv_row = [
                    figure.image_path,
                    panel.box[0],
                    panel.box[1],
                    panel.box[2],
                    panel.box[3],
                    'panel'
                    ]

                label = subfigure.label
                if label is not None and label.box is not None:
                    csv_row.append(label.box[0])
                    csv_row.append(label.box[1])
                    csv_row.append(label.box[2])
                    csv_row.append(label.box[3])
                    csv_row.append(label.text)
                else:
                    csv_row += [''] * 5
                csv_writer.writerow(csv_row)

                if individual_export:
                    figure.export_annotation_to_individual_csv(
                        csv_export_dir=individual_export_csv_directory)


def export_figures_to_tf_record(figure_generator: Iterable[Figure],
                                tf_record_filename: str):
    """
    Convert a set of figures to a a TensorFlow records file.

    Args:
        figure_generator (Iterable[Figure]):    A generator yielding figure objects.
        tf_record_filename (str):               Path to the output tf record file.
    """
    # Import TensorFlow.
    import tensorflow as tf

    with tf.io.TFRecordWriter(tf_record_filename) as writer:

        for figure in figure_generator:

            tf_example = figure.convert_to_tf_example()

            writer.write(tf_example.SerializeToString())


def export_figures_to_detectron_dict(figure_generator: Iterable[Figure],
                                     task: str = 'panel_splitting') -> dict:
    """
    Export a set of Figure objects to a dict which is compatible with Facebook Detectron 2.

    Args:
        figure_generator (Iterable[Figure]):    A generator yielding figure objects.
        task (str):                             The task for which to export the figures.

    Returns:
        dataset_dicts (dict): A dict representing the data set.
    """
    from detectron2.structures import BoxMode

    if task not in ['panel_splitting', 'label_recog', 'panel_seg']:
        raise ValueError("`task` has to be one of ['panel_splitting', 'label_recog',"\
            f" 'panel_seg'] but is {task}")

    dataset_dicts = []
    for index, figure in enumerate(figure_generator):
        record = {}

        record['file_name'] = figure.image_path
        record['image_id'] = index
        record['height'] = figure.image_height
        record['width'] = figure.image_width

        objs = []

        if figure.gt_panels is not None:

            for subfigure in figure.gt_subfigures:

                panel = subfigure.panel
                label = subfigure.label

                if task == 'panel_splitting':
                    obj = {
                        'bbox': panel.box,
                        'bbox_mode': BoxMode.XYXY_ABS,
                        'category_id': 0
                    }

                elif task == 'label_recog':
                    if label.box is None or len(label.text) != 1:
                        # We ensure that, for this task, the labels are valid
                        # (they have been previously checked while loading annotations)
                        continue

                    obj = {
                        'bbox': label.box,
                        'bbox_mode': BoxMode.XYXY_ABS,
                        'category_id': LABEL_CLASS_MAPPING[label.text]
                    }

                # panel segmentation task
                else:
                    # category_id is artificially set to zero to satisfy the Detectron API.
                    # The actual label (if any) is stored in 'label'.
                    obj = {
                        'panel_bbox': panel.box,
                        'bbox_mode': BoxMode.XYXY_ABS
                    }

                    if label.box is not None and len(label.box) == 1:
                        # If there is no valid label, it won't be considered for training.
                        # TODO: later, we would like to handle >1 length labels
                        obj['label_bbox'] = label.box
                        obj['label'] = LABEL_CLASS_MAPPING[label.text]


                objs.append(obj)

            record["annotations"] = objs

        dataset_dicts.append(record)

    return dataset_dicts