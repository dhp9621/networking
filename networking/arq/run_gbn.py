from gbn import *
import csv

C = 5000000
L = (1500 + 54) * 8
H = 54 * 8
TAU = [0.005, 0.25]
BER = [0, 10 ** (-5), 10 ** (-4)]
DELTA = [2.5, 5, 7.5, 10, 12.5]
window_size = 4
with open('gbn.csv', 'w', newline='') as csvfile:
    csv_writer = csv.writer(csvfile)
    for d in DELTA:
        row = []
        for t in TAU:
            for b in BER:
                row.append(gbn(C, L, H, t, b, d * t, window_size))
        csv_writer.writerow(row)