from pathlib import Path

from launch import Substitution
from launch import SomeSubstitutionsType
from launch.utilities import normalize_to_list_of_substitutions
from launch.utilities import perform_substitutions


class ReadFileSubstitution(Substitution):

    def __init__(self, filepath: SomeSubstitutionsType):
        self.__filepath = 