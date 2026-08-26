pyinstaller src/main.py ^
    --clean ^
    --name Authenstickator ^
    --icon="src/ui/view/res/logo.ico" ^
    --add-data "src/config/config.json;src/config" ^
    --add-data "src/ui/view;ui/view" ^
    --add-data "src/ui/script;ui/script" ^
    --paths . ^
    --distpath "%TEMP%\authenstickator\dist" ^
    --workpath "%TEMP%\authenstickator\build"