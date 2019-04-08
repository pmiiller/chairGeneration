# CMPT 464 Final Project - Chair Generation

Download the LeChairs scorer from [here](https://drive.google.com/file/d/19p7GjhSbcBYy6VUbuMHugcqD1tkQfl6-/view).

Instructions for setting up PyMesh can be found [here](settingUpPymesh.txt).

Requirements:
 - Python 3.*
 - [PyMesh](https://pymesh.readthedocs.io/en/latest/#)
 - [LeChairs](https://drive.google.com/file/d/19p7GjhSbcBYy6VUbuMHugcqD1tkQfl6-/view)
     - Modified versions of the LeChairs training and evaluation scripts are already included in the repo
     - `checkpoint/` and `chairs-data` directories from LeChairs (or some modified versions of the two) need to be placed in the root directory of the project
 - [Trimesh](https://trimsh.org/trimesh.html#github-com-mikedh-trimesh)
 	 - Installation:
 	 	- `pip3 install trimesh`
 	 	- show() requires pyglet: `pip3 install pyglet`
 	 	- trimesh.registration package requires rtree `pip3 install rtree`, `sudo apt install python3-rtree`
