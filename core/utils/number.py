def format_british_style(number):
    formatted_number = "{:,}".format(number)

    return formatted_number


def human_friendly_number(num: int) -> str:
    if num >= 1_000_000_000:
        return f"{round(num / 1_000_000_000, 1):.1f}B"
    elif num >= 1_000_000:
        return f"{round(num / 1_000_000, 1):.1f}M"
    elif num >= 1_000:
        return f"{round(num / 1_000, 1):.1f}K"
    else:
        return str(num)
