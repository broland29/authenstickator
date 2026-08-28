pyinstaller src/main.py \
    --clean \
    --name Authenstickator \
    --add-data "src/model/config/config.json:src/model/config" \
    --add-data "src/view:view" \
    --paths . \
    --distpath /tmp/authenstickator/dist \
    --workpath /tmp/authenstickator/build