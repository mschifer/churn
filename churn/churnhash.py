import base64
import os.path

class ChurnHashError(Exception):
    def __init__(self, msg):
        self.value = msg
    def __str__(self):
        return repr(self.value)


class PathHash(object):
    '''
    Just a hash of file paths and churn data associated with that path
    '''
    def __init__(self):
        self.hash = {}

    def add_entry(self, file_path, lines_changed):
        if file_path == '':
            raise ChurnHashError("Empty File path being added to FileHash")

        # Note we base64 encode the path so that two files with the same name
        # but different paths will not match could use the file path but then
        # the keys get really unwieldy
        encodedpath = base64.b64encode(file_path)
        if encodedpath in self.hash:
            self.hash[encodedpath]['lines_changed'] += lines_changed
        else:
            self.hash[encodedpath] = {}
            self.hash[encodedpath]['file'] = file_path
            self.hash[encodedpath]['lines_changed'] = lines_changed

    def get_entry(self, file_path):
        encodedpath = base64.b64encode(file_path)
        if encodedpath not in self.hash:
            raise ChurnHashError("%s not found in FileHash" % file_path)
        return self.hash[encodedpath]['lines_changed']


class ChurnHash(object):
    '''
    A hash of directory names and associated churn metrics which also splits
    out the files and hashes file names and each file's individual churn metrics
    as well.
    '''
    def __init__(self):
        self.hash = PathHash()

    def add_file_path(self, file_path, lines_changed):
        # This makes the assumption that it is called with fully specified files
        # with a common root and unix style ('/') paths
        if file_path == '':
            raise ChurnHashError("Empty File path used in ChurnHash add file")
        for pathsnippet in self._path_generator(file_path):
            self.hash.add_entry(pathsnippet, lines_changed)

    def get_churn(self, file_path):
        return self.hash.get_entry(file_path)

    def _path_generator(self, file_path):
        f = file_path
        while(f != ''):
            yield f
            # Replace f with the path minus its last element
            f = os.path.split(f)[0]
            # Handle the case where path starts with a '/'
            if f == '/':
                f = ''

