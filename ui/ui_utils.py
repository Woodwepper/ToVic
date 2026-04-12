"""UI/Display utilities for terminal interface"""


class Colors:
    """ANSI color codes"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(text: str):
    """Print a centered header"""
    width = 70
    print("\n" + "="*width)
    print(f"{text.center(width)}")
    print("="*width)


def print_success(text: str):
    """Print success message"""
    print(f"{Colors.GREEN}[OK]{Colors.ENDC} {text}")


def print_error(text: str):
    """Print error message"""
    print(f"{Colors.RED}[ERROR]{Colors.ENDC} {text}")


def print_warning(text: str):
    """Print warning message"""
    print(f"{Colors.YELLOW}[WARN]{Colors.ENDC} {text}")


def print_info(text: str):
    """Print info message"""
    print(f"{Colors.CYAN}[INFO]{Colors.ENDC} {text}")


def print_banner():
    """Print welcome banner"""
    banner = f"""
{Colors.BOLD}{Colors.CYAN}
╔══════════════════════════════════════════════════════════════════╗
║                  TOVIC - Game Simulation Framework              ║
║                         Version 0.1.0                           ║
╚══════════════════════════════════════════════════════════════════╝
{Colors.ENDC}
"""
    print(banner)


def print_menu(title: str, options: list[str]):
    """Print a formatted menu"""
    print(f"\n{Colors.BOLD}=== {title} ==={Colors.ENDC}")
    for i, option in enumerate(options, 1):
        print(f"  {Colors.CYAN}{i}.{Colors.ENDC} {option}")
    print()


def print_table(headers: list[str], rows: list[list[str]]):
    """Print a formatted table"""
    # Calculate column widths
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))
    
    # Print header
    header_line = " | ".join(f"{h:<{col_widths[i]}}" for i, h in enumerate(headers))
    print(f"\n{Colors.BOLD}{header_line}{Colors.ENDC}")
    print("-" * len(header_line))
    
    # Print rows
    for row in rows:
        print(" | ".join(f"{str(cell):<{col_widths[i]}}" for i, cell in enumerate(row)))
    print()


def print_dict(data: dict, indent: int = 0):
    """Print a formatted dictionary"""
    for key, value in data.items():
        prefix = "  " * indent
        if isinstance(value, dict):
            print(f"{prefix}{Colors.CYAN}{key}:{Colors.ENDC}")
            print_dict(value, indent + 1)
        elif isinstance(value, list):
            print(f"{prefix}{Colors.CYAN}{key}:{Colors.ENDC} [{len(value)} items]")
        else:
            print(f"{prefix}{Colors.CYAN}{key}:{Colors.ENDC} {value}")


def get_input_choice(prompt: str, valid_options: list[str]) -> str:
    """Get validated input from user"""
    while True:
        choice = input(f"\n{Colors.BOLD}{prompt}{Colors.ENDC} ").strip()
        if choice in valid_options:
            return choice
        print_error(f"Opcion no valida. Intenta con: {', '.join(valid_options)}")


def get_input_number(prompt: str, min_val: int = 1, max_val: int = None) -> int:
    """Get validated number input from user"""
    while True:
        try:
            value = int(input(f"\n{Colors.BOLD}{prompt}{Colors.ENDC} ").strip())
            if value < min_val:
                print_error(f"El valor debe ser mayor a {min_val}")
                continue
            if max_val and value > max_val:
                print_error(f"El valor debe ser menor a {max_val}")
                continue
            return value
        except ValueError:
            print_error("Ingresa un numero valido")


def print_section(title: str):
    """Print a section divider"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}>>> {title} <<<{Colors.ENDC}\n")
