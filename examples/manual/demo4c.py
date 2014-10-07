# examples/manual/demo4c.py
from __future__ import print_function

import pyxb_123
import po4
import address
import pyxb_123.binding.datatypes as xs

po = po4.purchaseOrder(orderDate=xs.date(1999, 10, 20))
po.shipTo = address.USAddress('Alice Smith', '123 Maple Street', 'Anytown', 'AK', 12341)
po.billTo = address.USAddress('Robert Smith', '8 Oak Avenue', 'Anytown', 'AK', 12341)
                
pyxb_123.RequireValidWhenGenerating(False)
print(po.toxml("utf-8"))
