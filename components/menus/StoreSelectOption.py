import discord


class StoreSelectOption(discord.SelectOption):
    def __init__(self, label, data):
        super().__init__(label=label)
        self.data = data
