import argparse
import os.path
import LZ4_Rate, LZ4_Time, LZ4_Transmission
import time
from datetime import timedelta
import datetime

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', default=None, required=True, help='File to Compress or Decompress')
    parser.add_argument('--Compress_Decompress', type=int, required=True,  help='0 for Compression , \
                                                                                 1 for Decompression')
    parser.add_argument('--mode', default=0, type=int, required=False, help='0 for optimizing Compression Ratio, \
                                                                             1 for optimizing Time of Compression, \
                                                                             2 for optimizing time of Transimision')
    parser.add_argument('--jump', default=5, type=int, required=False, help='Jumps to try between VA of size 5 and 65535')

    parser.add_argument('--ini_VA', default=15, type=int, required=False, help='Initial VA_Window (only for time option)')

    parser.add_argument('--end_VA', default=65535, type=int, required=False, help='End_ VA_Window (only for time option)')



    args = parser.parse_args()
    filename = args.file
    CorD = args.Compress_Decompress
    mode = args.mode
    jump = args.jump
    ini_VA = args.ini_VA
    end_VA = args.end_VA

    assert os.path.isfile(filename), "File path is wrong or it does not exist"
    assert mode <=2, "Mode should be equal or least than 2"
    assert CorD <=1, "Mode should be equal or least than 1"

    start = datetime.datetime.now()
    if mode == 0:
        if CorD == 0:
            Compressed = LZ4_Rate.compress(filename)
        else:
            Decompressed = LZ4_Rate.decompress(filename)
    elif mode == 1:
        if CorD == 0:
            Compressed = LZ4_Time.compress(filename, VA=10)
            end = datetime.datetime.now()
            elapsed_time = end - start;
            CR = 0
            with open(filename, 'rb') as f:
                CR = len(f.read()) / len(Compressed)
            print(' # Seconds {}, Miliseconds {}'.format(elapsed_time.seconds, elapsed_time.microseconds/1000), end='\t')
            print(' # Compression Rate:', CR, end='\t')
            print(' # Progress', 0, '%', end='\n\n')

            for i, VA in enumerate(range(ini_VA, end_VA, jump)):
                trial = LZ4_Time.compress(filename, VA=VA)
                if len(trial) < len(Compressed):
                    Compressed = trial
                    with open(filename, 'rb') as f:
                        CR = len(f.read()) / len(Compressed)
                end = datetime.datetime.now()
                elapsed_time = end - start;
                print(' # Seconds {}, Miliseconds {}'.format(elapsed_time.seconds, elapsed_time.microseconds/1000), end='\t')
                print(' # Compression Rate:', CR, end='\t')
                print(' # Progress', (VA/end_VA)*100, '%', end='\n\n')


                if elapsed_time.seconds >= 295:
                    print("################# Time limit Reached, therefore stop trials with a maximum Compression Rate of", CR)
                    break
            end = datetime.datetime.now()

            elapsed_time = end - start;
            print('Final time -> Seconds: {}, MicroSeconds: {}, BEST Compression Ratio, {}'.format(elapsed_time.seconds, elapsed_time.microseconds/1000, CR))

        else:
            Decompressed = LZ4_Time.decompress(filename)
    else:
        if CorD == 0:
            Compressed = LZ4_Transmission.compress(filename)
        else:
            Decompressed = LZ4_Transmission.decompress(filename)
    



    if CorD == 0:
        with open('./pruebas/' + filename + '.lz4', 'wb+') as f:
            f.write(Compressed)

    else:
        filename = '.'.join(filename.split('.')[:-1])
        with open(filename, 'wb+') as f:
            f.write(Decompressed)




