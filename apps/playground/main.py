from fridonai_core.graph.base import generate_response
from fridonai_core.plugins.registry import ensure_plugin_registry
from apps.fridon_brain import _preload_modules
from settings import settings

async def main():
    _preload_modules()
    plugin_names = [
        "intelligent-coin-searcher",
        "coin-technical-analyzer",
        "coin-observer",
        "wallet",
        "jupiter",
        "fridon",
        "solana-bonk-educator",
        "emperor-trader",
    ]
    registry = ensure_plugin_registry()

    plugins = [registry.plugins[plugin_name]() for plugin_name in plugin_names]

    config = {
        "thread_id": "1",
        "wallet_id": "2snYEzbMckwnv85MW3s2sCaEQ1wtKZv2cj9WhbmDuuRD",
        "chat_id": "bla",
    }

    final_response, used_agents, _, _ = await generate_response(
        "Analyze sol price chart",
        plugins,
        config,
        memory="sqlite",
    )

    print(final_response)
    print(used_agents)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
