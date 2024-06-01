def _preload_modules():
    print("load")
    import app.community.plugins
    from app.core.registry import resolve_module_plugins

    resolve_module_plugins(app.community.plugins)

_preload_modules()
