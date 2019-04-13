# CMPT 464 Final Project - Chair Generation

Github link: https://github.com/pmiiller/chairGeneration

## Instructions
 - Run `python clean_meshes.py` in order to clean the training data
  - Must be run before anything else!
 - `python main.py` to generate a single chair with a random template
 - `python main.py <chairDirectoryName>` to generate a single chair with a specified template
 - `python main.py all` to generate a chair for all templates and then score them
 - `python main.py eval` to evaluate a sample of already generated chairs
 - `python main.py load` to load all templates again and create a new pickle file
 - `python main.py cluster` to create clustering of the parts and create a new pickle file of parts
 - `python main.py scorer` to run the validation for the scorer
   - This runs the evaluation script on chairs generated using our method which we separated into two sets; "good" chairs and "bad" chairs. Good chairs on average should have a higher score than bad chairs.
 - **Important**: After running `scorer` or modifying the input chair data, you need to empty the `new_chair_bmp`, `new_chair_obj`, and `ranked_chair_obj` folders before running `all` or the jupyter notebook. Not doing so may lead to unexpected behaviour.


Download the LeChairs scorer from [here](https://drive.google.com/file/d/19p7GjhSbcBYy6VUbuMHugcqD1tkQfl6-/view).

Requirements:
 - Python 3.*
 - [LeChairs](https://drive.google.com/file/d/19p7GjhSbcBYy6VUbuMHugcqD1tkQfl6-/view)
     - Modified versions of the LeChairs training and evaluation scripts are already included in the repo
 - [Trimesh](https://trimsh.org/trimesh.html#github-com-mikedh-trimesh)
 	 - Installation:
 	 	- `pip3 install trimesh`
 	 	- show() requires pyglet: `pip3 install pyglet`
 	 	- trimesh.registration package requires rtree `pip3 install rtree`, `sudo apt install python3-rtree`
 - Run `pip3 install -r requirements` to install the needed pip requirements
