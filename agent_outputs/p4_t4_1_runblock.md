# RUN-BLOCK [T4.1] — Earthdata token + .netrc setup

**Hedef ortam**: Colab / Yerel Python (Windows veya Linux)
**Önkoşul**: Internet, urs.earthdata.nasa.gov hesabı
**Süre**: ~30 dk (hesap açık ise ~5 dk)
**Asenkron**: HAYIR — T4.2 başlamadan bitmesi lazım.

## Adımlar

1. **Hesap açma** (yoksa):
   https://urs.earthdata.nasa.gov/users/new

2. **Uygulama yetkilendirme**: Profile → Authorized Apps. Şunları "Authorize":
   - LP DAAC Data Pool
   - NASA GESDISC DATA ARCHIVE
   - Earthdata Search

3. **`.netrc` dosyası oluştur** (Windows PowerShell):
   ```powershell
   $u = "<EARTHDATA_USERNAME>"
   $p = "<EARTHDATA_PASSWORD>"
   $netrc = "machine urs.earthdata.nasa.gov`n    login $u`n    password $p"
   $path = "$env:USERPROFILE\.netrc"
   $netrc | Out-File -FilePath $path -Encoding ascii -NoNewline
   icacls $path /inheritance:r /grant:r "$($env:USERNAME):(R)"
   New-Item -ItemType File -Path "$env:USERPROFILE\.urs_cookies" -Force | Out-Null
   ```

   Linux/Colab:
   ```bash
   cat > ~/.netrc <<EOF
   machine urs.earthdata.nasa.gov
       login <USER>
       password <PASS>
   EOF
   chmod 600 ~/.netrc
   touch ~/.urs_cookies && chmod 600 ~/.urs_cookies
   ```

4. **Doğrulama**:
   ```bash
   curl -n -L -c ~/.urs_cookies -b ~/.urs_cookies \
        -o /tmp/edl.html https://urs.earthdata.nasa.gov/profile
   grep -q "Earthdata" /tmp/edl.html && echo OK
   ```

5. **CMR ping**:
   ```bash
   python -c "import requests; r=requests.get('https://cmr.earthdata.nasa.gov/search/collections.json?short_name=AST_L1T'); print(r.status_code)"
   ```
   Beklenen: `200`

## VERIFY-BLOCK [T4.1]
Bana yapıştır:
- `ls -la ~/.netrc` çıktısı (mode `-rw-------`)
- `curl -n https://urs.earthdata.nasa.gov/profile -I` ilk satırı (`HTTP/2 200` veya 302)
- CMR ping status kodu
- LP DAAC authorized listesinin ekran görüntüsü

## DELIVER
```
[P4] T4.1 TAMAM
Çıktı: ~/.netrc, ~/.urs_cookies (mode 600)
Sanity: ✅ Earthdata profile 200, ✅ CMR ping 200, ✅ LP DAAC authorized
Sıradaki bağımlı: T4.2 ASTER L1B indirme başlar
```
