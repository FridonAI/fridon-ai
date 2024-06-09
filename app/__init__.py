def _preload_modules():
    print("load")
    import app.community.plugins
    from app.core.module_utils import resolve_module_plugins

    resolve_module_plugins(app.community.plugins)

    from app.core.crons.registry import ensure_cron_registry
    ensure_cron_registry().start_crons()

_preload_modules()
