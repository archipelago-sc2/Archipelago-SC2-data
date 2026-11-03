# SC2 Archipelago Map and Mod data
This repo contains the required StarCraft2 map and mod data for Archipelago

## Dev setup
For the client to start a map, the map and mod dependencies must be in the Starcraft 2 install directory,
under the Maps/ and Mods/ folders respectively.

### Building a local download package
Maps and Mods are packaged by the `build_release_package.sh` command,
which requires the `parallel` and `smpq` apt packages to run.
If building on Windows, this must be run through the Windows Subsystem for Linux (WSL) terminal.

One-time setup:
```sh
sudo apt install parallel
sudo apt install smpq
```

For every build:
```sh
./build_release_package.sh
```

### Fast mod deployment
Only the map files are actually packaged, the mod files are simply copied over.
It may be helpful to create a symlink or create a script to copy files over to deploy mod files quickly.
Note that if the source files are symlinked directly to the target Mods/ directory, then `/download_data`
may overwrite all changes to the source code.

```sh
SC2_MODS_DIR=/path/to/sc2/install/Mods
rm -rf "$SC2_MODS_DIR/Archipelago*.SC2Mod"
cp -r ./Mods/* "$SC2_MODS_DIR"
```

## Licensing
- Original maps are owned by Blizzard®.
- This mod contains original Blizzard® assets for mod compatibility reasons.
    These are part of the base game. 
    They're licensed by their terms.
- This mod contains some assets and code from SCEvoComplete mod. See their license. See 
    - Dropship SCBW model
    - Valkyrie SCBW model
    - Overlord SCBW (Yggdrasil) model
- This mod contains some assets created by Enoki, including but not limited to:
    - Royal Guard Banshee (Night Hawk) model
    - Royal Guard Marine (Son of Korhal) model
    - Royal Guard Goliath (Bulwark Company) model
    - Royal Guard Medic (Field Respone Theta) model
    - Royal Guard Wraith (Winged Nightmare) model
    - Nerazim High Templar (Signifier) model
    - Various ability/upgrade icons
    See their license.
- This mod contains some assets created by Subsourian, including but not limited to:
    - Various ability/upgrade icons
    See their license.
- This mod contains some assets created by DaveSpectre, including but not limited to:
    - Purifier Mothership assets
    - Various ability/upgrade icons
    - Infested Diamondback portrait
    - Infested Liberator portrait
    - Infested Medic portrait/model
    - Infested SCV portrait
    - Brood Queen portrait
    See their license.
- This mod contains some assets created by Redfrog, including but not limited to:
    - UI elements for multi-hero missions
    See their license.
- This mod contains some assets created by 321, including but not limited to:
    - UI elements for supporting half-supply units
    See their license.
- This mod contains some assets created by Trigonomicon, including:
	- Launch Bay warp in model
	- Psi Spire warp in model
	See their license.
- This mod contains some assets created by AlleyV. See their license.
- This mod contains some assets created by SoulFilcher. See their license. 
- This mod contains some assets created by Solstice245. See their license.
- This mod uses the Archipelago logo created by Krista Corkos and Christopher Wilson. See their license.
- All third-party licenses are under [Mods/ArchipelagoPlayer.SC2Mod/3rdpartyLicenses/](Mods/ArchipelagoPlayer.SC2Mod/3rdpartyLicenses/)
- Otherwise, MIT license shall apply, see [LICENSE](LICENSE)

Blizzard is a registered trademark of Blizzard Entertainment, Inc.  
Wings of Liberty and StarCraft are a trademarks or registered trademark of Blizzard Entertainment, Inc., in the U.S. and/or other countries.
