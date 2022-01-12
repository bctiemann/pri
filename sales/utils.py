
def format_cc_number(cc_number):
    if len(cc_number) == 16:
        cc_number = cc_number[0:4] + ' ' + cc_number[4:8] + ' ' + cc_number[8:12] + ' ' + cc_number[12:16]
    elif len(cc_number) == 15:
        cc_number = cc_number[0:4] + ' ' + cc_number[4:10] + ' ' + cc_number[10:15]
    return cc_number
