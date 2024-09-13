def _preload_modules():
    print("load")
    import app.community.plugins
    from app.core.module_utils import resolve_module_plugins

    resolve_module_plugins(app.community.plugins)

    # import asyncio
    #
    # from app.core.crons.registry import ensure_cron_registry
    # asyncio.get_event_loop().run_until_complete(ensure_cron_registry().start_crons())

