import discord
from components.menus.StoreSelectOption import StoreSelectOption
from functions.list_to_embed import list_to_embed
from functions.check_game_in_db import check_game_in_db
import logging
import copy

log = logging.getLogger(__name__)


class StoreSelect(discord.ui.Select):
    def __init__(self, data, components, user_cnf):
        super().__init__()
        self.data = data
        self.components = components
        self.user_cnf = user_cnf
        options = []
        for option_data, name in self.data:
            if option_data:
                # Ensure each custom option includes the required arguments
                option = StoreSelectOption(label=name, data=option_data)
                options.append(option)
        self.options = options  # Override options with custom StoreSelectOption instances
        super().__init__(placeholder="Filter on store", options=options)

    async def callback(self, interaction: discord.Interaction):
        # if interaction.user.id != ctx.author.id
        selected_options = self.values  # Get the selected option
        selected_option_data = None
        # print("self.options", self.options)
        for option in self.options:  # Iterate over the options to find the selected option
            if option.value in selected_options:
                selected_option_data = option.data  # Get the data associated with the selected option

        modified_data = copy.deepcopy(selected_option_data)

        # convert modified_data[0][0] to steam game name
        game_name = await check_game_in_db(int(modified_data[0][0]))

        temp_list = list(modified_data[0])  # Work with the first element of the copied list
        temp_list[0] = game_name[1]  # Modify the first element
        modified_data[0] = tuple(temp_list)  # Convert it back to a tuple

        # Use the copied list for the embed
        embed = await list_to_embed(modified_data, ''.join(selected_options), self.user_cnf)

        await interaction.response.defer()
        await interaction.message.edit(embed=embed, view=self.components)
