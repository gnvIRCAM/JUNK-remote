## Installation and use 
To run the server, run the following command: 
```bash 
uv run fastapi dev
```

NOTE : in order for this to work, you must set an environment variable on the pi for the location of the Pd patches: 

```bash 
export PATCHES_PATH=/path/to/patches 
```

We advise to set this permanently, by running:

```bash 
sudo -H vim /etc/environment
```

and adding ``` PATCHES_PATH = /path/to/patches ``` to this file. Note that we added a fake folder for development purposes, at ``` backend/src/dummy_patches ``` 