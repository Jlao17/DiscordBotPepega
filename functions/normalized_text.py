def normalized_text(text):
    special_characters = ["ー", "™"]
    # We are removing everything in special_characters and special characters isalnum()
    return ''.join(c for c in text if c not in special_characters and c.isalnum()).lower()
