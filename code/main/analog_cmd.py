import serial
import time


# If you are not using Mac with my USB interface, 
# you need to update these serial port types.

ard = serial.Serial('/dev/cu.usbserial-14440', 9600)
last_time = 0

def main():
    while True:
        global last_time
        if time.time() - last_time >= 1:
            last_time = time.time()
            in_file = open('../../../../../../Applications/MOM/eegData.txt', 'r').read()

            list_in = in_file.split(' ')
            nums_list = []

            band_powers = ''

            for i in range(len(list_in)):
                if list_in[i].strip() != '':
                    nums_list += [float(list_in[i])]
                    band_powers += str(float(list_in[i])) + ', '
            
            cmd = str(nums_list[0])
            through = bytes(cmd, "utf8")

            ard.write(through)

            print('Sent {} to arduino.'.format(through))


    return 0




if __name__ == "__main__":
    last_time = 0
    main()
