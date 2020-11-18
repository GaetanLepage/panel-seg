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


##########################
Panel segmentation module.
Separate compound figures into multiple panels.

Input: Compound (i.e. multi-panel) figure/image.

Output: A list of sub-figures including :
    * Panel location
"""

from .load_datasets import *
from .evaluator import *

__all__ = [k for k in globals().keys() if not k.startswith("_")]
