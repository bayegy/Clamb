import os
import re
import json


class File(object):
    """docstring for File"""

    def __init__(self, prefix=""):
        self._basePath = os.path.dirname(__file__)
        self.prefix = prefix.replace(' ', '_').replace("'", "")
        self._results_file_name = 'results/' + prefix + '_results.txt'
        self._log_file_name = 'results/' + prefix + '_log.txt'
        self._results_file = self.open(self._results_file_name)
        self._log_file = self.open(self._log_file_name)
        self._file_dict = {"results": self._results_file, "log": self._log_file}

    def write_line(self, key, line):
        self._file_dict[key].write(line + '\n', encoding='utf-8')

    def open(self, path: str, mode='a', encoding='utf-8'):
        return open(file=self._basePath + '/' + path, mode=mode, encoding=encoding)

    def get_first_element(self, line):
        return re.sub('\t.*', '', line).strip()

    def get_done_list(self):
        results = []
        log = []
        rf = self.open(self._results_file_name, 'r')
        lf = self.open(self._log_file_name, 'r')
        for l in rf:
            results.append(self.get_first_element(l))
        for l in lf:
            log.append(self.get_first_element(l))
        rf.close()
        lf.close()
        return {"results": results, "log": log}

    def close(self):
        self._results_file.close()
        self._log_file.close()

    def json_config(self, file_name: str):
        return json.load(self._basePath + '/' + 'config/' + file_name)
