
import math
import os 
from pythonosc import udp_client
import time
import typing as tp
import subprocess
import sys

from .types import AppPages
from .data import Knobs

NUM_PRESETS = 16
SCRIPTS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scripts")
PD_STARTUP_DELAY = 0.5  # seconds to let pd open its OSC port before sending values


def _get_num_files(dir: str) -> int:
    """
    Returns the number of files in the given directory.
    """
    try:
        return len(os.listdir(dir))
    except FileNotFoundError:
        return 0

class Server:
    def __init__(self):
        self.menu_index: int = 0 # Currently selected patch
        self.preset_index: int = 0 # If a patch is loaded : currently selected preset (-1 = back to main menu)
        self.num_presets = NUM_PRESETS
        self.patches_path = os.environ["PATCHES_PATH"]
        self.page: AppPages = "menu" # "menu" or "patch"
        self.osc_client = udp_client.SimpleUDPClient(
                    "127.0.0.1", 
                    5005, 
                    timeout=10
                    )
        self.knobs: Knobs = Knobs(self.osc_client)
        self.pd_process: tp.Optional[subprocess.Popen] = None


    def get(self, page: AppPages) -> tp.Tuple[int, str]:
        """
        Returns the current index (menu_index or preset_index) depending on the page.
        Returns both the index and a string description
        """
        if page == "menu":
            _patches = sorted(
                d for d in os.listdir(self.patches_path) if os.path.isdir(os.path.join(self.patches_path, d))
                )    
            if not len(_patches): 
                return self.menu_index, "No patches found"
            patch_name = _patches[self.menu_index].split('/')[-1]
            return self.menu_index, patch_name
        else:
            if self.preset_index < 0:
                return -1, "menu"
            return self.preset_index, f"Preset {self.preset_index+1}"
    
    
    @property
    def patch_name(self) -> str:
        """
        Name of the currently selected patch
        """
        return self.get("menu")[1]
    
    
    @property
    def knob_values(self) -> tp.List[float]:
        """
        Returns the current knob values (8 floats, 0..1)
        """
        return [float(x) for x in self.knobs.display(self.page).values()]
    
    @property
    def num_patches(self) -> int:
        """
        Returns the number of patches in the patches folder.
        """
        return _get_num_files(self.patches_path)


    def switch_page(self) -> None:
        """
        Switches the page between "menu" and "patch".
        """
        self.knobs.reset()
        if self.page == "menu": # Loading a patch 
            self.page = "patch"
            self.load_patch()
        else:
            self.preset_index = 0 # Going back to the menu
            self.page = "menu"
            self.close_patch()
        
        
    def display(self) -> tp.Dict[str, tp.Any]:
        knobs_display = self.knobs.display(self.page)
        if self.page == "menu":
            title = "Patches"
            subtitle = self.patch_name
            button_names = {0: "Load patch", 1: "", 2: "", 3: ""}
        else:
            title = self.patch_name
            subtitle = f"Preset {self.preset_index+1}" if self.preset_index >= 0 else "Menu"
            button_names = {0: "Load", 1: "Write", 2: "Switch layer", 3: "Randomize"}
        return {
            "title": title,
            "subtitle": subtitle,
            "buttons": button_names,
            "knobs": knobs_display
        }
            
        
    def handle_button_click(self, button_idx: int) -> tp.Dict[str, tp.Any]:
        """
        Handles a button click event. \\
        If the current state is "menu": loads the patch indexed by self.patch_index and sets the state to "patch". \\
        If the current state is "patch" and self.preset_index is in [0, num_presets-1]: loads selected preset \\
        If the current state is "patch" and self.preset_index is -1: returns to the menu
        """
        if button_idx==0 : # Load patch / Load preset / Go back to menu 
            if self.page == "menu" or (self.page == "patch" and self.preset_index == -1): # Load patch / Go back to menu
                self.switch_page()
            else: # Load preset
                self.knobs.load(self.patch_name, self.preset_index)
            return self.display()

        
        if self.page != "patch":
            return self.display()
         
        match button_idx: 
            case 1:
                self.knobs.save(self.patch_name, self.preset_index)
            
            case 2:           
                self.knobs.switch_layer() # Note : could also be used in the menu to switch between patches categories (transfer, autonomous)

            case 3:
                self.knobs.randomize()
            
        return self.display()
        
        
    def handle_knob_turn(self, index: int, value: float) -> tp.Dict[str, tp.Any]:
        """
        Converts a wheel turn into an increment or decrement of the index.
        """
        self.knobs.set(index, value)
        return self.display()
    
    
    def handle_wheel_turn(self, value: float) -> tp.Dict[str, tp.Any]:
        """
        Converts a wheel turn into an increment or decrement of the index.
        """
        match self.page:
            case "menu":
                self.menu_index = math.ceil(value * (self.num_patches-1)) # 0...NUM_PATCHES-1
            case "patch":
                _preset_index = math.ceil(value * (self.num_presets)) # 0...NUM_PRESETS
                self.preset_index = _preset_index - 1
        return self.display()
    
    
    def load_patch(self) -> None:
        """
        Launches the currently selected patch in Pure Data (via scripts/load_patch.sh),
        then loads its first preset.
        """
        self.close_patch()  # never run two patches at once

        patch_dir = os.path.join(self.patches_path, self.patch_name)
        if not os.path.isdir(patch_dir):
            print(f"[server] patch folder not found: {patch_dir}", file=sys.stderr)
            self.page = "menu"
            return

        self.pd_process = subprocess.Popen(
            ["bash", os.path.join(SCRIPTS_PATH, "load_patch.sh"), patch_dir],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )

        time.sleep(PD_STARTUP_DELAY)
        if self.pd_process.poll() is not None:  # script/pd exited immediately
            err = self.pd_process.stderr.read().decode() if self.pd_process.stderr else ""
            print(f"[server] failed to load patch '{self.patch_name}': {err}", file=sys.stderr)
            self.pd_process = None
            self.page = "menu"
            return

        self.preset_index = 0

    def close_patch(self) -> None:
        """
        Stops the running Pure Data process (via scripts/close_patch.sh).
        """
        if self.pd_process is None:
            return
        if self.pd_process.poll() is None:
            subprocess.run(
                ["bash", os.path.join(SCRIPTS_PATH, "close_patch.sh"), str(self.pd_process.pid)],
                check=False,
            )
        try:
            self.pd_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.pd_process.kill()
        self.pd_process = None


    
    
    
    
# client.send_message("/filter", random.random())
# time.sleep(1)