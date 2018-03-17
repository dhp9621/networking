from utils import *

def abp_nak(C, L, H, TAU, BER, DELTA):
	"""
	:param C: transmission speed
	:param L: packet + header length
	:param H: header length
	:param TAU: propagation delay
	:param BER: bit error rate
	:param DELTA: time out
	:return: throughput
	"""
	event_simulator = []
	current_time = 0
	sn = 0
	next_expected_ack = 1
	next_expected_frame = 0
	next_expected_frame = send(C, L, H, TAU, BER, DELTA, current_time, event_simulator, sn, next_expected_frame)
	count_successful_packet = 0
	while count_successful_packet <= 10000:
		new_event = event_simulator.pop()
		current_time = new_event['time']
		if new_event['type'] == 'ACK' and new_event['error'] == 'NOERROR' and new_event['rn'] == next_expected_ack:
			sn = (sn + 1) % 2
			next_expected_ack = (next_expected_ack + 1) % 2
			count_successful_packet = count_successful_packet + 1
		next_expected_frame = send(C, L, H, TAU, BER, DELTA, current_time, event_simulator, sn, next_expected_frame)

	return count_successful_packet * (L - H) / current_time

def abp_ack(C, L, H, TAU, BER, DELTA):
	"""
	:param C: transmission speed
	:param L: packet + header length
	:param H: header length
	:param TAU: propagation delay
	:param BER: bit error rate
	:param DELTA: time out
	:return: throughput
	"""
	event_simulator = []
	current_time = 0 
	sn = 0 
	next_expected_ack = 1
	next_expected_frame = 0
	next_expected_frame = send(C, L, H, TAU, BER, DELTA, current_time, event_simulator, sn, next_expected_frame)
	count_successful_packet = 0
	while count_successful_packet <= 10000:
		new_event = event_simulator.pop()
		current_time = new_event['time']
		if new_event['type'] == 'timeout':
			next_expected_frame = send(C, L, H, TAU, BER, DELTA, current_time, event_simulator, sn, next_expected_frame)
		elif new_event['type'] == 'ACK' and new_event['error'] == 'NOERROR' and new_event['rn'] == next_expected_ack:
			sn = (sn + 1) % 2
			next_expected_ack = (next_expected_ack + 1) % 2
			count_successful_packet = count_successful_packet + 1
			next_expected_frame = send(C, L, H, TAU, BER, DELTA, current_time, event_simulator, sn, next_expected_frame)

	return count_successful_packet * (L - H) / current_time

def send(C, L, H, TAU, BER, DELTA, current_time, event_simulator, sn, next_expected_frame):
	timeout = current_time + L/C + DELTA
	timeout_event = {'type':'timeout', 'time': timeout}
	purge_time_out(event_simulator)
	register_event(event_simulator, timeout_event)
	error_count_packet = count_error_bit(L, BER)
	ack_time = current_time + L/C + 2*TAU + H/C
	error_count_ack = count_error_bit(H, BER)
	#if there is no error and receive correct serial number
	if error_count_packet == 0 and next_expected_frame == sn:
		next_expected_frame = (next_expected_frame + 1) % 2
	#check if ack is error
	if error_count_ack == 0:
		ack_event = {'type': 'ACK', 'error': 'NOERROR', 'time': ack_time, 'rn': next_expected_frame}
	elif error_count_ack >= 1 and error_count_ack <= 4:
		ack_event = {'type': 'ACK', 'error': 'ERROR', 'time': ack_time, 'rn': next_expected_frame}
	#check if ack is lost
	if error_count_packet >= 5 or error_count_ack >= 5:
		ack_event = None

	if ack_event is not None:
		register_event(event_simulator, ack_event)

	return next_expected_frame
