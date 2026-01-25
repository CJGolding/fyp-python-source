import logging

from InquirerPy import inquirer

from backend.time_sensitive_game_manager import TimeSensitiveGameManager
from backend.unrestricted_game_manager import UnrestrictedGameManager

LOG: logging.Logger = logging.getLogger(__name__)


def get_matchmaking_options() -> dict:
    return {
        "message": "Select matchmaking mode: ",
        "choices": [
            {"name": "Unrestricted Queue System", "value": UnrestrictedGameManager},
            {"name": "Time-Sensitive Queue System", "value": TimeSensitiveGameManager},
            {"name": "Exit", "value": exit}
        ]
    }


def get_player_insertion_options() -> dict:
    return {
        "message": "Select action: ",
        "choices": [
            {"name": "Insert Player", "value": "insert_players_manually"},
            {"name": "Insert Players in Bulk", "value": "insert_players_automatically"},
            {"name": "Start Matchmaking", "value": "start_matchmaking"},
            {"name": "View Steps", "value": "view_steps"},
            {"name": "Exit", "value": "exit"}
        ]
    }

def init_matchmaking_system(system_class):
    while True:
        config = {"team_size": int(inquirer.number(
            message="Enter team size: ",
            min_allowed=1,
            max_allowed=5,
            default=2
        ).execute()), "p_norm": float(inquirer.number(
            message="Enter fairness norm (p): ",
            min_allowed=1.0,
            default=1.0,
            float_allowed=True
        ).execute()), "q_norm": float(inquirer.number(
            message="Enter uniformity norm (q): ",
            min_allowed=1.0,
            default=1.0,
            float_allowed=True
        ).execute()), "fairness_weight": float(inquirer.number(
            message="Enter fairness weight (α): ",
            min_allowed=0.0,
            default=0.1,
            float_allowed=True
        ).execute())}
        if system_class == TimeSensitiveGameManager:
            config["queue_weight"]: float = float(inquirer.number(
                message="Enter queue weight (β): ",
                min_allowed=0.0,
                default=0.1,
                float_allowed=True
            ).execute())
        config["is_recording"] : bool = inquirer.confirm(
            message="Enable recording of steps and statistics?",
            default=True
        ).execute()
        config["approximate"]: bool = inquirer.confirm(
            message="Enable approximate matching?",
            default=False
        ).execute()
        try:
            return system_class(**config)
        except ValueError:
            LOG.error("Invalid input parameters. Please try again.")
            continue

def start_matchmaking_loop(system):
    while True:
        option: str = inquirer.select(**get_player_insertion_options()).execute()
        if option == "insert_players_manually":
            skill_level: int = inquirer.number(
                message="Enter player skill level: ",
                min_allowed=0,
                default=1500
            ).execute()
            system.insert_player_manually(skill_level)
        elif option == "insert_players_automatically":
            num_players: int = inquirer.number(
                message="Enter number of players to insert: ",
                min_allowed=1,
                default=10
            ).execute()
            mean = inquirer.number(
                message="Enter mean skill level: ",
                min_allowed=0,
                default=1500
            ).execute()
            std_dev = inquirer.number(
                message="Enter standard deviation of skill levels: ",
                min_allowed=0,
                default=200
            ).execute()
            system.insert_players_automatically(num_players, mean, std_dev)
        elif option == "start_matchmaking":
            system.create_match()
        elif option == "view_steps":
            if system.recorder:
                for index, step in enumerate(system.recorder.get_steps()):
                    LOG.info(f"Step {index + 1}: {step}")
            else:
                LOG.info("Recording is disabled. No steps to display.")
        elif option == "exit":
            break


def run():
    """Run the matchmaking system via CLI."""

    system_class = inquirer.select(**get_matchmaking_options()).execute()
    if system_class == exit:
        return

    system = init_matchmaking_system(system_class)
    start_matchmaking_loop(system)

    if system.recorder:
        for stat_name, stat_value in system.recorder.get_stats().items():
            LOG.info(f"{stat_name}: {stat_value}")
    LOG.info(f"Total matches created: {len(system.created_matches)}")
    LOG.info(f"Final player queue size: {len(system.players)}")
