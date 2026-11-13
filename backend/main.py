import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.server import Server
from src.types import KnobKind

assert os.environ.get("PATCHES_PATH", None) is not None, "PATCHES_PATH environment variable is not set"

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# HTTP + OSC server
server = Server() 

@app.get("/")
def root():
    return {"message": "Hello World"}

@app.get("/action/button/{idx}/click")
def button_click(idx: int):
    result = server.handle_button_click(idx)
    return result

@app.post("/action/wheel/turn")
def wheel_turn(kind: KnobKind):
    server.handle_wheel_turn(kind.value)

@app.post("/action/knob/{idx}/turn")
def knob_turn(kind: KnobKind):
    server.handle_knob_turn(kind.index, kind.value)
    
@app.get("/get_patch_name")
def get_patch_name():
    return {"patch_name": server.patch_name}
    
@app.get("/state")
def state():
    return {
        "page": server.page,
        "preset": server.preset_index,      # 0..NUM_PRESETS-1
        "knobs": server.knob_values,       # 8 floats, 0..1
        "layer": str(server.knobs.active_layer) # A or B
        }

@app.on_event("shutdown")
def shutdown():
    server.close_patch()