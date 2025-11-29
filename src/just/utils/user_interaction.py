def confirm_action(message: str) -> bool:
    """Prompt user for confirmation"""
    response = input(f"{message} (y/N): ").strip().lower()
    return response in ['y', 'yes']