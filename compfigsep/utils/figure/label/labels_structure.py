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

Collaborators:  Niccolò Marini (niccolo.marini@hevs.ch)
                Stefano Marchesin (stefano.marchesin@unipd.it)


###############################
Defines a structure for labels.
"""

from __future__ import annotations

import logging
import operator
from enum import Enum
from typing import List

from .utils import (is_lower_char,
                    is_upper_char,
                    UC_ROMAN,
                    LC_ROMAN,
                    UC_ROMAN_TO_INT,
                    LC_ROMAN_TO_INT)


class LabelStructureEnum(Enum):
    """
    Enum representing the category of labels for a figure.
    """

    # The image contain no labels
    NONE = 0

    # 1, 2, 3...
    NUMERICAL = 1

    # A, B, C
    LATIN_UC = 2

    # a, b, c
    LATIN_LC = 3

    # I, II, III
    ROMAN_UC = 4

    # i, ii, iii
    ROMAN_LC = 5

    OTHER = 6


class LabelStructure:
    """
    Class representing the label structure for a compound figure.
    With only two information (the type of labels and the number) it is possible
    to qualify the label structure of a figure.

    Attributes:
        labels_type (LabelStructureEnum):   The type of label structure.
        num_labels (int):                   The number of labels.
    """

    def __init__(self,
                 labels_type: LabelStructureEnum,
                 num_labels: int) -> None:
        """
        Args:
            labels_type (LabelStructureEnum):   The type of labels.
            num_labels (int):                   The number of labels.
        """

        self.labels_type = labels_type
        self.num_labels = num_labels


    @classmethod
    def from_labels_list(cls,
                         labels_list: List[str]) -> LabelStructure:
        """
        Create a LabelStructure object from a list of labels.

        Args:
            labels_list (List[str]):    A list of labels (text).

        Returns:
            label_structure (LabelStructure):   An instance of the corresponding LabelStructure
                                                    object.
        """
        # Case where there are no named labels.
        if labels_list == ['_'] * len(labels_list):
            return cls(labels_type=LabelStructureEnum.NONE,
                       num_labels=len(labels_list))


        # "Histogram" of the label types.
        similarity_list = {structure: 0 for structure in LabelStructureEnum}

        for label in labels_list:

            # Test if label is a latin character (single letter by definition).
            if len(label) == 1:

                # a, b, c...
                if is_lower_char(char=label):
                    similarity_list[LabelStructureEnum.LATIN_LC] += 1
                    continue

                # A, B, C...
                if is_upper_char(char=label):
                    similarity_list[LabelStructureEnum.LATIN_UC] += 1
                    continue

            # Test if label is an int.
            # 1, 2, 3...
            try:
                int(label)
                similarity_list[LabelStructureEnum.NUMERICAL] += 1
                continue
            except ValueError:
                pass

            # Test if label is a roman character (i, ii, iii...).
            # --> Can be several characters long.
            if label in LC_ROMAN_TO_INT.keys():
                similarity_list[LabelStructureEnum.ROMAN_LC] += 1
                continue

            # I, II, III...
            if label in UC_ROMAN_TO_INT.keys():
                similarity_list[LabelStructureEnum.ROMAN_UC] += 1
                continue

            # Default case
            logging.warning("Label %s does not belong to a default type.",
                            label)
            similarity_list[LabelStructureEnum.OTHER] += 1

        max_pos = max(similarity_list.items(),
                      key=operator.itemgetter(1)
                      )[0]

        return cls(labels_type=LabelStructureEnum(max_pos),
                   num_labels=len(labels_list))


    def get_core_label_list(self) -> List[str]:
        """
        Returns:
            core_label_list (List[str]):    The list of labels corresponding to this
                                                LabelStructure.
        """
        output_list: List[str] = []

        if self.labels_type is None:
            output_list = []

        elif self.labels_type == LabelStructureEnum.NUMERICAL:
            output_list = [str(i) for i in range(self.num_labels)]

        elif self.labels_type == LabelStructureEnum.LATIN_UC:
            output_list = [chr(65 + i) for i in range(self.num_labels)]

        elif self.labels_type == LabelStructureEnum.LATIN_LC:
            output_list = [chr(97 + i) for i in range(self.num_labels)]

        elif self.labels_type == LabelStructureEnum.ROMAN_UC:
            output_list = UC_ROMAN[:self.num_labels]

        elif self.labels_type == LabelStructureEnum.ROMAN_LC:
            output_list = LC_ROMAN[:self.num_labels]

        # Default case
        else:
            assert self.labels_type in (LabelStructureEnum.OTHER, LabelStructureEnum.NONE)
            output_list = ['_'] * self.num_labels

        return output_list


    def __eq__(self, other: object) -> bool:

        if isinstance(other, LabelStructure):
            return self.labels_type == other.labels_type and self.num_labels == other.num_labels

        return False

    def __str__(self) -> str:
        string = str(self.labels_type)
        string += f" | number of labels : {self.num_labels}"

        return string
