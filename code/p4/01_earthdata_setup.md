# T4.1 — NASA Earthdata Token Setup (P4 Spektral Mühendis)

> Hedef: ASTER L1B sahnelerini CMR API üzerinden indirebilmek için kullanıcı kimlik
> bilgilerini `.netrc` dosyasına yerleştirmek. Bu adım **insan tarafından bir kez**
> yapılır. P4 ajanı yalnızca talimatları üretir.

---

## 1. Earthdata hesabı

1. https://urs.earthdata.nasa.gov/users/new adresine gidin.
2. Form alanlarını doldurun. Şu uygulamaları **explicit olarak yetkilendirin**
   (Profile → Applications → Authorized Apps):
   - `NASA GESDISC DATA ARCHIVE`
   - `LP DAAC Data Pool`        ← ASTER L1B bu DAAC üzerinden geliyor
   - `Earthdata Search`
   - `Common Metadata Repository (CMR) API`

   Uygulama yetkisi verilmezse `curl` 401 döner ve script sessizce boş `.hdf` üretebilir.

## 2. `.netrc` dosyası (Windows)

PowerShell:
```powershell
$netrc = @"
machine urs.earthdata.nasa.gov
    login YOUR_EARTHDATA_USERNAME
    password YOUR_EARTHDATA_PASSWORD
"@
$netrcPath = "$env:USERPROFILE\.netrc"
$netrc | Out-File -FilePath $netrcPath -Encoding ascii -NoNewline
icacls $netrcPath /inheritance:r /grant:r "$($env:USERNAME):(R)"
```

> Windows'ta dosya `C:\Users\<USER>\.netrc` veya `_netrc` olabilir. `curl` her ikisini
> de okur; yine de `.netrc` öneriyoruz (Linux/macOS uyumu için).

## 3. `.netrc` dosyası (Linux / Colab / WSL)

```bash
cat > ~/.netrc <<'EOF'
machine urs.earthdata.nasa.gov
    login YOUR_EARTHDATA_USERNAME
    password YOUR_EARTHDATA_PASSWORD
EOF
chmod 600 ~/.netrc
```

`chmod 600` zorunlu; daha gevşek izinlerde `curl` `.netrc`'yi reddeder.

## 4. `.urs_cookies` (LP DAAC için gerekli)

LP DAAC redirect zinciri çerez tutmadan kırılır:

```bash
touch ~/.urs_cookies
chmod 600 ~/.urs_cookies
```

Windows için:
```powershell
New-Item -ItemType File -Path "$env:USERPROFILE\.urs_cookies" -Force | Out-Null
```

## 5. Doğrulama

Aşağıdaki komut başarıyla `Welcome to Earthdata Login` HTML'i döndürmelidir:

```bash
curl -n -L -c ~/.urs_cookies -b ~/.urs_cookies \
     -o /tmp/edl_test.html \
     "https://urs.earthdata.nasa.gov/profile"
grep -q "Earthdata Login" /tmp/edl_test.html && echo "OK" || echo "FAIL"
```

Küçük bir CMR sorgusu (kimlik gerektirmeyen, sadece bağlantı testi):

```bash
curl -s "https://cmr.earthdata.nasa.gov/search/granules.json?short_name=AST_L1T&page_size=1" \
     | python -c "import sys, json; d=json.load(sys.stdin); print('granules:', len(d['feed']['entry']))"
```

## 6. Çevre değişkeni alternatifi (CI / Colab)

`.netrc` koyamadığınız ortamlarda:

```bash
export EARTHDATA_USER="..."
export EARTHDATA_PASS="..."
```

`02_aster_l1b_download.py` her ikisini de destekler (önce `.netrc`, sonra env-var).

## 7. Sanity checklist

- [ ] `~/.netrc` mevcut, mode 600
- [ ] `~/.urs_cookies` mevcut, mode 600
- [ ] `LP DAAC Data Pool` uygulaması "Authorized" listesinde
- [ ] `curl -n -L https://e4ftl01.cr.usgs.gov/ASTT/AST_L1T.003/` → `200 OK`
- [ ] `python -c "import requests; print(requests.get('https://cmr.earthdata.nasa.gov/search/collections.json?short_name=AST_L1T').status_code)"` → `200`

Tüm `[x]` olduğunda T4.2 çalıştırılabilir.
