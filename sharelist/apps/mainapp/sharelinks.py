import secrets

def generate_sharecode():
    """simply generator of url-safe sharecod using secrets"""
    return secrets.token_urlsafe(11)

def main():
    print(generate_sharecode())

if __name__ == "__main__":
    main()