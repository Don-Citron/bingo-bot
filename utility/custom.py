"""Custom versions of discord.py objects.

Note that in order to reload this code utility.custom needs to be reloaded, and then every cog that uses it."""

import discord
from discord.ext import commands

import importlib

class CustomCog(commands.Cog):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
    
    def _reload_module(self, module_name: str) -> bool:
        """Reloads a module by name.
        For imports that are in a folder, the folder name must be included. For instance: `utility.files` would reload the utility.files code.
        Returns a bool for whether anything was reloaded, so the number of reloads can be counted."""

        # Get a list of the names of every module in globals(). This can be done with a list comprehension but this is easier to read.
        globals_modules = []

        for module in self.globals.values():
            if hasattr(module, "__name__"):
                globals_modules.append(module.__name__)
        
        # Get a list of every imported module via cross-checking globals_modules and sys.modules.
        all_modules = set(self.modules) & set(globals_modules)

        # If the provided module name 
        if module_name not in all_modules:
            return False
        
        # Get the module object.
        module = self.modules[module_name]

        # Reload the module via importlib.reload.
        importlib.reload(module)
        print("- {} has reloaded {}.".format(self.qualified_name, module_name))

        # Return True, since it has been reloaded in theory.
        return True