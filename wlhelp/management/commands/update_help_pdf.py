from ...models import Tribe as TribeModel

from django.core.management.base import BaseCommand, CommandError
from settings import MEDIA_ROOT, WIDELANDS_SVN_DIR, MEDIA_URL

import os
import shutil
from os import path
from widelandslib.tribe import *
from widelandslib.make_flow_diagram import make_graph
from wlhelp.models import Tribe
from glob import glob

class Command(BaseCommand):
    help =\
    """Update the overview pdfs of all tribes in a current checkout"""

    def handle(self, directory = WIDELANDS_SVN_DIR, **kwargs):
        tribes = [d for d in glob("%s/tribes/*" % directory)
                    if os.path.isdir(d)]

        print "updating pdf files for all tribes"

        for t in tribes:
            tribename = os.path.basename(t)
            print "  updating pdf file for tribe ", tribename
            gdir = make_graph(tribename)
            pdffile = path.join(gdir, tribename + ".pdf")
            giffile = path.join(gdir, tribename + ".gif")

            targetdir = path.join(MEDIA_ROOT, "wlhelp", "network_graphs", tribename)

            try:
                os.makedirs(targetdir)
            except OSError:
                pass

            shutil.copy(pdffile, targetdir)
            shutil.copy(giffile, targetdir)

            tribe = Tribe.objects.get(name=tribename)
            if tribe:
                tribe.network_pdf_url = path.normpath("%s/%s/%s" % (MEDIA_URL, targetdir[len(MEDIA_ROOT):], tribename + ".pdf"))
                tribe.network_gif_url = path.normpath("%s/%s/%s" % (MEDIA_URL, targetdir[len(MEDIA_ROOT):], tribename + ".gif"))
                tribe.save()
            else:
                print "Could not set tribe urls"

            shutil.rmtree(gdir)