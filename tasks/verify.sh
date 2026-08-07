#!/bin/bash
# ToyScout — gorev ve hatirlatma dogrulamasi.
#   bash tasks/verify.sh
#
# tasks/TASKS.md'de YAZAN ile makinede GERCEKTE olani karsilastirir.
# Kayit dogru gorunse bile ajan yuklu degilse burasi yakalar.

cd "$(dirname "$0")/.." || exit 1
SITE="$PWD"
LA="$HOME/Library/LaunchAgents"
ok=0; bad=0

c_g="\033[32m"; c_r="\033[31m"; c_y="\033[33m"; c_0="\033[0m"; c_b="\033[1m"

hr() { printf '%s\n' "------------------------------------------------------------"; }
pass() { printf "  ${c_g}✓${c_0} %s\n" "$1"; ok=$((ok+1)); }
fail() { printf "  ${c_r}✗${c_0} %s\n" "$1"; bad=$((bad+1)); }
warn() { printf "  ${c_y}!${c_0} %s\n" "$1"; }

printf "\n${c_b}ToyScout — gorev durumu${c_0}   %s\n" "$(date '+%Y-%m-%d %H:%M')"
hr

check_agent() {
  local label="$1" plist="$2" script="$3" logf="$4" desc="$5" max_gun="$6"
  printf "\n${c_b}%s${c_0}  — %s\n" "$label" "$desc"

  [ -f "$LA/$(basename "$plist")" ] && pass "plist var" || fail "plist YOK: $plist"

  if launchctl list 2>/dev/null | grep -q "$label"; then
    local st
    st=$(launchctl list | awk -v l="$label" '$3==l {print $2}')
    if [ "$st" = "0" ] || [ -z "$st" ]; then
      pass "launchd'ye yuklu (son cikis: ${st:-yok})"
    else
      fail "launchd'ye yuklu ama son calisma HATA verdi (exit=$st)"
    fi
  else
    fail "launchd'ye YUKLU DEGIL -> launchctl load $plist"
  fi

  # yol "/" ile basliyorsa mutlak kabul et (launchd'nin gercekten calistirdigi dosya
  # proje disinda olabilir — bkz. net.toyscout.gsc / Application Support)
  case "$script" in /*) script_p="$script";; *) script_p="$SITE/$script";; esac
  case "$logf"  in /*) logf_p="$logf";;    *) logf_p="$SITE/$logf";;   esac

  [ -f "$script_p" ] && pass "script var: $script" || fail "script YOK: $script"

  # ── launchd ajani GERCEKTEN tetiklendi mi?
  # Log'un son satirina BAKMA: log'a ajan disindaki kod yollari da yazabiliyor
  # (ornek: bestseller_sync'in Supabase ping'i). 7 Agu 2026'da tam bu oldu —
  # ajan 30 Tem'den beri hic calismamisken log 31 Tem tarihli bir ping satiri
  # tasidigi icin burasi "son calisma: 31 Tem" deyip YESIL veriyordu.
  # Tek guvenilir kanit: launchctl'in "runs" sayaci + stdout log'unun mtime'i.
  local runs
  runs=$(launchctl print "gui/$(id -u)/$label" 2>/dev/null | awk '/^\truns = /{print $3}')
  if [ -n "$runs" ]; then
    pass "launchd runs sayaci: $runs"
  else
    warn "launchctl print 'runs' vermedi (eski macOS?)"
  fi

  # Ajanin kendi stdout log'u varsa gercek son calisma zamani odur.
  local stdout_p="${script_p%.py}.stdout.log"
  if [ -f "$stdout_p" ]; then
    local m mgun
    m=$(date -r "$stdout_p" '+%Y-%m-%d %H:%M')
    mgun=$(( ( $(date +%s) - $(stat -f %m "$stdout_p") ) / 86400 ))
    if [ -n "$max_gun" ] && [ "$mgun" -gt "$max_gun" ]; then
      fail "son GERCEK calisma $m ($mgun gun once) — beklenen araligi ($max_gun gun) astI, tur KACIRILMIS"
      warn "elle tetikle: launchctl kickstart -k gui/$(id -u)/$label"
    else
      pass "son gercek calisma: $m ($mgun gun once)"
    fi
  elif [ -f "$logf_p" ]; then
    local last
    last=$(tail -n 40 "$logf_p" | grep -oE '^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9:]{8}' | tail -1)
    [ -n "$last" ] && pass "log son satiri: $last (stdout log yok, dolayli kanit)" \
                   || warn "log var ama tarih okunamadi"
  else
    warn "henuz hic calismamis (log yok: $logf)"
  fi
}

check_agent "net.toyscout.bestsellers" \
  "$LA/net.toyscout.bestsellers.plist" \
  "products/bestseller_sync.py" \
  "products/bestseller_sync.log" \
  "Amazon Best Sellers senkronizasyonu, 5 gunde bir (TAM OTOMATIK)" \
  6

check_agent "net.toyscout.gsc" \
  "$LA/net.toyscout.gsc.plist" \
  "$HOME/Library/Application Support/toyscout/gsc_reminder.sh" \
  "$HOME/Library/Application Support/toyscout/gsc_reminder.log" \
  "Gunluk GSC turu hatirlaticisi, 22:15 (SADECE BILDIRIM)"

# --- katalog tutarliligi
printf "\n${c_b}Katalog${c_0}\n"
N=$(python3 - <<'PY' 2>/dev/null
import json,re
s=open('js/data.js',encoding='utf-8').read()
d=json.loads(re.search(r'window\.TS_DATA\s*=\s*(\{.*\})\s*;$',s,re.S).group(1))
print(sum(len(v) for v in d.values()))
PY
)
S=$(grep -c "<url>" sitemap-products.xml 2>/dev/null)
if [ -n "$N" ]; then
  pass "js/data.js gecerli — $N urun"
  if [ "$N" = "$S" ]; then
    pass "sitemap-products.xml eslesiyor — $S URL"
  else
    fail "sitemap UYUMSUZ: katalog $N urun, sitemap $S URL -> sitemap yeniden uretilmeli"
  fi
else
  fail "js/data.js AYRISTIRILAMADI"
fi

B=$(ls js/data.js.bak-* 2>/dev/null | wc -l | tr -d ' ')
pass "$B yedek duruyor (js/data.js.bak-*)"

# --- canli site
printf "\n${c_b}Canli site${c_0}\n"
L=$(curl -s --max-time 20 "https://www.toyscout.net/js/data.js?cb=$RANDOM" | grep -o '"asin"' | wc -l | tr -d ' ')
if [ "$L" = "$N" ]; then
  pass "canli katalog guncel — $L urun"
else
  warn "canli $L urun, yerelde $N urun -> DEPLOY EDILMEMIS degisiklik var"
fi

# --- Supabase analitik
# Ucretsiz plan ~7 gun hareketsizlikte projeyi DURAKLATIYOR; duraklayinca sbInsert()
# sessizce basarisiz olur ve tiklama/mesaj/bulten kayitlari kaybolur. 31 Tem 2026'da
# tam bu olmustu (17 gun veri kaybi). Bkz. tasks/TASKS.md A6.
printf "\n${c_b}Analitik (Supabase)${c_0}\n"
SB_KEY="sb_publishable_3bra6T7gE_JBJ4Ff-_oX2w_CaHMpxmQ"
SB_URL="https://vijagongnjfddhtlwecu.supabase.co/rest/v1/amazon_clicks?select=id&limit=1"
SB=$(curl -s -o /dev/null -w '%{http_code}' --max-time 25 -H "apikey: $SB_KEY" "$SB_URL")
if [ "$SB" = "200" ]; then
  pass "Supabase uyanik (REST 200) — tiklama/form kayitlari yaziliyor"
else
  fail "Supabase yanit $SB — proje DURAKLAMIS olabilir, analitik VE iletisim formu kaybediliyor"
  warn "supabase.com panelinden projeyi Restore et; sonra: bash tasks/verify.sh"
fi

# --- acik isler
printf "\n${c_b}Acik isler${c_0} (tasks/TASKS.md B bolumu)\n"
grep -n '^\- \[ \]' tasks/TASKS.md | sed 's/^\([0-9]*\):- \[ \] /  · /' | cut -c1-100

hr
printf "%b%d gecti%b, " "$c_g" "$ok" "$c_0"
if [ "$bad" -gt 0 ]; then
  printf "%b%d BASARISIZ%b\n\n" "$c_r" "$bad" "$c_0"; exit 1
else
  printf "hata yok\n\n"; exit 0
fi