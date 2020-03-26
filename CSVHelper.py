from BaseObject import BaseObject
#import datetime
#from FileHelper import FileHelper
import csv
#import os
#from TempFileName import TempFileName


class CSVHelper(BaseObject):

    def __init__(self,csv_file=None):
        super().__init__()
        self._file = csv_file
        self.log(f"CSVHelper file:{self._file}")
        self.log("CSVHelper initialised")

    @property
    def out_file(self):
        if os.path.exists(self._file):
            return self._file
        else:
            return None

    # def write_rows_to_csv(self, rows):
    #     if self._out_file:
    #         with open(self._out_file,'wb') as csvfile:
    #             writer = csv.writer(csvfile,delimiter=',')
    #             for row in rows:
    #                 writer.writerow(row)
    #     return self.out_file

    # def clean_up_temp_csvs(self):
    #     # for python 2.7 - use glob for 3
    #     self.log("Cleaning up temp csvs")
    #     FileHelper().remove_all_temp_files("csv")

    def reader(self, delim):
        with open(self._file, 'r') as csv_file:
            reader = csv.reader(csv_file, delimiter=str(delim))
            for row in reader:
                yield row

    def dic_reader(self, delim):
        with open(self._file, 'r') as csv_file:
            reader = csv.DictReader(csv_file, delimiter=str(delim))
            for row in reader:
                yield row

# if __name__ == "__main__":
#     pass
