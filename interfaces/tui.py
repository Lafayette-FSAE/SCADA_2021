#!/usr/bin/python3
import sys, os

# scada_path = os.environ['SCADA_PATH']
scada_path = '/usr/etc/scada'
config_path = '/usr/etc/scada/config'

sys.path.append(scada_path)
sys.path.append(config_path)

from blessed import Terminal
term = Terminal()

import config
import redis
import time

data = redis.Redis(host='localhost', port=6379, db=0)

columns = config.get('Display')

def print_column(data, label, x=0, y=0):
	
	print(term.move_y((term.height // 2) - len(data) // 2 ))

	col = ''

	col += term.move_x(x)
	col += term.bold_underline(label)
	col += term.move_down(1)

	for name, value in data:
		col += term.move_x(x)
		col += '{}'.format(name)
		col += term.move_x(x + 20)
		col += '{}'.format(value)
		col += term.move_down(1)
	print(col)

def update():
	print(term.clear())

	motor_data = []

	for key in Motor:
		target = Motor.get(key).get('data_target')
		value = data.get(target)
		value = str(value)
		motor_data.append((key, value))

	print_column(motor_data, 'MOTOR:', 10, 0)

	tsi_data = []

	for key in TSI:
		target = TSI.get(key).get('data_target')
		value = data.get(target)

		if value == None:
			value = '--'

		try:
			value_float = float(value)
			value_float = round(value_float, 2)
			value = value_float
		except:
			pass

		value = str(value)
		value = value.replace("b'", "")
		value = value.replace("'", "")
		tsi_data.append((key, value))


	print_column(tsi_data, 'TSI:', 50, 0)

#while True:
#update()
#time.sleep(0.5)
