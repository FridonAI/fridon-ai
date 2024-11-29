from fridonai_core.graph.base import generate_response
from fridonai_core.plugins.registry import ensure_plugin_registry
from apps.fridon_brain import _preload_modules
from settings import settings

async def main():
    _preload_modules()
    plugin_names = ["wallet", "fridon", "coin-technical-chart-searcher", "coin-technical-analyzer"]
    registry = ensure_plugin_registry()

    plugins = [registry.plugins[plugin_name]() for plugin_name in plugin_names]

    config = {  
            "thread_id": "1",
            "wallet_id": "2snYEzbMckwnv85MW3s2sCaEQ1wtKZv2cj9WhbmDuuRD",
            "chat_id": "bla"
        }
    
    final_response, used_agents = await generate_response(
        # "Give me coins like WIF in 2023 december by chart similarity",
        "Which coins in the past end when had the same 4h chart as WIF now?",
        plugins,
        config,
        memory="sqlite",
    )
    
    print(final_response)
    print(used_agents)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
