import datetime
import time


d = datetime.datetime.utcnow() # <-- get time in UTC
print(d.isoformat("T") + "Z")

