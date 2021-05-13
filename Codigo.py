import argparse
import os.path
import LZ4_Rate, LZ4_Time, LZ4_Transmission


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', default=None, required=True, help='File to Compress or Decompress')
    parser.add_argument('--Compress_Decompress', type=int, required=True,  help='0 for Compression , \
                                                                                 1 for Decompression')
    parser.add_argument('--mode', default=0, type=int, required=False, help='0 for optimizing Compression Ratio, \
                                                                             1 for optimizing Time of Compression, \
                                                                             2 for optimizing time of Transimision')
    parser.add_argument('--VA', default=150, type=int, required=False, help='Ventana Avanzada')
    parser.add_argument('--VB', default=65536, type=int, required=False, help='Ventanza Búsqueda')
    args = parser.parse_args()
    filename = args.file
    CorD = args.Compress_Decompress
    mode = args.mode
    va = args.VA
    vb = args.VB

    assert os.path.isfile(filename), "File path is wrong or it does not exist"
    assert mode <=2, "Mode should be equal or least than 2"
    assert CorD <=1, "Mode should be equal or least than 1"

    if mode == 0:
        if CorD == 0:
            Compressed = LZ4_Rate.compress(filename)
        else:
            Decompressed = LZ4_Rate.decompress(filename)
    elif mode == 1:
        if CorD == 0:
            Compressed = LZ4_Time.compress(filename, va, vb)
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




