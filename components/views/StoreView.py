import discord
from components.menus.StoreSelect import StoreSelect


class StoreView(discord.ui.View):
    def __init__(self, data):
        super(StoreView, self).__init__(timeout=100)
        self.data = data

        self.add_item(StoreSelect(data, self))