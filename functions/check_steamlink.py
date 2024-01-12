async def check_steamlink(args, check):
    if check == 0:
        name = ""
        check = ["https://store.steampowered.com/app/", "store.steampowered.com/app/", "steampowered.com/app/"]
        for steamlink in check:
            if steamlink in args:
                new_args = args.replace(steamlink, "")
                for character in new_args:
                    if character.isdigit():
                        name += character
                    else:
                        return [True, name]
        return [False, name]
    elif check == 1:
        name = ""
        check = ["https://store.steampowered.com/app/", "store.steampowered.com/app/", "steampowered.com/app/"]
        for steamlink in check:
            if steamlink in args:
                new_args = args.replace(steamlink, "")
                for character in new_args:
                    if character.isdigit():
                        name += character
                    else:
                        return name
