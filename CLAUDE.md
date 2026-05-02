# Proje Kuralları

## Commit Kuralları

Bu proje için commit'ler aşağıdaki kurallara KESİNLİKLE uymak zorundadır:

### 1. Atomic Commit
- Her commit tek bir mantıksal değişiklik içermelidir.
- Birden fazla iş bir commit'te birleştirilmez; her biri ayrı commit olur.
- Bir commit, geri alındığında sadece kendi değişikliğini geri almalıdır.

### 2. Claude İmzası YASAK
- Commit mesajlarında `Co-Authored-By: Claude` satırı **KESİNLİKLE** bulunmamalıdır.
- `🤖 Generated with Claude Code` veya benzeri ibareler **KULLANILMAZ**.
- Hiçbir AI/asistan imzası, etiketi veya referansı eklenmez.

### 3. Sade ve Net Açıklama
- Commit mesajı kısa, açık ve doğrudan olmalıdır.
- Format: `<tür>: <ne yapıldı>` (örn: `fix: login redirect bug`, `add: user profile page`)
- Türler: `add`, `fix`, `update`, `remove`, `refactor`, `docs`, `test`, `style`
- Mesajda gereksiz dolgu, emoji veya pazarlama dili olmaz.
- "Why" gerekiyorsa body'de 1-2 cümle ile açıklanır; "what" başlıkta yeterlidir.

### 4. Commit Komutu
Her commit aşağıdaki şablon ile atılır (HEREDOC kullanılmaz, imza eklenmez):

```bash
git commit -m "<tür>: <kısa açıklama>"
```

Detay gerekiyorsa:
```bash
git commit -m "<tür>: <kısa açıklama>" -m "<gerekçe veya bağlam — 1-2 cümle>"
```

### 5. Yapılmayacaklar
- `git commit --amend` ile yayımlanmış commit değiştirilmez.
- `--no-verify` ile hook atlanmaz.
- Tek commit'te `.env`, credential veya büyük binary dosya bulunmaz.
- `git add .` veya `git add -A` yerine dosyalar isimle eklenir.
