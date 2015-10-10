# GPI (v0.5.0-n1) auto-generated library file.
#
# FILE: /Users/nick/gpi/nick/default/GPI/MyNode_GPI.py
#
# For node API examples (i.e. widgets and ports) look at the
# core.interfaces.Template node.

import os

# gpi, future
import gpi
from bart.python.ebe import IFile, OFile, Command

# bart
import bart
base_path = bart.__path__[0] # library base for executables
import bart.python.cfl as cfl

class ExternalNode(gpi.NodeAPI):
    '''Usage svd: [-e] <input> <U> <S> <VH>
    
    Compute singular-value-decomposition (SVD).
    '''

    def initUI(self):
        # Widgets
        self.addWidget('PushButton', 'SVD Econ', toggle=True)

        # IO Ports
        self.addInPort('input', 'NPYarray', obligation=gpi.REQUIRED)
        self.addOutPort('U', 'NPYarray')
        self.addOutPort('S', 'NPYarray')
        self.addOutPort('VH', 'NPYarray')

        return 0

    def compute(self):

        e = self.getVal('SVD Econ')
        inp = self.getData('input')

        # load up arguments list
        args = [base_path+'/svd']
        if e:
            args += ['-e']

        # setup file for passing data to external command
        in1 = IFile(cfl.writecfl, inp, asuffix=['.cfl','.hdr'])
        args += [in1]

        # setup file for getting data from external command
        out1 = OFile(cfl.readcfl, asuffix=['.cfl','.hdr'])
        args += [out1]
        out2 = OFile(cfl.readcfl, asuffix=['.cfl','.hdr'])
        args += [out2]
        out3 = OFile(cfl.readcfl, asuffix=['.cfl','.hdr'])
        args += [out3]

        # run commandline
        print Command(args)

        self.setData('U', out1.data())
        self.setData('S', out2.data())
        self.setData('VH', out3.data())
        out1.close()
        out2.close()
        out3.close()

        return 0