pyinstaller src/main.py \
    --clean \
    --name Authenstickator \
    --add-data "src/config/config.json:src/config" \
    --add-data "src/ui/view:ui/view" \
    --add-data "src/ui/script:ui/script" \
    --paths . \
    --distpath /tmp/authenstickator/dist \
    --workpath /tmp/authenstickator/build