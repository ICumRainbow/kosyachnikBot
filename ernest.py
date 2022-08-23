# text = 'b'
#
# num_list = [ord(i) - 96 for i in text]
#
# print(num_list)


# def find_the_number_plate(cust_id: str):
#     plate_num = 'a a a 0 0 1'
#     plate_num_splitted = plate_num.split()
#     print(plate_num_splitted)
#     letters = []
#     numbers = []
#     for i in plate_num_splitted:
#         if i.isnumeric():
#             numbers.append(i)
#         else:
#             letters.append(i)
#     print(letters, numbers)
#     cust_id = int(cust_id)
#     if cust_id == 0:
#         plate_num = plate_num.replace(' ', '')
#         return print(plate_num)
#     elif cust_id > 0:
#         for inx, val in enumerate(plate_num_splitted):
#             if not val.isnumeric():
#                 val = ord(val) + 1
#                 val = chr(val)
#                 plate_num_splitted[inx] = val
#             else:
#                 while int(val) < 9:
#                     val = int(val) + 1
#                     plate_num_splitted[inx] = val
#                 else:
#                     continue
#         return print(plate_num_splitted)
#
#
# find_the_number_plate('1')

# ДОДЕЛАТЬ
# def format_duration(seconds):
#     hours = seconds // 60 // 60
#     minutes = seconds // 60
#     secs = seconds % 60
#
#     return print(hours, minutes, secs)
#
# format_duration(7200)
#
# print(2516 % 100)
# ДОДЕЛАТЬ# ДОДЕЛАТЬ# ДОДЕЛАТЬ# ДОДЕЛАТЬ# ДОДЕЛАТЬ


def rgb(r, g, b):
    first_digit = {
        '0': 0,
        '1': 16,
        '2': 32,
        '3': 48,
        '4': 64,
        '5': 80,
        '6': 96,
        '7': 112,
        '8': 128,
        '9': 144,
        'A': 160,
        'B': 176,
        'C': 192,
        'D': 208,
        'E': 224,
        'F': 240
    }
    second_digit = {
        '0': 0,
        '1': 1,
        '2': 2,
        '3': 3,
        '4': 4,
        '5': 5,
        '6': 6,
        '7': 7,
        '8': 8,
        '9': 9,
        'A': 10,
        'B': 11,
        'C': 12,
        'D': 13,
        'E': 14,
        'F': 15
    }
    r_string = ''
    g_string = ''
    b_string = ''
    for (key, value) in first_digit.items():

        for key2, value2 in second_digit.items():
            if r < 0:
                r_string = '00'
            elif value2 + value == r:
                r_string = r_string + (key + key2)
            elif r > 255:
                r_string = 'FF'

            if g < 0:
                g_string = '00'
            elif value2 + value == g:
                g_string = g_string + (key + key2)
            elif g > 255:
                g_string = 'FF'

            if b < 0:
                b_string = '00'
            elif value2 + value == b:
                b_string = b_string + (key + key2)
            elif b > 255:
                b_string = 'FF'

    return r_string + g_string + b_string


rgb(-20, 275, 125)
