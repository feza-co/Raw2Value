# Commit Discipline

Bu proje için commit'ler aşağıdaki kurallara KESİNLİKLE uymak zorundadır.

## 1. Atomic Commit
- Her commit tek bir mantıksal değişiklik içermelidir.
- Birden fazla iş bir commit'te birleştirilmez; her biri ayrı commit olur.
- Bir commit, geri alındığında sadece kendi değişikliğini geri almalıdır.
- Refactor + feature + fix aynı commit'te olmaz; ayrılır.

## 2. Claude İmzası YASAK
- Commit mesajlarında `Co-Authored-By: Claude` satırı **KESİNLİKLE** bulunmamalıdır.
- `🤖 Generated with Claude Code` veya benzeri ibareler **KULLANILMAZ**.
- Hiçbir AI/asistan imzası, etiketi, emoji veya referansı eklenmez.
- Footer'da, body'de veya başlıkta hiçbir yerde geçmez.

## 3. Sade ve Net Açıklama
- Commit mesajı kısa, açık ve doğrudan olmalıdır.
- Başlık 70 karakteri geçmez.
- Format: `<tür>: <ne yapıldı>`
- Türler: `add`, `fix`, `update`, `remove`, `refactor`, `docs`, `test`, `style`, `chore`
- Mesajda gereksiz dolgu, pazarlama dili veya emoji olmaz.
- "Why" gerekiyorsa body'de 1-2 cümle ile açıklanır; "what" başlıkta yeterlidir.

### Örnekler
İyi:
```
fix: login redirect after session expiry
add: user profile avatar upload
refactor: extract auth middleware
remove: unused legacy api client
```

Kötü:
```
fix bug                              # belirsiz
Updated some files                   # ne, neden?
feat: ✨ amazing new feature 🚀      # emoji, dolgu
fix: bug + refactor + new endpoint   # atomic değil
```

## 4. Commit Komutu
Her commit aşağıdaki şablon ile atılır. HEREDOC kullanılmaz, imza eklenmez:

```bash
git commit -m "<tür>: <kısa açıklama>"
```

Detay gerekiyorsa:
```bash
git commit -m "<tür>: <kısa açıklama>" -m "<gerekçe veya bağlam — 1-2 cümle>"
```

## 5. Staging
- Dosyalar isimle eklenir: `git add path/to/file`.
- `git add .` veya `git add -A` **kullanılmaz** (sızıntı riski).
- `.env`, credential, secret, büyük binary dosyalar commit edilmez.

## 6. Yapılmayacaklar
- `git commit --amend` ile yayımlanmış (push edilmiş) commit değiştirilmez.
- `--no-verify` ile pre-commit hook atlanmaz; hook fail olursa kök sebep çözülür.
- `--no-gpg-sign` ile imza atlanmaz.
- `git push --force` main/master'a yapılmaz.
- `git reset --hard`, `git clean -f`, `git checkout .` kullanıcı izni olmadan çalıştırılmaz.

## 7. Hook Fail Durumu
Pre-commit hook fail ederse:
1. Commit OLUŞMADI; `--amend` kullanma (önceki commit'i bozar).
2. Hatayı oku, kök sebebi düzelt.
3. Düzeltmeyi `git add <dosya>` ile stage'le.
4. **YENİ** commit oluştur (eski mesajla).

## 8. Pull Request
- PR başlığı 70 karakter altı, commit başlıklarıyla aynı dilde.
- PR body'sine Claude imzası, "Generated with" satırı eklenmez.
- Test plan checklist'i body'de yer alır.

## Özet Kural
Her commit: **atomic + imzasız + sade**. Bu üç şarttan biri eksikse commit atılmaz.
