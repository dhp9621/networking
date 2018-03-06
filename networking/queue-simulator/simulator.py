import random
import math
import statistics
from operator import itemgetter
import bisect
import collections
import csv

def generate_event_list(max_time, parameter):
	time_list = list()
	time = 0
	while time < max_time:
		time = generate_rv(parameter) + time
		time_list.append(time)
	return time_list

def generate_rv(parameter):
	u = random.random()
	rv = (-1/parameter)*math.log(1-u)
	return rv

def generate_1000_rv():
	result = [generate_rv(75) for i in range(1000)]
	return statistics.mean(result), statistics.variance(result)

def mm1_queue(T, L, C, P):
	"""
		T: Simulation time
		L: Average length of packet
		C: Transmission rate
		P: Utilization of the queue
	"""
	#Compute lambda and alpha
	LAMBDA = P*C/L
	ALPHA = LAMBDA * 4
	#Generate events
	observer_events = generate_event_list(T, ALPHA)
	arrival_events = generate_event_list(T, LAMBDA)
	packets_length = [generate_rv(1/L) for event in arrival_events]
	service_time = [length/C for length in packets_length]
	#Calculate departure time
	departure_events = [None] * len(arrival_events)
	departure_events[0] = arrival_events[0] + service_time[0]
	for i in range(1,len(arrival_events)):
		if (departure_events[i-1] > arrival_events[i]):
			departure_events[i] = departure_events[i-1] + service_time[i]
		else:
			departure_events[i] = arrival_events[i] + service_time[i]
	#Put events in event simulator
	observer_events_with_key = [(event, 'observer') for event in observer_events]
	arrival_events_with_key = [(event, 'arrival') for event in arrival_events]
	departure_events_with_key = [(event, 'departure') for event in departure_events]
	event_simulator = collections.deque(sorted(observer_events_with_key + arrival_events_with_key + departure_events_with_key, key=itemgetter(0)))
	#Calculate metrics
	n_idle = 0 
	n_queue = 0 
	queue_at_observed_times = []
	while event_simulator:
		event = event_simulator.popleft()
		if event[1] == 'arrival':
			n_queue = n_queue + 1
		elif event[1] == 'departure':
			n_queue = n_queue - 1
		else:
			queue_at_observed_times.append(n_queue)
			if (n_queue == 0):
				n_idle = n_idle + 1
	#Result
	e_n = statistics.mean(queue_at_observed_times)
	p_idle = n_idle/len(observer_events)
	return e_n, p_idle

def mm1k_queue(T, L, C, P, K):
	"""
		T: Simulation time
		L: Average length of packet
		C: Transmission rate
		P: Utilization of the queue
		K: Queue size
	"""
	#Compute lambda and alpha
	LAMBDA = P*C/L
	ALPHA = LAMBDA * 4
	#Generate events
	observer_events = generate_event_list(T, ALPHA)
	arrival_events = generate_event_list(T, LAMBDA)
	packets_length = [generate_rv(1/L) for event in arrival_events]
	service_time = [length/C for length in packets_length]
	#Put events in event simulator
	observer_events_with_key = [(event, 'observer') for event in observer_events]
	arrival_events_with_key = [(event, 'arrival') for event in arrival_events]
	event_simulator = sorted(observer_events_with_key + arrival_events_with_key, key=itemgetter(0), reverse = True)
	#Calculate metrics
	n_a = 0 
	n_d = 0 
	n_idle = 0 
	n_queue = 0 
	n_dropped = 0
	queue_at_observed_times = []
	departure_events = [0]
	
	while event_simulator:
		event = event_simulator.pop()
		if event[1] == 'arrival':	
			if n_queue < K:
				n_a = n_a + 1
				n_queue = n_queue + 1
				service_time = generate_rv(1/L)/C
				if event[0] >= departure_events[-1]:
					departure_time = event[0] + service_time
				else:
					departure_time = departure_events[-1] + service_time
				departure_events.append(departure_time)
				event_simulator.insert(reverse_bisect(event_simulator, departure_time), (departure_time, 'departure'))
			else:
				n_dropped = n_dropped + 1
		elif event[1] == 'departure':
			n_d = n_d + 1
			n_queue = n_queue - 1
		else: 
			queue_at_observed_times.append(n_queue)
			if (n_queue == 0):
				n_idle = n_idle + 1


	e_n = statistics.mean(queue_at_observed_times)
	p_idle = n_idle/len(observer_events)
	p_loss = n_dropped/len(arrival_events)
	return e_n, p_loss

def reverse_bisect(l, x, lo=0, hi=None):
	if hi is None:
		hi = len(l)
	while lo < hi:
		mid = (lo+hi)//2
		if x > l[mid][0]: 
			hi = mid
		else: 
			lo = mid+1
	return lo

def mm1_simulation():
	T = 10000
	L = 12000
	C = 1000000
	p = 0.25
	print("Result of mm1_simulation: ")
	with open('mm1.csv', 'w', newline='') as csvfile:
		csv_writer = csv.writer(csvfile)
		while p < 0.96:
			e_n, p_idle = mm1_queue(T, L, C, p)
			csv_writer.writerow([p, e_n, p_idle])
			print("p: %0.2f, e_n: %0.8f , p_idle: %0.8f " % (p, e_n, p_idle))
			p = p + 0.1

		p = 1.2
		e_n, p_idle = mm1_queue(T, L, C, p)
		csv_writer.writerow([p, e_n, p_idle])
		print("p: 1.2, e_n: %0.8f , p_idle: %0.8f " % (e_n, p_idle))

def mm1k_simulation():
	T = 10000
	L = 12000
	C = 1000000
	p = 0.5
	K_list = [5, 10, 40]
	print("Result of mm1k_simulation: ")

	with open('mm1k_en.csv', 'w', newline='') as csvfile:
		csv_writer = csv.writer(csvfile)
		while p < 1.6:
			for K in K_list:
				e_n, p_loss = mm1k_queue(T, L, C, p, K)
				csv_writer.writerow([p, K, e_n])
				print("p: %0.2f, K:%1d, e_n: %0.8f" % (p, K, e_n))
			p = p + 0.1

	p = 0.4
	with open('mm1k_p_loss.csv', 'w', newline='') as csvfile:
		csv_writer = csv.writer(csvfile)
		while p < 10.1:
			for K in K_list:
				e_n, p_loss = mm1k_queue(T, L, C, p, K)
				csv_writer.writerow([p, K, p_loss])
				print("p: %0.2f, K:%1d, p_loss: %0.8f" % (p, K, p_loss))
			if p < 2:
				p = p + 0.1
			elif p >= 5: 
				p = p + 0.4
			else:
				p = p + 0.2

mm1_simulation()
mm1k_simulation()
#print(generate_1000_rv())















