#!/bin/bash
# NOT: BU KOPYA ARTIK CALISMIYOR — yalnizca referans icin duruyor.
# launchd'nin calistirdigi gercek script:
#   ~/Library/Application Support/toyscout/gsc_reminder.sh
# (30 Tem 2026: proje ~/Projects/toyscout'a tasindi, TCC sorunu bitti; bu
#  script yine de disarida tutuldu, projeye bagimli degil.)
# ToyScout — gunluk GSC denetim/indeksleme turu hatirlatmasi.
# launchd: net.toyscout.gsc (her gun 22:15)
#
# GSC turu SCRIPT'LE YAPILAMAZ: Search Console'da "Request indexing" akisi
# Google oturumu acik bir tarayici gerektiriyor, API'siz otomatiklestirilemiyor.
# Bu is yalnizca hatirlatir; turu Claude Code ile yaparsin.
#
# Saat 22:15 bilincli secildi: indeksleme kotasi 24 saat KAYAN pencere
# (takvim gunu degil). Her gun ayni saatte istek gonderilirse ertesi gun
# ayni saatte kota tam dolmus olur. Erken saatte "Quota Exceeded" yiyorsun.

LOG="/Users/ahmet/Downloads/toyscout-master/products/gsc_reminder.log"
echo "$(date '+%Y-%m-%d %H:%M:%S')  GSC turu hatirlatmasi gonderildi" >> "$LOG"

/usr/bin/osascript -e 'display notification "GSC tam denetimi + ~10 indeksleme isteği. Kota penceresi 24 saat kayan — tur bu saatte yapılmalı." with title "ToyScout · GSC günlük tur" sound name "Glass"'
