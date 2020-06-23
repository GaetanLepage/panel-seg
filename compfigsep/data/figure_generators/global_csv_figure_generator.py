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


#########################################
Figure generator handling a csv data set.
"""

import os
import logging
import csv

from ...utils.figure import Panel, Label, SubFigure, Figure
from .figure_generator import FigureGenerator


class GlobalCsvFigureGenerator(FigureGenerator):
    """
    Generator of Figure objects from a csv data set.

    Attributes:
        data_dir (str):         The path to the directory where the image data sets are stored.
        current_index (int):    Index of the currently handled figure. This helps knowing the
                                     "progression" of the data loading process.
        csv_annotation_file_path (str): The path to the csv annotation file.
    """

    def __init__(self, csv_annotation_file_path: str):
        """
        Init function.
        Call the init function of the abstract parent class.

        Args:
            csv_annotation_file_path (str): The path to the csv annotation file.
        """

        self.csv_annotation_file_path = csv_annotation_file_path

        super().__init__()

        if not os.path.isfile(csv_annotation_file_path):
            raise FileNotFoundError("The prediction annotation csv file does not exist :"\
                "\n\t {}".format(csv_annotation_file_path))


    def __call__(self) -> Figure:
        """
        Generator of Figure objects from a single csv annotation file.

        Yields:
            figure (Figure):    Figure objects with annotations.
        """


        with open(self.csv_annotation_file_path, 'r') as csv_annotation_file:
            csv_reader = csv.reader(csv_annotation_file, delimiter=',')

            subfigures = []
            image_path = ''
            figure = None

            image_counter = 0

            for row in csv_reader:

                # New figure
                if not image_path.endswith(row[0]):
                    if figure is not None:
                        figure.gt_subfigures = subfigures
                        yield figure

                        image_counter += 1

                    image_path = row[0]
                    if not os.path.isfile(image_path):
                        image_path = os.path.join('data/', image_path)
                    if not os.path.isfile(image_path):
                        raise FileNotFoundError("The following image file does not exist :"\
                            "\n\t {}".format(image_path))

                    figure = Figure(image_path=image_path,
                                    index=image_counter)
                    # Load image file
                    try:
                        figure.load_image()
                    except FileNotFoundError as exception:
                        logging.error(exception)
                        continue

                    # Create empty list of subfigures.
                    subfigures = []


                # Panel segmentation + panel splitting
                if len(row) == 11:
                    try:
                        # Instanciate Label object
                        label = Label(text=row[10],
                                      box=[int(x) for x in row[6:10]])
                    except ValueError:
                        label = None

                # Panel splitting only
                elif len(row) == 6:
                    label = None
                else:
                    raise ValueError("Row should be of length 6 or 11")

                panel_coordinates = [int(x) for x in row[1:5]]
                panel_class = row[5]
                assert panel_class == 'panel'

                # Instanciate Panel object
                panel = Panel(box=panel_coordinates)

                subfigures.append(SubFigure(panel=panel,
                                            label=label))

            # set subfigures for the last figure
            figure.gt_subfigures = subfigures

            yield figure