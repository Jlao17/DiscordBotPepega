import string


def normalized_text(text):
    ascii_and_numbers = string.ascii_letters + string.digits
    # We are just allowing a-z, A-Z and 0-9 and use lowercase characters

    return ''.join(c for c in text if c in ascii_and_numbers).lower()
