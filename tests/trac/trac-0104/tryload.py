# -*- coding: utf-8 -*-
from __future__ import print_function
import logging
if __name__ == '__main__':
    logging.basicConfig()
_log = logging.getLogger(__name__)
import sys
sys.path.append("modules")

import com.example.pyxb_123.ModelA.AA
import com.example.pyxb_123.ModelB.BB

print('Modules loaded')
sys.exit(0)
