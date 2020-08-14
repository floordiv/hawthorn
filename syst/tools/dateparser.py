multipliers = {
    's': 1,
    'm': 60,
    'h': 3600,
    'd': 86400,
    'M': 2592000,
    'y': 31536000
}

intervals = (
        ('weeks', 604800),  # 60 * 60 * 24 * 7
        ('days', 86400),  # 60 * 60 * 24
        ('hours', 3600),  # 60 * 60
        ('minutes', 60),
        ('seconds', 1),
    )


def validate(dates):
    valid = []

    for date in dates:
        if date and date[:-1].isdigit() and date[-1] in multipliers:
            valid.append(date)

    return valid


def parse(*dates):
    dates = validate(dates)
    total = 0

    for date in dates:
        time_of_mute = date[:-1]  # remove letter
        chosen_multiplier = date[-1]

        if not time_of_mute.isdigit() or chosen_multiplier not in multipliers:
            continue

        if chosen_multiplier in multipliers.keys():
            total += int(time_of_mute) * multipliers[chosen_multiplier]

    return total


def date_by_seconds(seconds):
    result = ''

    for name, count in intervals:
        value = seconds // count
        seconds -= value * count

        if value == 1:
            name = name.rstrip('s')
        elif value == 0:
            continue

        result += str(value) + ' ' + name + ', '

    return result.strip(',')
