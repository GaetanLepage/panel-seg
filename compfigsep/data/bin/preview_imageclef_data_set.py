#!/usr/bin/env python3

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


################################################################################################
Script to visualize the ImageCLEF data set by displaying the images along with the corresponding
bounding boxes.
"""

import sys
import os
from argparse import ArgumentParser, Namespace

from typing import List

from compfigsep.data.figure_generators import ImageClefXmlFigureGenerator
from compfigsep.data.figure_viewer import add_viewer_args, view_data_set

sys.path.append('.')


def parse_args(args: List[str]) -> Namespace:
    """
    Parse the arguments from the command line.

    Args:
        args (List[str]):   The arguments from the command line call.

    Returns:
        namespace (Namespace):  Populated namespace.
    """
    parser: ArgumentParser = ArgumentParser(
        description="Preview all the figures from an ImageCLEF data set.")

    parser.add_argument('--annotation_xml',
                        help="The path to the xml annotation file.",
                        default="data/ImageCLEF/test/FigureSeparationTest2016GT.xml",
                        type=str)

    parser.add_argument('--image_directory_path',
                        help="The path to the directory where the images are stored.",
                        default="data/ImageCLEF/test/FigureSeparationTest2016/",
                        type=str)

    add_viewer_args(parser)

    return parser.parse_args(args)


def main(args: List[str] = None) -> None:
    """
    Launch previsualization of ImageCLEF data set.

    Args:
        args (List[str]):   Arguments from the command line.
    """

    # Parse arguments.
    if args is None:
        args = sys.argv[1:]
    parsed_args: Namespace = parse_args(args)

    # Create the figure generator handling ImageCLEF xml annotation files.
    figure_generator: ImageClefXmlFigureGenerator = ImageClefXmlFigureGenerator(
        xml_annotation_file_path=parsed_args.annotation_xml,
        image_directory_path=parsed_args.image_directory_path)

    # Preview the data set.
    view_data_set(figure_generator=figure_generator,
                  mode=parsed_args.mode,
                  save_preview=parsed_args.save_preview,
                  preview_folder=os.path.join(parsed_args.image_directory_path, "preview"),
                  delay=parsed_args.delay,
                  window_name="ImageCLEF data preview")


if __name__ == '__main__':
    main()
