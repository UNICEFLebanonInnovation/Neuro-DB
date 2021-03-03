import os
import tempfile
import subprocess 
import time

from django.conf import settings
from django.http import StreamingHttpResponse

class StreamingConvertedPdf:

    def __init__(self, dock_obj,name, download=True):
        self.doc = dock_obj
        self.name = name
        self.download = download
        self.tmp_path = settings.MEDIA_ROOT + 'tmp/'

    def validate_document(self):
        if not self.name.split('.')[-1] in ('doc', 'docm', 'docx'):
            raise Exception('The input file must have one format from this: doc, docm, docx')

    def check_tmp_folder(self):
        if not os.path.exists(self.tmp_path):
            os.makedirs(self.tmp_path)

    def convert_to_pdf(self):
        self.validate_document()
        self.check_tmp_folder()
        
        with tempfile.NamedTemporaryFile(mode='w+b',prefix=self.tmp_path) as tmp:
            tmp.write(self.doc.read())
            
            os.fchmod(tmp.fileno(), 0777) 
            

            #print(tmp.name)
            tmp.flush()
            os.system("libreoffice --convert-to pdf "+tmp.name+" --outdir "+self.tmp_path)
            #os.system("libreoffice --convert-to pdf "+tmp.name+" --outdir /home/neurodb/Neuro-DB-sub-new-ux/internos/mediatmp")
           
            self.tmp_path = tmp.name + '.pdf'

    def get_file_name(self):
        return self.name.split('.')[0] + '.pdf'

    def stream_content(self):
        self.convert_to_pdf()
        res = StreamingHttpResponse(open(self.tmp_path, 'rb'), content_type='application/pdf')
        if self.download:
            res['Content-Disposition'] = 'attachment; filename="{}"'.format(self.get_file_name())
        return res

    def __del__(self):
        try:
            if os.path.exists(self.tmp_path):
                os.remove(self.tmp_path)
        except IOError:
            print('Error deleting file')


class ConvertFileModelField(StreamingConvertedPdf):

    def get_content(self):
        self.convert_to_pdf()
        return {'path': self.tmp_path, 'name': self.get_file_name()}

    def stream_content(self):
        pass