def installer(func=None, *, check=None):
    """
    Decorator to mark a function as an installer.
    
    Args:
        check: Optional command to check if already installed.
    """
    def _decorator(f):
        f._is_just_installer = True
        f._check_command = check
        return f

    if func is None:
        return _decorator
    return _decorator(func)
