import csv, codecs, cStringIO

from django.http import HttpResponse

# also include UnicodeWriter from the Python docs http://docs.python.org/library/csv.html


class UTF8Recoder:
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")


class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


class ExportModel(object):

    @staticmethod
    def as_csv(meta):

        with open(meta['file'], 'wb') as f:
            writer = UnicodeWriter(f, encoding='utf-8')
            writer.writerow(meta['header'])
            for obj in meta['queryset']:
                row = [unicode(getattr(obj, field)) for field in meta['fields']]
                writer.writerow(row)
            path = f.name
        return path


def get_model_as_csv_file_response(meta, content_type, filename):
    """
    Call this function from your model admin
    """
    with open(ExportModel.as_csv(meta), 'r') as f:
        response = HttpResponse(f.read(), content_type=content_type)
        # response['Content-Disposition'] = 'attachment; filename=Extraction.csv;'
        response['Content-Disposition'] = 'attachment; filename=%s;' % filename
    return response
