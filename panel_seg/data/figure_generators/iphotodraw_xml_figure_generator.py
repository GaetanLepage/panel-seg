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


######################################################
Figure generator handling the PanelSeg (Zou) data set.
"""

import os
import sys
import logging

from ...utils.figure.figure import Figure
from .figure_generator import FigureGenerator


class IphotodrawXmlFigureGenerator(FigureGenerator):
    """
    Generator of Figure objects from iPhotoDraw xml annotations (PanelSeg data set).
    The input files can be provided either from a csv list or from the path to the directory
    where the image files are stored.

    Attributes:
        data_dir (str):             The path to the directory where the image data sets are
                                        stored.
        current_index (int):        Index of the currently handled figure. This helps knowing the
                                        "progression" of the data loading process.
        image_paths (List[str]):    List of the image paths.
    """

    def __init__(self,
                 eval_list_txt: str = None,
                 image_directory_path: str = None):
        """
        Init for IphotodrawXmlFigureGenerator.

        Args:
            eval_list_txt (str):            The path of the list of figures which annotations
                                                have to be loaded.
            image_directory_path (str):     The path of the directory where the images are stored
        """
        # Call base class method.
        super().__init__()

        # Check argument consistency
        if eval_list_txt is not None and image_directory_path is not None:
            logging.error("Both `eval_list_txt` and `input_directory` options cannot be"\
                          " simultaneously True.")
            sys.exit(1)

        # If a list of image files was provided, read it and store the image files.
        if eval_list_txt is not None:

            # Read list of image files
            with open(eval_list_txt, 'r') as eval_list_file:
                eval_list_lines = eval_list_file.read().splitlines()

            self.image_paths = [line if os.path.isfile(line)
                                else os.path.join('data/', line)
                                for line in eval_list_lines]

        # If a path was provided, list the image files in this directory.
        elif image_directory_path is not None:

            self.image_paths = [f for f in os.listdir(image_directory_path)
                                if f.endswith('.jpg') and os.path.isfile(
                                    os.path.join(image_directory_path, f))
                                ]

        else:
            logging.error("Either one of `eval_list_txt` and `input_directory` options"\
                          " has to be set.")
            sys.exit(1)



    def __call__(self) -> Figure:
        """
        'Generator' method yielding annotated figures from the PanelSeg data set.

        Yields:
            figure (Figure): Figure objects with annotations.
        """

        # Looping over the list of image paths.
        for image_index, image_path in enumerate(self.image_paths):

            # TODO maybe set up a verbose mode
            # print('Processing Image {}/{} : {}'.format(image_index + 1,
                                                       # num_images,
                                                       # image_path))

            # Create figure object.
            figure = Figure(image_path=image_path,
                            index=image_index)

            # Load image file.
            try:
                figure.load_image()
            except FileNotFoundError as exception:
                logging.error(exception)
                continue

            # Load annotation file.
            xml_path = os.path.join(figure.image_path.replace('.jpg', '_data.xml'))
            # Load figure annotations.
            figure.load_annotation_from_iphotodraw(xml_path)

            yield figure
