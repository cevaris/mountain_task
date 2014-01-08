#!/usr/bin/env python
#!/bin/env python

import random
import string
# GeoNameId,Name,Country,Latitude,Longitude,Altitude (m)
# 5885171,Angel Peak,CA,58.48553,-124.85859,6858


def random_alpha(N):
  return ''.join(random.choice(string.ascii_lowercase) for x in range(N))

def generate():


  with open('mountains-1MM.txt', 'w') as writer:
    writer.write("GeoNameId,Name,Country,Latitude,Longitude,Altitude (m)\n")
    for i in xrange(1,100):
      writer.write("%d," % (random.randint(1,2000000) + 5000000))
      writer.write("%s," % (random_alpha(random.randint(4,10)).capitalize()+' '+random_alpha(random.randint(4,10)).capitalize()))
      writer.write("%s," % (random_alpha(2).upper()))
      writer.write("%0.6f," % (random.uniform(-180.0, 180.0)))
      writer.write("%0.6f," % (random.uniform(-180.0, 180.0)))

      if random.random() >= 0.15:
        writer.write("%d" % (random.randint(1,3000) + 1000))
      else:
        writer.write("null")

      writer.write("\n")




generate()