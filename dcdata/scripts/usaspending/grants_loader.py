#from django.db import connections
from faads import FIELDS, CALCULATED_FIELDS
import os.path

class Loader():
    def fields(self):
        return [ x[0] for x in FIELDS ] + [ x[0] for x in CALCULATED_FIELDS ]

    def print_sql(self, infile):
        table = 'grants_grant'
        print self.sql_template_postgres(infile, table, self.fields())

    def sql_template_postgres(self, file_, table, fields):
        return """
            \\copy {1} \
            ({2}) \
            FROM '{0}' \
            DELIMITER '|' \
            CSV QUOTE '"' \
            NULL 'NULL' \
        """.format(os.path.relpath(file_), table, ', '.join(fields))
        # relpath is for the sake of tests passing in different environments
