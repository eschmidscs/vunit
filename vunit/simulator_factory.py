# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2015, Lars Asplund lars.anders.asplund@gmail.com

"""
Create simulator instances
"""

from vunit.modelsim_interface import ModelSimInterface
from vunit.ghdl_interface import GHDLInterface
from os.path import join, exists
import os


class SimulatorFactory(object):
    """
    Create simulator instances
    """

    @staticmethod
    def supported_simulators():
        """
        Return a list of supported simulator classes
        """
        return [ModelSimInterface, GHDLInterface]

    @classmethod
    def available_simulators(cls):
        """
        Return a list of available simulators
        """
        return [simulator_class
                for simulator_class in cls.supported_simulators()
                if simulator_class.is_available()]

    @classmethod
    def select_simulator(cls):
        """
        Select simulator class, either from VUNIT_SIMULATOR environment variable
        or the first available
        """
        environ_name = "VUNIT_SIMULATOR"

        available_simulators = cls.available_simulators()
        name_mapping = {simulator_class.name: simulator_class for simulator_class in cls.supported_simulators()}
        if len(available_simulators) == 0:
            raise RuntimeError("No available simulator detected. "
                               "Simulator executables must be available in PATH environment variable.")

        if environ_name in os.environ:
            simulator_name = os.environ[environ_name]
            if simulator_name not in name_mapping:
                raise RuntimeError(
                    ("Simulator from " + environ_name + " environment variable %r is not supported. "
                     "Supported simulators are %r")
                    % (simulator_name, name_mapping.keys()))
            simulator_class = name_mapping[simulator_name]
        else:
            simulator_class = available_simulators[0]

        return simulator_class

    @classmethod
    def add_arguments(cls, parser):
        """
        Add command line arguments to parser
        """
        cls.select_simulator().add_arguments(parser)

    def __init__(self, args):
        self._args = args
        self._output_path = args.output_path
        self._simulator_class = self.select_simulator()

    @property
    def simulator_name(self):
        return self._simulator_class.name

    @property
    def simulator_output_path(self):
        return join(self._output_path, self.simulator_name)

    def create(self):
        """
        Create new simulator instance
        """
        if not exists(self.simulator_output_path):
            os.makedirs(self.simulator_output_path)

        return self._simulator_class.from_args(self.simulator_output_path,
                                               self._args)