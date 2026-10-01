# This script shows a simple example of how to use the API, including changing variables from their defaults.

from datetime import datetime
from wrapper import api

data = api(start_date=datetime(2022, 9, 24, 6), end_date=datetime(2022, 9, 26, 6), station='TPA', report_type=3, tmpc=False, tmpf=True, dwpf=True, dwpc=False)
print(data.obs)