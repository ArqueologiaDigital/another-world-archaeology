import hashlib
import json
import os
import enum

class ResourceType(enum.IntEnum):
  SOUND = 0
  MUSIC = 1
  POLY_ANIM = 2
  PALETTE = 3
  BYTECODE = 4
  POLY_CINEMATIC = 5
  UNKNOWN = 6


class Bank():
  def __init__(self, dataDir):
    self._dataDir = dataDir

  def read(self, me):
    bankName = "bank%02x" % me["bankId"]
    f = open(os.path.join(self._dataDir, bankName), "rb")
    f.seek(me["bankOffset"])

    # Depending if the resource is packed or not we
    # can read directly or unpack it.
    if me["packedSize"] == me["size"]:
      return f.read(me["packedSize"])

    else:
      self.buf = list(f.read(me["packedSize"]))
      self.buf.extend([0] * (me["size"]-me["packedSize"]))
      self._iBuf = me["packedSize"] - 4
      print(len(self.buf))
      return self.unpack()


  def decUnk1(self, numChunks, addCount):
    count = self.getCode(numChunks) + addCount + 1
    # debug(DBG_BANK, "Bank::decUnk1(%d, %d) count=%d", numChunks, addCount, count)
    self.datasize -= count
    while count:
      count -= 1
      assert(self._oBuf >= self._iBuf and self._oBuf >= 0)
      self.buf[self._oBuf] = self.getCode(8)
      self._oBuf -= 1

  def decUnk2(self, numChunks):
    i = self.getCode(numChunks)
    count = self.size + 1
    # debug(DBG_BANK, "Bank::decUnk2(%d) i=%d count=%d", numChunks, i, count)
    self.datasize -= count
    while count:
      count -= 1
      assert(self._oBuf >= self._iBuf and self._oBuf >= 0)
      self.buf[self._oBuf] = self.buf[self._oBuf + i]
      self._oBuf -= 1


  def READ_BE_UINT32(self, i):
    return self.buf[i] << 24 | self.buf[i+1] << 16 | self.buf[i+2] << 8 | self.buf[i+3]

  def unpack(self):
    self.crc = 0
    self.size = 0
    self.datasize = self.READ_BE_UINT32(self._iBuf); self._iBuf -= 4
    self._oBuf = self.datasize - 1
    self.crc = self.READ_BE_UINT32(self._iBuf); self._iBuf -= 4
    self.chk = self.READ_BE_UINT32(self._iBuf); self._iBuf -= 4
    self.crc ^= self.chk
    while self.datasize > 0:
      if not self.nextChunk():
        self.size = 1
        if not self.nextChunk():
          self.decUnk1(3, 0)
        else:
          self.decUnk2(8)
      else:
        c = self.getCode(2);
        if c == 3:
          self.decUnk1(8, 8)
        else:
          if c < 2:
            self.size = c + 2
            self.decUnk2(c + 9)
          else:
            self.size = self.getCode(8)
            self.decUnk2(12)

    if self.crc != 0:
      #raise
      return None

    return bytes(self.buf)


  def getCode(self, numChunks):
    c = 0
    while numChunks:
      numChunks -= 1
      c <<= 1
      if self.nextChunk():
        c |= 1
    return c

  def nextChunk(self):
    CF = self.rcr(False)
    if self.chk == 0:
      assert(self._iBuf >= 0)
      self.chk = self.READ_BE_UINT32(self._iBuf); self._iBuf -= 4
      self.crc ^= self.chk
      CF = self.rcr(True)
    return CF

  def rcr(self, CF):
    rCF = self.chk & 1
    self.chk >>= 1
    if (CF): self.chk |= 0x80000000
    return rCF


def ord2(v):
  return v[0] << 8 | v[1]


def ord4(v):
  return v[0] << 24 | v[1] << 16 | v[2] << 8 | v[3]


def read_mem_entries(path):
  memList = []
  f = open(os.path.join(path, "memlist.bin"), "rb")
  state = 0
  while True:
    entry = {}
    entry["state"] = ord(f.read(1))
    entry["type"] = ord(f.read(1))
    f.read(2) # skip (bufPtr)
    f.read(2) # skip (unk4)
    entry["rankNum"] = ord(f.read(1))
    entry["bankId"] = ord(f.read(1))
    entry["bankOffset"] = ord4(f.read(4))
    f.read(2) # skip (unkC)
    entry["packedSize"] = ord2(f.read(2))
    f.read(2) # skip (unk10)
    entry["size"] = ord2(f.read(2))
    if entry["state"] == 0:
      memList.append(entry)
    else:
      break
  return memList


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
for md in metadata:
  fullpath = get_files(md)
  # TODO:
  # create a directory using the md5sum as the dirname and extract the files there
  if 0:
    os.mkdir(md["md5sum"])
    os.mkdir(md["md5sum"] + "/bin")
    os.mkdir(md["md5sum"] + "/original")
    os.mkdir(md["md5sum"] + "/disasm")

  # parse memlist and extract resources from the banks
  path = os.path.join(md["md5sum"], "original", md["rootdir"])
  memlist = read_mem_entries(path)
  resource_count = 0
  for entry in memlist:
    print(entry)
    bank = Bank(path)
    filename = "{}-{}.bin".format(hex(resource_count),
                                  ResourceType(entry["type"]).name)
    filepath = os.path.join(md["md5sum"], "bin", filename)
    open(filepath, "wb").write(bank.read(entry))
    resource_count += 1
      
    if entry["type"] == ResourceType.BYTECODE:
      # run the another world bytecode disassembler
      pass


# After we get the source listings of the bytecode for all releases we may perform comparisons between them to figure out their differences.
# We may also build a local git repo with branches for each of the releases, or something like that...
