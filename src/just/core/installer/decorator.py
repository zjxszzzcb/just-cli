def installer(func):
    """
    Decorator to mark a function as an installer.
    """
    # Mark the function as an installer
    func._is_installer = True
    return func