# text = 'b'
#
# num_list = [ord(i) - 96 for i in text]
#
# print(num_list)


def find_the_number_plate(cust_id: str):
    plate_num = 'a a a 0 0 1'
    plate_num_splitted = plate_num.split()
    print(plate_num_splitted)
    letters = []
    numbers = []
    for i in plate_num_splitted:
        if i.isnumeric():
            numbers.append(i)
        else:
            letters.append(i)
    print(letters, numbers)
    cust_id = int(cust_id)
    if cust_id == 0:
        plate_num = plate_num.replace(' ', '')
        return print(plate_num)
    elif cust_id > 0:
        for inx, val in enumerate(plate_num_splitted):
            if not val.isnumeric():
                val = ord(val) + 1
                val = chr(val)
                plate_num_splitted[inx] = val
            else:
                while int(val) < 9:
                    val = int(val) + 1
                    plate_num_splitted[inx] = val
                else:
                    continue
        return print(plate_num_splitted)


find_the_number_plate('1')
