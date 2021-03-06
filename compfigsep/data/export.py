"""
#############################
#        CompFigSep         #
# Compound Figure Separator #
#############################

GitHub:         https://github.com/GaetanLepage/compound-figure-separator

Author:         Gaétan Lepage
Email:          gaetan.lepage@grenoble-inp.fr
Date:           Spring 2020

Master's project @HES-SO (Sierre, SW)

Supervisors:    Henning Müller (henning.mueller@hevs.ch)
                Manfredo Atzori (manfredo.atzori@hevs.ch)

Collaborators:  Niccolò Marini (niccolo.marini@hevs.ch)
                Stefano Marchesin (stefano.marchesin@unipd.it)


#####################################
Export tools for compfigseg datasets.
"""

import csv
import json
import os
import logging
import datetime
from typing import List, Dict, Any

import compfigsep

from .figure_generators import FigureGenerator
from ..utils.figure import Panel
from ..utils.figure.label import map_label, LABEL_CLASS_MAPPING


PROJECT_DIR = os.path.join(os.path.dirname(compfigsep.__file__),
                           os.pardir)

def export_figures_to_csv(figure_generator: FigureGenerator,
                          output_csv_file: str,
                          individual_export: bool = False,
                          individual_export_csv_directory: str = None) -> None:
    """
    Export a set of figures to a csv file.
    This may be used for keras-retinanet.

    Args:
        figure_generator (FigureGenerator):     A generator yielding figure objects
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
        for figure in figure_generator():

            # Looping over SubFigure objects
            for subfigure in figure.gt_subfigures:

                if subfigure.panel is None:
                    continue

                panel: Panel = subfigure.panel

                csv_row = [figure.image_path,
                           panel.box[0],
                           panel.box[1],
                           panel.box[2],
                           panel.box[3],
                           'panel']

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
                    figure.export_gt_annotation_to_individual_csv(
                        csv_export_dir=individual_export_csv_directory)


def export_figures_to_json(figure_generator: FigureGenerator,
                           json_output_filename: str = None,
                           json_output_directory: str = None) -> None:
    """
    Export a data set that can contain ground truth and/or detected annotations for any task to a
    JSON file.

    Args:
        figure_generator (FigureGenerator): A generator yielding figure objects.
        json_output_filename (str):         Name of the JSON output file.
        json_output_directory (str):        Path to the directory where to save the JSON
                                                output file.
    """

    if json_output_directory is None:

        # If no directory was given, use the default one.
        if json_output_filename is not None:
            json_output_directory_: str = os.path.dirname(json_output_filename)

            if not os.path.isdir(json_output_directory_):
                return

        else:
            json_output_directory_ = os.path.join(PROJECT_DIR, "output/")

    else:
        json_output_directory_ = json_output_directory


    # Create output directory if it does not exist yet.
    if not os.path.isdir(json_output_directory_):
        os.mkdir(json_output_directory_)

    if json_output_filename is None:
        json_output_filename = "compfigsep_experiment_{date:%Y-%B-%d_%H:%M:%S}.json".format(
            date=datetime.datetime.now())

    json_output_path: str = os.path.join(json_output_directory_,
                                         json_output_filename)

    if os.path.isfile(json_output_path):
        logging.warning("JSON output file already exist (%s).\nAborting export.",
                        json_output_path)
        return

    output_dict: Dict[str, Dict] = {}

    # Loop over the figure from the generator and add their dict representation to the output
    # dictionnary.
    for figure in figure_generator():
        output_dict[figure.image_filename] = figure.to_dict()

    with open(json_output_path, 'w') as json_file:
        json.dump(obj=output_dict,
                  fp=json_file,
                  indent=4)


def export_figures_to_detectron_dict(figure_generator: FigureGenerator,
                                     task: str = 'panel_splitting') -> List[dict]:
    """
    Export a set of Figure objects to a dict which is compatible with Facebook Detectron 2.

    Args:
        figure_generator (FigureGenerator): A generator yielding figure objects.
        task (str):                         The task for which to export the figures.

    Returns:
        dataset_dicts (dict): A dict representing the data set.
    """
    if task not in ['panel_splitting', 'label_recog', 'panel_seg']:
        raise ValueError("`task` has to be one of ['panel_splitting', 'label_recog',"\
                         f" 'panel_seg'] but is {task}")

    from detectron2.structures import BoxMode

    dataset_dicts: List[dict] = []

    for index, figure in enumerate(figure_generator()):
        record: Dict[str, Any] = {}

        record['file_name'] = figure.image_path
        record['image_id'] = index
        record['height'] = figure.image_height
        record['width'] = figure.image_width

        objs: List[Dict[str, Any]] = []

        if figure.gt_subfigures is not None:

            for subfigure in figure.gt_subfigures:

                panel = subfigure.panel
                label = subfigure.label

                if task == 'panel_splitting':

                    if panel is None:
                        continue

                    obj: Dict[str, Any] = {
                        'bbox': panel.box,
                        'bbox_mode': BoxMode.XYXY_ABS,
                        'category_id': 0
                    }

                elif task == 'label_recog':

                    # We ensure that, for this task, the labels are valid
                    # (they have been previously checked while loading annotations)
                    if label is None\
                        or label.box is None\
                        or label.text is None\
                        or len(label.text) != 1:
                        continue

                    obj = {
                        'bbox': label.box,
                        'bbox_mode': BoxMode.XYXY_ABS,
                        'category_id': LABEL_CLASS_MAPPING[map_label(label.text)]
                    }

                # panel segmentation task
                else:

                    if panel is None:
                        continue

                    # category_id is artificially set to zero to satisfy the Detectron API.
                    # The actual label (if any) is stored in 'label'.
                    obj = {
                        'panel_bbox': panel.box,
                        'bbox_mode': BoxMode.XYXY_ABS
                    }

                    if label is not None\
                        and label.box is not None\
                        and label.text is not None\
                        and len(label.text) == 1:
                        # If there is no valid label, it won't be considered for training.
                        # TODO: later, we would like to handle >1 length labels
                        obj['label_bbox'] = label.box
                        obj['label'] = LABEL_CLASS_MAPPING[map_label(label.text)]

                objs.append(obj)

            record["annotations"] = objs

        dataset_dicts.append(record)

    return dataset_dicts
