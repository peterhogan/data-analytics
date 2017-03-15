import pafy
from os import environ, path
from pocketsphinx.pocketsphinx import *
from sphinxbase.sphinxbase import *

MODELDIR = "/usr/lib64/python3.4/site-packages/pocketsphinx/model"
DATADIR = "/usr/lib64/python3.4/site-packages/pocketsphinx/test/data"

# grab the url from trending
url = "https://www.youtube.com/watch?v=OaRBPXLgKyg"

video = pafy.new(url)

# print video title and viewcount
print(video.title, video.viewcount)

# Create a decoder with certain model
config = Decoder.default_config()
config.set_string('-hmm', path.join(MODELDIR, 'en-us/en-us'))
config.set_string('-lm', path.join(MODELDIR, 'en-us/en-us.lm.bin'))
config.set_string('-dict', path.join(MODELDIR, 'en-us/cmudict-en-us.dict'))
decoder = Decoder(config)
