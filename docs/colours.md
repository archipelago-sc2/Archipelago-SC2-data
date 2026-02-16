# Colours
Noting what colours are used by tooltips for different contexts.

Note colour constants can be defined in fontstyles.sc2style. Use them with `#<constant name>`.

* #FFE303 - "Detector"
* #ffff8a - "Can attack ground and air units"
  * Also "#ColorAttackInfo"
* #ffff8a - "Passive ability"
* #ffff8a - "Enables:" header for lists of unlocked units
* #ffff8a - Unit names (rarely), like "Warp Prisms" in Gravitic Drive. We're moving away from this.
* #ColorTooltipNumber - Key numbers, like +armour or damage amounts in a tooltip
  * Currently #ffff8a
* #ColorTooltipAttribute - Attributes affected by key numbers, like "speed", "armor", "damage", etc
  * Currently #ffff8a
* #FFE303 - "War Council Upgrade"
* #f078ff - Indicates energy drain over time, like for Medic heal or cloaking
* #777777 - Greyed out perks, such as previewed Royal Guard perks
* #64e4fa - "Aiur"
* #32CD32 - "Nerazim"
* #f2bf16 - "Purifier"
* #d40d24 - "Tal'darim"

## Recommendations
* Use `<d ref=""/>` tags whenever possible
  * This automatically highlights values affected by an upgrade
* Highlight word descriptions of magnitude effects, like "doubles"
* Generally don't highlight unit names if the button appears on that unit's command card
* Highlight the primary stat affected by the change, such as "damage", "attack speed", "speed", "armor", etc
