import hashlib
import json
import os

def get_files(entry):
  for dirname, dirnames, filenames in os.walk('original_files'):
    for filename in filenames:
      fullpath = os.path.join(dirname, filename)
      contents = open(fullpath, 'rb').read()
      md5 = hashlib.md5(contents).hexdigest()
      if md5 == entry["md5sum"]:
        return fullpath

  # TODO:
  # If not found, then download it from entry["download"]
  # and save it to the "original_files" folder
  # then calculate checksum to make sure it matches entry["md5sum"]
  # if we got a mismatch, print a warning
  # if the download fails, print a warning and return None so that this release is skipped

metadata = json.loads(open("metadata.json").read())
for entry in metadata:
  fullpath = get_files(entry)
  # TODO:
  # create a directory using the md5sum as the dirname and extract the files there
  # find memlist.bin
  # parse memlist and extract resources from the banks
  # run the another world bytecode disassembler


# After we get the source listings of the bytecode for all releases we may perform comparisons between them to figure out their differences.
# We may also build a local git repo with branches for each of the releases, or something like that...
