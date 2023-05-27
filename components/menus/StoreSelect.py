import discord
from components.menus.StoreSelectOption import StoreSelectOption
from functions.list_to_embed import list_to_embed
import logging

log = logging.getLogger(__name__)

class StoreSelect(discord.ui.Select):
    def __init__(self, data, components):
        super().__init__()
        self.data = data
        self.components = components
        options = []
        for data, name in self.data:
            if data:
                # log.info(data)
                # log.info(name)
                option = StoreSelectOption(label=name, data=data)
                options.append(option)
            continue
        super().__init__(placeholder="Filter on store", options=options)

    async def callback(self, interaction: discord.Interaction):
        selected_options = self.values  # Get the selected option
        selected_option_data = None
        # print("self.options", self.options)
        for option in self.options:  # Iterate over the options to find the selected option
            if option.value in selected_options:
                selected_option_data = option.data  # Get the data associated with the selected option
        embed = await list_to_embed(selected_option_data, ''.join(selected_options))
        await interaction.response.defer()
        await interaction.message.edit(embed=embed, view=self.components)
