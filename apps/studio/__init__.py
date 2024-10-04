def _preload_modules():
    print("load")
    import libs.community.plugins
    from fridonai_core.module_utils import resolve_module_plugins

    resolve_module_plugins(libs.community.plugins)

    # import asyncio
    #
    # from fridonai_core.crons.registry import ensure_cron_registry
    # asyncio.get_event_loop().run_until_complete(ensure_cron_registry().start_crons())

