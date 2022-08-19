def suffix_function(hours, minutes, seconds):
    time_list = [hours, minutes, seconds]
    if (hours % 10 == 0 or (hours >= 11 and hours < 20) or hours % 10 >= 5):
        p = "ов";
    elif (hours % 10 == 1):
        p = "";
    else:
        p = "а";
    time_list[0] = f"{hours} час{p}".format(hours=hours, p=p)
    if (minutes % 10 == 0 or (minutes >= 11 and minutes < 20) or minutes % 10 >= 5):
        p = "";
    elif (minutes % 10 == 1):
        p = "а";
    else:
        p = "ы";
    time_list[1] = f"{minutes} минут{p}".format(minutes=minutes, p=p)
    if (seconds % 10 == 0 or (seconds >= 11 and seconds < 20) or seconds % 10 >= 5):
        p = "";
    elif (seconds % 10 == 1):
        p = "а";
    else:
        p = "ы";
    time_list[2] = f"{seconds} секунд{p}".format(seconds=seconds, p=p)

    return time_list