from utils import *
from collections import deque

def gbn(C, L, H, TAU, BER, DELTA, window_size):
    """
    :param C: transmission speed
    :param L: packet + header length
    :param H: header length
    :param TAU: propagation delay
    :param BER: bit error rate
    :param DELTA: time out
    :param window_size: window size
    :return: throughput
    """

    window_buffer = deque([[s,0] for s in range(window_size)], maxlen=window_size)
    event_simulator = []
    current_time = 0
    next_expected_frame = 0
    sn = 0
    count_successful_packet = 0
    i = 0

    while count_successful_packet <= 10000:
        P = window_buffer[0][0] #P is the first element in the queue aka the oldest packet sent
        sn = window_buffer[i][0]
        current_time = window_buffer[i][1] #time when the packet was sent
        timeout = window_buffer[0][1] + L/C + DELTA
        timeout_event = {'type': 'timeout', 'time': timeout}
        purge_time_out(event_simulator)
        register_event(event_simulator, timeout_event)
        next_expected_frame = send(C, L, H, TAU, BER, DELTA, current_time, event_simulator, sn, next_expected_frame, window_size)
        if i >= window_size - 1 or window_buffer[i][1] >= event_simulator[-1]['time']: #If all packets in the buffer have been sent or time exceeds
            new_event = event_simulator.pop()
            current_time = new_event['time']
            if new_event['type'] == 'timeout':
                i = 0
            elif new_event['type'] == 'ACK' and new_event['error'] == 'NOERROR' and new_event['rn'] != P:
                number_of_shifts = (new_event['rn'] - P) % (window_size + 1) #Shift (RN - P) % (N + 1) entries
                count_successful_packet = count_successful_packet + number_of_shifts
                for n in range(number_of_shifts): #Shift the buffer
                    window_buffer.popleft()
                    next_sn = (window_buffer[-1][0] + 1) % (window_size + 1)
                    current_time = current_time + L/C
                    window_buffer.append([next_sn, current_time])
                i = i - number_of_shifts + 1 #Calculate next packet to be sent
                if i < 0:
                    i = 0
        else:
            i = i + 1
            current_time = current_time + L / C
        window_buffer[i][1] = current_time #Update the time of current packet
    return count_successful_packet * (L - H) / current_time


def send(C, L, H, TAU, BER, DELTA, current_time, event_simulator, sn, next_expected_frame, window_size):
    error_count_packet = count_error_bit(L, BER)
    ack_time = current_time + L/C + 2*TAU + H/C
    error_count_ack = count_error_bit(H, BER)
    #if there is no error and receive correct serial number
    if next_expected_frame == sn:
        if error_count_packet == 0:
            next_expected_frame = (next_expected_frame + 1) % (window_size + 1)
        #check if ack is error
        if error_count_ack == 0:
            ack_event = {'type': 'ACK', 'error': 'NOERROR', 'time': ack_time, 'rn': next_expected_frame}
        elif error_count_ack >= 1 and error_count_ack <= 4:
            ack_event = {'type': 'ACK', 'error': 'ERROR', 'time': ack_time, 'rn': next_expected_frame}
    #check if ack is lost
    else:
        ack_event = None

    if error_count_packet >= 5 or error_count_ack >=5:
        ack_event = None

    if ack_event is not None:
        register_event(event_simulator, ack_event)

    return next_expected_frame