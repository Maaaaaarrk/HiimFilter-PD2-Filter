type 00-Hiim_Top.filter 01-Version.filter 02-Hiim_Top.filter 02-Hiim_Top-End.filter 03-alias-general.filter 03-PD2_items.filter 04-Ubermats.filter 05-Maps.filter 06-Gems.filter 07-Runes.filter 07-Runes-ToolTip.filter 08-Potions.filter 09-QuestItems.filter 10-Formatted_MagRare_Names.filter 11-Formatted_MagRare_All.filter 12-Unid_MagRare.filter 13-Formatted_MagicRare.filter 14-RingAmuJewelPts.filter 15-Formatted_Charms.filter 16-Tags_All.filter 17-Tags_LLD.filter 18-Unid_UniquesSet_Name.filter 19-Tags_Unid_UniquesSet.filter 20-Unid_UniquesSet_Tiers.filter 20-Unid_UniquesSet_Tiers_Hides.filter 21-Tags_Weap_range.filter 22-Tags_Shopping.filter 23-Tags_Crafting_Unid.filter 24-Tags_Crafting_Id.filter 25-Nmag_TopFilter.filter 26-Nmag_Staffmod.filter 27-Tags_Nmag_Sockets.filter 28-Tags_Nmag_runewords.filter 29-Tags_Nmag_bases.filter 30-Tags_Sockets_Upgrading.filter 31-Leveling.filter 32-Footer.filter 33-Gambleing.filter > "..\Hiim_Closed_Beta.filter"

@echo off
setlocal enabledelayedexpansion

:: === Configuration ===
set "sourceFile=README.md"
set "keyword={{REPLACE_ME}}"
set "replacementFile=01-Version.filter"
set "finalFile=..\README.md"

:: === Read the replacement text into a variable ===
set "replacementText="
for /f "usebackq delims=" %%A in ("%replacementFile%") do (
    set "line=%%A"
    set "line=!line:%%CL%%= !"
    set "replacementText=!replacementText!!line!\n"
)

:: Remove trailing newline
set "replacementText=!replacementText:~0,-2!"

:: === Replace keyword with replacement text and &&& with ! ===
(
    for /f "usebackq delims=" %%A in ("%sourceFile%") do (
        set "line=%%A"
        set "line=!line:%keyword%=%replacementText%!"
        set "line=!line:&&&=!"
        echo !line!
    )
) > "%finalFile%"
echo Done. Replaced "%keyword%" and replaced "&&&" with "!" in "%finalFile%".