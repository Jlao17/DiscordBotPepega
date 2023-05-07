import discord
from components.menus.StoreSelectOption import StoreSelectOption
from functions.list_to_embed import list_to_embed


class StoreSelect(discord.ui.Select):
    def __init__(self, data, components):
        super().__init__()
        self.data = data
        self.components = components
        options = []
        for data, name in self.data:
            option = StoreSelectOption(label=name, data=data)
            options.append(option)
        super().__init__(placeholder="Filter on store", options=options)

    async def callback(self, interaction: discord.Interaction):
        selected_options = self.values  # Get the selected option
        selected_option_data = None
        for option in self.options:  # Iterate over the options to find the selected option
            if option.value in selected_options:
                selected_option_data = option.data  # Get the data associated with the selected option
        embed = list_to_embed(selected_option_data, ''.join(selected_options))
        await interaction.response.defer()
        await interaction.message.edit(embed=embed, view=self.components)