def installer(func):
    """
    Decorator to mark a function as an installer.
    
    Sets _is_just_installer attribute to True for runtime detection.
    """
    func._is_just_installer = True
    return func
