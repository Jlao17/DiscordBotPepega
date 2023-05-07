import discord
from functions.list_to_embed import list_to_embed


class StoreButton(discord.ui.Button):
    def __init__(self, label, style, data, button_row):
        super().__init__(style=style, label=label)
        self.data = data
        self.button_row = button_row

    async def callback(self, interaction: discord.Interaction):
        self.disabled = True
        for button in self.button_row.children:
            if button.label != self.label:
                button.disabled = False
        embed = list_to_embed(self.data, self.label)
        await interaction.response.defer()
        await interaction.message.edit(embed=embed, view=self.button_row)