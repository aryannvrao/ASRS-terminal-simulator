import time
from asrs_logic import (
    Tray,
    is_valid_choice,
    is_valid_amount,
    get_qty_after_increase,
    get_qty_after_reduce,
    build_path,
    find_nearest_empty_slot,
    build_admin_view,
    build_station_tray_view,
    build_movement_header
)

# ==========================================
# Constants
# ==========================================
N = 4
TRAY_CAPACITY = 50
MOVE_SEC = 1
TURN_SEC = 0

# ==========================================
# Display & Validation Functions
# ==========================================
def display_main_menu(racks, robot, sim_clock, n):
    """Prints the ASRS header, current warehouse snapshot, and the 5 main choices."""
    print("=" * 40)
    print("ASRS TERMINAL")
    print("=" * 40)
    print(build_admin_view(racks, robot, sim_clock, n))
    print("1. Call robot WITH tray id")
    print("2. Call robot EMPTY")
    print("3. Print warehouse map / Admin")
    print("4. Robot status")
    print("5. Exit")

def validate_choice(prompt, max_choice):
    """Prompts the user until a valid whole-number choice is entered."""
    while True:
        user_input = input(prompt)
        if is_valid_choice(user_input, max_choice):
            return int(user_input)
        print("Invalid choice.")

def validate_tray_id(racks):
    """Prompts for a Tray ID, ensuring it exists somewhere in the racks."""
    while True:
        user_input = input("Tray ID: ")
        try:
            tid = int(user_input)
        except ValueError:
            print("Tray not found.")
            continue
        
        found = False
        for side in range(2):
            for r in range(N):
                for c in range(N):
                    if racks[side][r][c] is not None and racks[side][r][c].tray_id == tid:
                        found = True
                        break
                if found: break
            if found: break
            
        if found:
            return tid
        print("Tray not found.")

def validate_amount(prompt):
    """Prompts the user until a valid non-negative whole number is entered."""
    while True:
        user_input = input(prompt)
        if is_valid_amount(user_input):
            return int(user_input)
        print("Invalid input.")

def get_valid_item_id():
    """Prompts for an Item ID, ensuring it's a valid integer (prevents crashes)."""
    while True:
        user_input = input("Enter new item id: ")
        try:
            return int(user_input)
        except ValueError:
            print("Invalid input.")

# ==========================================
# Execution & Movement
# ==========================================
def execute_path(path, robot, sim_clock):
    """Applies each move in path to robot, sleeping 1 second and printing live position."""
    print(build_movement_header(path))
    for step in path:
        if step == 'UP':
            robot['row'] -= 1
        elif step == 'DOWN':
            robot['row'] += 1
        elif step == 'IN':
            robot['col'] += 1
        elif step == 'OUT':
            robot['col'] -= 1
        elif step == 'TURN':
            robot['side'] = 1 - robot['side']
            
        if step != 'TURN':
            sim_clock += MOVE_SEC
            
        print(f"[t={sim_clock}s] robot at Side {robot['side']} ({robot['row']},{robot['col']})")
        time.sleep(MOVE_SEC)
        
    return sim_clock

# ==========================================
# Main Application Loop
# ==========================================
def main():
    # 1. Initialize state
    racks = [
        [[None for _ in range(N)] for _ in range(N)],
        [[None for _ in range(N)] for _ in range(N)]
    ]
    
    robot = {
        "side": 0,
        "row": N - 1,
        "col": 0,
        "carrying": None
    }
    
    sim_clock = 0
    next_tray_id = 1
    
    # 2. Main Loop
    while True:
        display_main_menu(racks, robot, sim_clock, N)
        choice = validate_choice("Enter choice: ", 5)
        
        # ==========================================
        # Choice 1: Call robot WITH tray id
        # ==========================================
        if choice == 1:
            tray_id = validate_tray_id(racks)
            
            # Locate the tray
            tray = None
            t_side, t_row, t_col = -1, -1, -1
            for side in range(2):
                for r in range(N):
                    for c in range(N):
                        if racks[side][r][c] is not None and racks[side][r][c].tray_id == tray_id:
                            tray = racks[side][r][c]
                            t_side, t_row, t_col = side, r, c
                            break
