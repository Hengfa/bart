#    Copyright (C) 2014  Dignity Health
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#    NO CLINICAL USE.  THE SOFTWARE IS NOT INTENDED FOR COMMERCIAL PURPOSES
#    AND SHOULD BE USED ONLY FOR NON-COMMERCIAL RESEARCH PURPOSES.  THE
#    SOFTWARE MAY NOT IN ANY EVENT BE USED FOR ANY CLINICAL OR DIAGNOSTIC
#    PURPOSES.  YOU ACKNOWLEDGE AND AGREE THAT THE SOFTWARE IS NOT INTENDED FOR
#    USE IN ANY HIGH RISK OR STRICT LIABILITY ACTIVITY, INCLUDING BUT NOT
#    LIMITED TO LIFE SUPPORT OR EMERGENCY MEDICAL OPERATIONS OR USES.  LICENSOR
#    MAKES NO WARRANTY AND HAS NOR LIABILITY ARISING FROM ANY USE OF THE
#    SOFTWARE IN ANY HIGH RISK OR STRICT LIABILITY ACTIVITIES.

# Nick Zwart
# 2015Aug22
# from gpi future (external binary encapsulation):
#   This is a set of convenience functions for wrapping external binaries in
#   python.


import os
import tempfile
import subprocess

# gpi
GPI_SHDM_PATH = tempfile.gettempdir()
class stub(object):
    def __init__(self):
        pass
    def warn(self, msg):
        print msg
log = stub()


class File(object):
    '''Hold a filename as a reference to an actual file.  If THIS object
    looses its reference then make sure the associated file is also deleted.
    By default this file will be created in the GPI tmp directory and will be
    named after the node it is called in. The supplied read/writer functions
    can be used to write and retrieve the file information.

    path: /tmp (default GPI tmp dir)
    filename: additional to the nodeid
    suffix: additional to the nodeid (i.e. '.jpg')
    nodeid: node's location in memory (id())
    rfunc: reader function with footprint:
                data = rfunc('filename')
    wfunc: writer function with footprint:
                retcode = wfunc('filename', data)
                retcode: None or 0 for success

    If no names are specified then THIS object id is used.
    '''
    _Extern_File_Handle_Type = True

    def __init__(self, wfunc=None, wdata=None, path=None, filename=None, suffix=None, nodeid=None, rfunc=None, asuffix=[]):

        self._reader = rfunc
        self._writer = wfunc
        self._output_data = wdata # data to be written
        self._additional_suffix = asuffix

        ## build the filepath one step at a time

        self._fullpath = ''
        self._filename = ''
        if nodeid:
            self._filename += str(nodeid)

        if filename:
            if self._filename != '':
                self._filename += '_'
            self._filename += str(filename)

        if suffix:
            self._filename += str(suffix)

        # just use THIS object id if nothing is specified
        if self._filename == '':
            self._filename = str(id(self))

        if path:
            self._fullpath = os.path.join(str(path), self._filename)
        else:
            self._fullpath = os.path.join(GPI_SHDM_PATH, self._filename)

        if os.path.exists(self._fullpath):
            log.warn('The path: \'' + self._fullpath + '\' already exists, continuing...')

    def __str__(self):
        return self._fullpath

    def __del__(self):
        # this may not delete in a timely fashion so direct use of clear() is
        # encouraged.
        if self.fileExists():
            log.warn('The \'File\' object for path: \''+self._fullpath+'\' was not closed before collection.')
            self.clear()

    def additionalSuffix(self, suf=[]):
        # in case the filename is used as a basename, this will allow more
        # files to be searched for removal.  -helpful for formats that require
        # multiple files.
        self._additional_suffix = suf

    def clear(self):
        if os.path.isfile(self._fullpath):
            os.remove(self._fullpath)
        for s in self._additional_suffix:
            if os.path.isfile(self._fullpath + s):
                os.remove(self._fullpath + s)

    def fileExists(self):
        if os.path.isfile(self._fullpath):
            return True
        for s in self._additional_suffix:
            if os.path.isfile(self._fullpath + s):
                return True
        return False

    def close(self):
        self.clear()

    def setReader(self, func):
        self._reader = func

    def setWriter(self, func):
        self._writer = func

    def read(self):
        return self._reader(self._fullpath)

    def data(self):
        return self.read()

    def write(self):
        return self._writer(self._fullpath, self._output_data)

    def isOutput(self):
        # this file is the result of running the command
        if self._reader:
            return True
        return False

    def isInput(self):
        # this file is an input argument to the command
        if self._writer:
            return True
        return False

class IFile(File):
    def __init__(self, wfunc, wdata, suffix=None, asuffix=[]):
        super(IFile, self).__init__(wfunc=wfunc, wdata=wdata, suffix=suffix, asuffix=asuffix)

class OFile(File):
    def __init__(self, rfunc, suffix=None, asuffix=[]):
        super(OFile, self).__init__(rfunc=rfunc, suffix=suffix, asuffix=asuffix)

class Command(object):
    '''This object simplifies the situation where an external program generates
    a file and potentially takes a file as input.  These files need to be
    communicated as commandline arguments, and also need to be read and written
    from GPI.

    in1 = File('.cfl', writer, data)
    out1 = File('.cfl', reader)

    Command(['fft', in1, '-o', out1, '-d1']).run()

    data = out1.read()
    '''

    def __init__(self, cmd=[], warn=True):
        self._cmd = cmd
        self._cmd_str = ' '.join([str(x) for x in cmd])
        self._warn = warn

        # run the command straight away 
        self._retcode = self.run()

    def returnCode(self):
        return self._retcode

    def __str__(self):
        return self._cmd_str
       
    def run(self):

        retcode = 1 # fail

        # write all data to input files
        for x in self._cmd:
            if hasattr(x, '_Extern_File_Handle_Type'):
                if x.isInput():
                    x.write()

        # run the command
        if self._cmd_str:
            retcode = subprocess.call(self._cmd_str, shell=True)

        if self._warn:
            if retcode:
                log.warn("Command(): the commandline argument failed to execute:\n\t" + str(self._cmd_str))

        return retcode
