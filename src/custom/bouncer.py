# bouncer.py

from discord.ext import commands

def bouncer_command(func):
    async def wrapper(ctx, *args, **kwargs):
        # Add your custom logic before calling the original command function
        print(f"Bouncer Command: {ctx.command} executed")
        result = await func(ctx, *args, **kwargs)
        # Add your custom logic after calling the original command function
        return result
    return wrapper

def bouncer_event(func):
    async def wrapper(*args, **kwargs):
        # Add your custom logic before calling the original event function
        print(f"Bouncer Event: {func.__name__} triggered")
        result = await func(*args, **kwargs)
        # Add your custom logic after calling the original event function
        return result
    return wrapper
