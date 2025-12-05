from utils.loading_animation import main as loading_animation
from utils.turn_all_off import turn_all_off

def main():
    turn_all_off()
    loading_animation()
    turn_all_off()
    
if __name__ == "__main__":
    main()