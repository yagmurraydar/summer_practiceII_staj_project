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

## 4. Gerçek Sorun: `.pem` Dosyasının Windows'tan Ubuntu VM'e Taşınması

### Problem

AWS EC2 oluşturulurken kullanılan `.pem` private key dosyası yanlışlıkla Windows ortamına indirildi.

SSH bağlantısını Ubuntu VirtualBox VM içerisinden gerçekleştirmek gerektiği için private key'in Ubuntu ortamına aktarılması gerekti.

### Çözüm

VirtualBox paylaşımlı klasörü kullanılarak Windows'taki dosyaya Ubuntu VM içerisinden erişildi.

Paylaşımlı klasör `/media/` altında görünüyordu.

İlk kontrolde:

```bash
ls /media/
```

çıktısında `sf_task-manager-key.pem` adı görüldü.

Ancak bu isim doğrudan private key dosyasını değil, VirtualBox tarafından oluşturulan paylaşımlı klasörü ifade ediyordu.

Klasörün içerisinde gerçek dosya:

```text
task-manager-key.pem
```

olarak bulunuyordu.

Dosya Ubuntu'nun SSH klasörüne kopyalandı:

```bash
sudo cp /media/sf_task-manager-key.pem/task-manager-key.pem ~/.ssh/
```

Dosyanın sahibi mevcut kullanıcı olarak ayarlandı:

```bash
sudo chown $USER:$USER ~/.ssh/task-manager-key.pem
```

Private key için güvenli dosya izinleri verildi:

```bash
chmod 600 ~/.ssh/task-manager-key.pem
```

Kontrol:

```bash
ls -la ~/.ssh/task-manager-key.pem
```

Beklenen izin:

```text
-rw-------
```

### Öğrenilenler

* `.pem` dosyası AWS EC2 için kullanılan private key'dir.
* Private key'in izinleri mümkün olduğunca kısıtlı tutulmalıdır.
* VirtualBox shared folder içerisindeki dosyalar doğrudan normal Linux dosyaları gibi görünmeyebilir.
* `/media/sf_...` altında görünen isim bir shared folder olabilir.
* SSH bağlantısında private key'in gerçek dosya yolu kullanılmalıdır.

Örnek SSH bağlantısı:

```bash
ssh -i ~/.ssh/task-manager-key.pem ubuntu@<EC2_PUBLIC_IP>
```
