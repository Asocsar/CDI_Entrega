import time
import sys
import datetime


compress_decompress = sys.argv[1]
filename = sys.argv[2]

# %%
def move_search_window_forward(VB_ini, VB_end, windows_size):
    VB_end += 1
    if VB_end - VB_ini > windows_size:
            VB_ini += 1
    return VB_ini, VB_end
# %%
def move_advance_window_forward(VB_end, window_size, total_length):
    VA_ini = VB_end
    VA_end = min(VA_ini + window_size, total_length)
    return VA_ini, VA_end

# %%
def move_both_windows(VA, VB, window_VA, window_VB, total_length):
    VA_ini, VA_end = VA
    VB_ini, VB_end = VB
    VB_iniO, VB_endO = move_search_window_forward(VB_ini, VB_end, window_VB)
    VA_iniO, VA_endO = move_advance_window_forward(VB_endO, window_VA, total_length)
    return VA_iniO, VA_endO, VB_iniO, VB_endO

# %%
def create_token_expansion(S):
    if S < 15:
        t = bin(S)[2:]
        t = '0'*(4-len(t)) + t
        return t, bytearray([])
    
    else:
        t = bin(15)[2:]
        S -= 15
        e = bytearray([])
        while S >= 255:
            e += bytearray([255])
            S -= 255
        e += bytearray([S])
        return t, e

# %%
def createOffsetBytes(Offset):
    O = Offset.to_bytes(2, 'little')
    return O

#%%
def update_windows(VB_ini, VB_end, match_size, window_sizeB, window_sizeA, total_length):
    VB_end += match_size
    if VB_end - VB_ini > window_sizeB:
        VB_ini = VB_end - window_sizeB
    VA_ini, VA_end = move_advance_window_forward(VB_end, window_sizeA, total_length)
    return VA_ini, VA_end, VB_ini, VB_end

# %%
def compress(filename, VB=65535, VA=150):

    start = time.time()
    
    with open(filename, 'rb') as f:
        end = False
        data = f.read()
        output = bytearray([])
        total_length = len(data)



        ini_debug = 0

        VB_ini = 0
        VB_end = 0
        VA_ini = 0
        VA_end = VA+1

        VB_Window = data[VB_ini:VB_end]
        VA_Window = data[VA_ini:VA_end]

        acumulated_bits = bytearray([])
        itera = -1
        while not end:
            if total_length <= 5:
                end = True
            itera += 1
            sizeA = 1 #size of the advance window
            match = False
            end = len(VA_Window) == 0
            VB_iniM, VB_endM = VB_ini, VB_end
            while not end and sizeA <= len(VA_Window) and VA_Window[0:sizeA] in VB_Window:
                match = (sizeA  >= 4)
                VB_Window = VB_Window + bytearray([VA_Window[sizeA-1]])
                sizeA += 1
            
            #Corrijo error numerico ya que para romper el bucle, los indices daran error por una posicion
            sizeA -=1
            
            if not match and not end:
                desp = max(sizeA, 1)
                acumulated_bits += bytearray([data[VA_ini]])
                VA_ini, VA_end, VB_ini, VB_end = move_both_windows((VA_ini, VA_end), (VB_ini, VB_end), VA, VB, total_length-6)

            else:
                

                if not end:
                    t1, e1 = create_token_expansion(len(acumulated_bits))
                    t2, e2 = create_token_expansion(sizeA - 4)
                    
                    Offset = len(VB_Window) - VB_Window.index(VA_Window[0:sizeA]) - sizeA
                    O = createOffsetBytes(Offset)
                    t = bytearray([int(t1 + t2, 2)])
                    block = t + e1 + acumulated_bits + O + e2
                    acumulated_bits_d = acumulated_bits
                    acumulated_bits = bytearray([])

                    advanced = sizeA
                    VA_ini, VA_end, VB_ini, VB_end = update_windows(VB_ini, VB_end, advanced, VB, VA, total_length-6)
                else: 
                    t1, e1 = create_token_expansion(len(data[-6:]))
                    t2, e2 = create_token_expansion(0)
                    t = bytearray([int(t1 + t2, 2)])
                    block = t + e1 + acumulated_bits + data[-6:] 
                


                output += block
            
            ini_debug = len(output)


            VB_Window = data[VB_ini:VB_end]
            VA_Window = data[VA_ini:VA_end]

    end = time.time()
    print(str(end-start))

    return output   
        

def readByte(file, bytesToRead):
    byte = int(ord(file.read(bytesToRead)))
    return byte

def decompress(filename):
    start = time.time()

    fileDecompress = []
    with open(filename,'rb') as file:
        byte = readByte(file,1)
        t1 = (byte & 0xF0) >> 4
        t2 = byte & 0x0F
        while True:
            try:
                sumLength = t1
                if ( t1 == 15):
                    byte = readByte(file,1)
                    sumLength = sumLength + byte
                    
                    while (byte == 255):
                        byte = readByte(file,1)
                        sumLength = sumLength + byte
                
                literal = []
                
                for i in range(0, sumLength):
                    byte = readByte(file,1)
                    literal.append(chr(byte))
                    fileDecompress.append(chr(byte))
                
                offset1 = readByte(file,1)
                offset2 = readByte(file,1)
                
                offset2 = offset2 << 8
                offset = offset1 | offset2
                
                matchlength = t2+4
                
                if ( t2 == 15 ):
                    byte = readByte(file,1)
                    matchlength = matchlength + byte
                    
                    while ( byte == 255 ):
                        byte = readByte(file,1)
                        matchlength = matchlength + byte
                
                initial_index = (len(fileDecompress)-offset)
                final_index = (len(fileDecompress)-offset+matchlength)
                
                if ( offset < matchlength ): #exception
                    offsetMensaje = fileDecompress[initial_index:final_index]
                    for i in range(0, matchlength-offset):
                        offsetMensaje.append(offsetMensaje[i])
                
                else:			
                    offsetMensaje = fileDecompress[initial_index:final_index]
                
                for i in range(0, len(offsetMensaje)):
                    fileDecompress.append(offsetMensaje[i])
                
                byte = readByte(file,1)
                t1 = (byte & 0xF0) >> 4
                t2 = byte & 0x0F
            
            except:
                break

    fileDecompress = [ord(x) for x in fileDecompress]
    mensaje = bytearray(fileDecompress)
    #for i in range(0, len(fileDecompress)):
    #    mensaje += fileDecompress[i]
    filename = '.'.join(filename.split('.')[:-1])
    with open(filename, 'wb+') as f:
        f.write(mensaje)

    end = time.time()
    print(end-start)

if ( compress_decompress == '-c' ):
    ini_VA, end_VA = 10, 200
    jump = 5

    start = datetime.datetime.now()
    Compressed = compress(filename)
    end = datetime.datetime.now()
    elapsed_time = end - start

    for i, VA in enumerate(range(ini_VA, end_VA, jump)):
        start_comp = datetime.datetime.now()
        trial = compress(filename, VA=VA)
        if len(trial) < len(Compressed):
            Compressed = trial

        end = datetime.datetime.now()
        elapsed_time = end - start;
        compression_elapsed_time = end - start_comp
       


        if elapsed_time.seconds + compression_elapsed_time.seconds >= 295:
            break
    end = datetime.datetime.now()

    elapsed_time = end - start;

    with open(filename + '.lz4', 'wb+') as f:
        f.write(Compressed)

elif ( compress_decompress == '-d' ):
    decompress(filename)
