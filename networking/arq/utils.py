import random
def register_event(event_simulator, event):
	event_simulator.insert(reverse_bisect(event_simulator, event['time']), event)

def purge_time_out(event_simulator):
	for event in event_simulator:
		if event['type'] == 'timeout':
			event_simulator.remove(event)

def reverse_bisect(l, x, lo=0, hi=None):
	if hi is None:
		hi = len(l)
	while lo < hi:
		mid = (lo+hi)//2
		if x > l[mid]['time']:
			hi = mid
		else:
			lo = mid+1
	return lo

def count_error_bit(L, BER):
	count_error = 0
	for i in range(L):
		x = random.random()
		if x <= BER:
			count_error = count_error + 1
	return count_error