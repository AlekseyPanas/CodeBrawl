import traceback
try:
	import main
except Exception as e:
	traceback.print_exc()
	print(e)
	input()
