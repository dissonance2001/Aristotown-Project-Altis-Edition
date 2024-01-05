
# Aristotown: Altis Edition
A customized version of Project Altis that's is heavily based on the predecessor Toontown: Corporate Clash. Although this version of the game may not reflect what comes directly from Clash, it does have very similar features to what Clash has to offer. This game is in no way, shape or form intended to be a Toontown: Corporate Clash mirror or duplicate (it is very far from being so), this version of the game uses various assets from Clash such as select gui panels, cog models, animated cog heads, cog abilities, cog animations, and prop models. 

# ❓ What does Aristotown: Altis Edition have to offer?
- There are currently a total of 128 cogs in this game. New cogs have been added to each department, each department has 14 regular cogs, the rest of the cogs have been filled with managers ranging from the ones seen in clash to a few custom managers made by me. There are Operations Analysts and Field Specialists for each department.
- Executive and Manager cogs have both been implemented working the same as they do in clash. Managers have lure resistance and are completely immune to being fired.
- Governaughts have been added, they have double the amount of health as regular cogs and deal twice the amount of damage.
- Version 2 cogs work the same way they do in clash, having half of the amount of health after the first shell is dead, also dealing 1.5x the amount of damage. Cogs can have more than 2 layers, the health deduction and damage multipliers will stack.
- 99% of the managers from Clash have been added, however most of them do not have their set abilities from Clash.
- The Litigation team with working abilities some mirroring Clash others I have tweaked myself to meet specific needs.
- Legacy managers including, Count Erclaim, Count Erfit (not with the old model), Redd "Heir" Wing and The Witness Stand-In have been added. (Sads is not present.)
- Facility managers are present ingame, however are not placed in their desired locations (yet).
- All cogs will go into "desperation mode" once they reach .3x of their max health, including managers, once they are desperation mode, they will deal twice the amount of damage, this will stack with governaughts, executive and v2 damage multipliers.
- Gag damages mirror what they are in Clash, level 8s have not been added yet but it is on the todo list.
- Trap damage reflects what prestige trap damage is in Clash, prestiges don't exist (yet).
- Zap is present ingame, but needs to be revamped.

## 💻 Windows
Run the [Start.bat](Start.bat) file to launch the game.

## 🐧 Linux
### Gathering Basic Dependencies
##### Arch / Manjaro
```yay -S xorg-server  xterm  libgl  python  openssl  libjpeg  libpng  freetype2  gtk2  libtiff  nvidia-cg-toolkit  openal  zlib  libxxf86dga  assimp  bullet  eigen  ffmpeg  fmodex  libxcursor  libxrandr  git  opencv  libgles  libegl```

##### Debian / Ubuntu / Linux Mint
```sudo apt-get install build-essential xterm pkg-config fakeroot python-dev libpng-dev libjpeg-dev libtiff-dev zlib1g-dev libssl-dev libx11-dev libgl1-mesa-dev libxrandr-dev libxxf86dga-dev libxcursor-dev bison flex libfreetype6-dev libvorbis-dev libeigen3-dev libopenal-dev libode-dev libbullet-dev nvidia-cg-toolkit libgtk2.0-dev libassimp-dev libopenexr-dev mongodb libboost-dev libyaml-cpp-dev```

### Getting Python 2

The First step to get this Source running is obtaining a version of Python 2. The Python we use is located [here](https://github.com/NormalNed/python) but feel free to use the one in your package manager (should be **python2**)

### Installing Pip

Once you get the Python installed you need to type these following commands to install Pip
```bash
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python2 get-pip.py
```

### Installing Pip Dependencies
The next part is to get our Dependencies. Open a Terminal inside of the Stride Project and follow these instructions below.
```bash
pip2.7 install -r requirements.txt
```

### Installing "our" Panda 3D
We use a version of Astron Panda3D that is upstream code from the main repo. To set it up follow these instructions

```bash
git clone https://github.com/NormalNed/panda3d.git
cd panda3d
python2 makepanda/makepanda.py --everything --installer --no-egl --no-gles --no-gles2 --no-opencv --threads=4
sudo python2 makepanda/installpanda.py
sudo ldconfig
```

### Running the Game
Now run the [Start.sh](Start.sh) file to launch the game.
# Aristotown
