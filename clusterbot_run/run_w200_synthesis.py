import os
import sys
import csv
import time
import inspect

HERE = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
ROOT = os.path.join(HERE, "..")
CSV = os.path.join(HERE, "csv")
PLATFORM = os.path.join(ROOT, "clusterbot", "software")

sys.path.append(PLATFORM)

from tools.manager import Manager
import operations.constants.common as cst
import operations.constants.filepaths as fp


FRODO_CSV = os.path.join(CSV, "DSA_CB_WTM_1429_1548", "frodocsv.csv")
SAM_CSV = os.path.join(CSV, "DSA_CB_WTM_397_564", "samcsv.csv")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Pass in the flag! 0 for Frodo, 1 for Sam")
        sys.exit(-1)

    flag = int(sys.argv[1])

    platform = Manager(flag)
    if flag == 0:
        csv_file = FRODO_CSV
    elif flag == 1:
        csv_file = SAM_CSV

    platform.start_wheel_stirring()
    platform.start_stirrer_plate()

    x = input("Prime pumps? (y/n)")
    if x.lower() == "y":
        platform.prime_pumps() # Add in the pumps to ignore as arguments
        platform.turn_wheel(1)
        input("Replace vial and press enter...")


    ifile = open(csv_file, 'r')
    reader = csv.reader(ifile)

    rownum = 0
    '''
    Setting the Header row as the titles i.e the pump reagents column by column
    '''

    for row in reader:
        if rownum == 0:
            header = row
        else:
            colnum = 0
            for col in row:
                if colnum == 10: # do this number column in position 'K' on the csv to avoid needing to change for each reaction series
                    if float(col) % 24 == 0:
                        platform.log('Thats 24.. Replace the vials')
                        platform.send_mail("Finished 24!\nGo replace the vials!", 0)
                        input('Reaction {} about to start, time to change out vials! Any key to continue'.format(col))
                        input('Are you sure?!')
                elif colnum == 0:
                    platform.log("\nThe reaction is code {}".format(col)) # first column contains the reaction code
                elif colnum == 1:
                    print ("Dispensing from {} pump, {} mL".format(header[colnum],col)) # W
                    platform.dispense("R1", float(col))
                elif colnum == 2:
                    print ("Dispensing from {} pump, {} mL".format(header[colnum],col)) # acid
                    platform.dispense("R3", float(col))
                elif colnum == 3:
                    print ("Dispensing from {} pump, {} mL".format(header[colnum],col)) # TM1
                    platform.dispense("R4", float(col))
                elif colnum == 4:
                    print ("Dispensing from {} pump, {} mL".format(header[colnum],col)) # TM2
                    platform.dispense("R5", float(col))
                elif colnum == 5:
                    print ("Dispensing from {} pump, {} mL".format(header[colnum],col)) # TM3
                    platform.dispense("R6", float(col))
                elif colnum == 6:
                    print ("Dispensing from {} pump, {} mL".format(header[colnum],col)) # TM4
                    platform.dispense("R7", float(col))
                elif colnum == 7:
                    print ("Dispensing from {} pump, {} mL".format(header[colnum],col)) # Thionite
                    platform.dispense("R2", float(col))
                # elif colunm == 8:
                #     print ("Dispensing from {} pump, {} mL".format(header[colnum],col)) # TM5
                #     platform.dispense("R8", float(col))
                # elif colnum == 6:
                #     print ("Dispensing from {} pump, {} mL".format(header[colnum],col)) # Mn
                #     platform.dispense("R6", float(col))
                # elif colnum == 7:
                #     print ("Dispensing from {} pump, {} mL".format(header[colnum],col)) # Fe
                #     platform.dispense("R7", float(col))
                colnum += 1
            platform.turn_wheel(1)

        rownum += 1

    ifile.close()

    platform.stop_wheel_stirring()
    platform.send_mail("Reaction sequence finished!", 0)
