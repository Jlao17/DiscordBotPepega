import time

seconds = 1673000


if int(time.time()) - seconds > 43200:
    print("12 hours has been passed")
else:
    print("Ignoring")