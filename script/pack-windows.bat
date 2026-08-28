pyinstaller src/main.py ^
    --clean ^
    --name Authenstickator ^
    --icon="src/view/html/res/logo.ico" ^
    --noconsole ^
    --add-data "src/model/config/config.json;src/model/config" ^
    --add-data "src/view;src/view" ^
    --paths . ^
    --distpath "%TEMP%\authenstickator\dist" ^
    --workpath "%TEMP%\authenstickator\build"