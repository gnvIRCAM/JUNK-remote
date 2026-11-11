import json
import os
import random
import typing as tp

from .types import AppPages

class Knobs:
    """
    A data model for the knobs.
    """
    def __init__(self):
        self.values = {
            "A": {str(i): 0.0 for i in range(8)}, 
            "B": {str(i): 0.0 for i in range(8)}
        }
        self.active_layer: tp.Literal["A", "B"] = "A"
    
    def switch_layer(self) -> None:
        """
        Switches the active layer between A and B.
        """
        self.active_layer = "B" if self.active_layer == "A" else "A"
        
    def set(self, index: int, value: float) -> None:
        """
        Sets the value of the knob at the given index in the active layer.
        """
        self.values[self.active_layer][str(index)] = value

    def get(self, index: int, default: float = 0.0) -> float:
        """
        Gets the value of the knob at the given index in the active layer.
        """
        return self.values[self.active_layer].get(str(index), default)
        
    def reset(self) -> None:
        """
        Resets all knob values to 0.0 in both layers.
        """
        self.values = {
            "A": {str(i): 0.0 for i in range(8)}, 
            "B": {str(i): 0.0 for i in range(8)}
            }
        
    def load(self, patch, preset_index: int) -> None:
        """
        Loads the knob values from a preset file for the given patch and preset index.
        If the preset file does not exist, it will keep the current values.
        """
        preset_path = os.path.join(
            os.environ["PATCHES_PATH"], 
            patch, 
            f"preset_{preset_index}.json"
            )
        if not os.path.exists(preset_path):
            return
        with open(preset_path, "r") as f:
            self.values = json.load(f)

    def save(self, patch: str, preset_index: int) -> None:
        """
        Saves the knob values to a preset file for the given patch and preset index.
        Existing files will be overwritten.
        """
        preset_path = os.path.join(
            os.environ["PATCHES_PATH"], 
            patch, 
            f"preset_{preset_index}.json"
            )
        with open(preset_path, "w", encoding='utf-8') as f:
            json.dump(self.values, f, indent=2)
            
    def randomize(self) -> None:
        """
        Randomizes the knob values in the active layer.
        """
        self.values[self.active_layer] = {str(i): random.uniform(0.0, 1.0) for i in range(8)}
            
    def display(self, page: AppPages) -> tp.Dict[int, str]:
        """
        Returns a dictionary representation of the knob values for both layers.
        """
        if page == "menu":
            return {i: "0" for i in range(8)}
        else:
            return {i: f"{self.values[self.active_layer][str(i)]}" for i in range(8)}