meta:
  id: ljc
  file-extension: ljc
  imports:
    - /common/vlq_base128_le

seq:
  - id: header
    type: dump_header
  - id: proto
    type: dump_prototype
  - id: tail
    size-eos: true

types:
  dump_header:
    seq:
      - id: magic
        contents: [0x1B, 0x4C, 0x4A]
      - id: version
        type: u1
      - id: flags
        type: vlq_base128_le
      # if BCDUMP_F_STRIP is not set then we can read debugname
      - id: debugname
        type: ule_string
        if: (flags.value & 2) == 0
  
  ule_string:
    seq:
      - id: length
        type: vlq_base128_le
      - id: string
        type: str
        encoding: UTF-8
        size: length.value
  
  dump_prototype:
    seq:
      - id: length
        type: vlq_base128_le
      - id: pdata
        type: prototype_data
        
  prototype_data:
    seq:
      - id: phead
        type: prototype_head
  
  prototype_head:
    seq:
      - id: flags
        type: u1
      - id: numparams
        type: u1
      - id: framesize
        type: u1
      - id: numuv
        type: u1
      - id: numkgc
        type: vlq_base128_le
      - id: numkn
        type: vlq_base128_le
      - id: numbc
        type: vlq_base128_le
      # - id: kek
      #   type: u1
      #   if: flags & 2 == 0
      # TODO: add support to [debuglenU [firstlineU numlineU]]
      
enums:
  bcdump_f:
      1:  be
      2:  strip
      4:  ffi