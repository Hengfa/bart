# Author: Nick Zwart
# Date: 2015-10-10
# Copyright (c) 2015 Dignity Health

from __future__ import absolute_import, division, print_function

import os

# gpi, future
import gpi
from bart.gpi.borg import IFilePath, OFilePath, Command

# bart
import bart
base_path = bart.__path__[0] # library base for executables
import bart.python.cfl as cfl

class ExternalNode(gpi.NodeAPI):
    '''Usage: traj [-h] [-r] <output>

    Computes k-space trajectories.

    -x x    readout samples
    -y y    phase encoding lines
    -a a    acceleration
    -t t    turns
    -r  radial
    -G  golden-ratio sampling
    -D  double base angle
    -h  help
    '''

    def initUI(self):
        # Widgets
        self.addWidget('SpinBox', 'readout samples', min=128)
        self.addWidget('SpinBox', 'phase encoding lines', min=32)
        self.addWidget('SpinBox', 'acceleration', min=1)
        self.addWidget('SpinBox', 'turns', min=1)
        self.addWidget('PushButton', 'radial', toggle=True)
        self.addWidget('PushButton', 'golden-ratio sampling', toggle=True)
        self.addWidget('PushButton', 'double base angle', toggle=True)

        # IO Ports
        self.addOutPort('out1', 'NPYarray')

        return 0

    def compute(self):

        x = self.getVal('readout samples')
        y = self.getVal('phase encoding lines')
        a = self.getVal('acceleration')
        t = self.getVal('turns')
        r = self.getVal('radial')
        g = self.getVal('golden-ratio sampling')
        d = self.getVal('double base angle')

        # load up arguments list
        args = [base_path+'/bart traj']
        args += ['-x '+str(x)]
        args += ['-y '+str(y)]
        args += ['-a '+str(a)]
        args += ['-t '+str(t)]
        args += r*['-r']
        args += g*['-G']
        args += d*['-D']

        # setup file for getting data from external command
        out = OFilePath(cfl.readcfl, asuffix=['.cfl','.hdr'])
        args += [out]

        # run commandline
        print(Command(*args))

        self.setData('out1', out.data())
        out.close()

        return 0
