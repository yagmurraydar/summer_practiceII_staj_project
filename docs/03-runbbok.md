## Problem: SSH Private Key VM içinde oluşturuldu
**Belirti:** Permission denied hatası
**Sebep:** private keyin yanlış makinede oluşturulması

## Problem: app.py çalıştırıken hata aldım 
**Belirti:** Sayfa açılmadı
**Sebep:** /docs uzantısı eklemeden tarayıcıda çalıştırdığım için

## Problem : 5432 portunu ubuntuda başka bir container zaten kullanıyordu
**Belirti:** failed to bind host port 0.0.0.0:5432/tcp:
address already in use
**Çözüm:** PostgreSQL'e host Ubuntu'dan doğrudan bağlanmadan Compose'daki PostgreSQL için ports kısmını tamamen kaldırdık

