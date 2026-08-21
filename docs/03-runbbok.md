# Runbook - Karşılaşılan Sorunlar ve Çözümleri

Bu dokümanda proje geliştirme, Docker, AWS ve EC2 deployment süreçlerinde karşılaşılan gerçek sorunlar ve uygulanan çözümler yer almaktadır.

---

## 1. Problem: SSH Private Key Yanlış Ortamda Bulunuyordu

### Belirti

SSH bağlantısı kurulmaya çalışıldığında:

```text
Permission denied
```

hatası alındı.

### Sebep

SSH bağlantısında kullanılacak private key dosyası bağlantının yapılacağı ortamda bulunmuyordu.

Private key Windows ortamında oluşturulmuş veya indirilmişti, ancak bağlantı Ubuntu VirtualBox VM içerisinden yapılmaya çalışılıyordu.

Bu nedenle Ubuntu ortamı private key dosyasına erişemiyordu.

### Çözüm

Private key dosyası Windows ortamından Ubuntu VM içerisine aktarıldı ve SSH klasörüne yerleştirildi.

Dosyanın izinleri güvenlik amacıyla düzenlendi:

```bash
chmod 600 ~/.ssh/task-manager-key.pem
```

Daha sonra SSH bağlantısı doğru key dosyası kullanılarak gerçekleştirildi:

```bash
ssh -i ~/.ssh/task-manager-key.pem ubuntu@EC2_PUBLIC_IP
```

### Öğrenilen Ders

- SSH bağlantısında private key, bağlantıyı gerçekleştiren makinede bulunmalıdır.
- Private key dosyalarının izinleri güvenlik amacıyla kısıtlanmalıdır.
- AWS `.pem` dosyaları için genellikle `chmod 600` kullanılabilir.

---

## 2. Problem: FastAPI Uygulamasına Yanlış URL ile Erişme

### Belirti

FastAPI uygulaması çalışmasına rağmen beklenen sayfa doğrudan tarayıcıda görünmedi.

### Sebep

FastAPI'nin otomatik API dokümantasyonu için `/docs` endpoint'i kullanılmadan uygulamaya erişilmeye çalışıldı.

### Çözüm

Tarayıcıda aşağıdaki adres kullanıldı:

```text
http://127.0.0.1:8000/docs
```

Bu adres üzerinden FastAPI'nin Swagger UI arayüzüne erişildi.

### Öğrenilen Ders

FastAPI uygulamasında:

```text
/
```

uygulamanın root endpoint'idir.

```text
/docs
```

ise FastAPI tarafından otomatik oluşturulan Swagger UI dokümantasyon sayfasıdır.

---

## 3. Problem: PostgreSQL İçin 5432 Port Çakışması

### Belirti

Docker Compose çalıştırılırken aşağıdaki hata alındı:

```text
failed to bind host port 0.0.0.0:5432/tcp:
address already in use
```

### Sebep

Ubuntu üzerinde başka bir uygulama veya container zaten `5432` portunu kullanıyordu.

Bu nedenle PostgreSQL container'ının aynı host portuna bağlanması mümkün olmadı.

### Çözüm

PostgreSQL'e host Ubuntu üzerinden doğrudan erişilmesine ihtiyaç olmadığı için `docker-compose.yml` dosyasındaki PostgreSQL servisine ait `ports` bölümü kaldırıldı.

PostgreSQL yalnızca Docker ağı içerisinde erişilebilir bırakıldı.

FastAPI uygulaması PostgreSQL'e host üzerindeki `localhost` yerine Docker Compose servis adı üzerinden bağlandı.

Örnek yapı:

```text
FastAPI Container
        ↓
Docker Network
        ↓
postgres_db
        ↓
PostgreSQL
```

### Öğrenilen Ders

Container'lar aynı Docker Compose ağı içerisindeyse birbirleriyle servis adı üzerinden haberleşebilir.

Bu nedenle her container'ın portunu host makineye açmak gerekli değildir.

Veritabanı portunu internete veya host'a açmamak güvenlik açısından da daha iyi bir yaklaşımdır.

---

## 4. Problem: `.pem` Dosyasının Windows'tan Ubuntu VM'e Taşınması

### Problem

AWS EC2 oluşturulurken kullanılan `.pem` private key dosyası Windows ortamına indirildi.

SSH bağlantısını Ubuntu VirtualBox VM içerisinden gerçekleştirmek gerektiği için private key'in Ubuntu ortamına aktarılması gerekiyordu.

### Çözüm

VirtualBox paylaşımlı klasörü kullanılarak Windows'taki dosyaya Ubuntu VM içerisinden erişildi.

Paylaşımlı klasör `/media/` altında görünüyordu.

İlk kontrolde:

```bash
ls /media/
```

çıktısında aşağıdaki isim görüldü:

```text
sf_task-manager-key.pem
```

Ancak bu isim doğrudan private key dosyası değil, VirtualBox tarafından oluşturulan paylaşımlı klasörü ifade ediyordu.

Klasör içerisinde gerçek dosya:

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

Kontrol edildi:

```bash
ls -la ~/.ssh/task-manager-key.pem
```

Beklenen izin:

```text
-rw-------
```

### Öğrenilen Ders

- `.pem` dosyası AWS EC2 için kullanılan private key'dir.
- Private key'in izinleri mümkün olduğunca kısıtlı tutulmalıdır.
- VirtualBox shared folder içerisindeki yapılar normal Linux dosyalarından farklı görünebilir.
- `/media/sf_...` altında görünen isim bir shared folder olabilir.
- SSH bağlantısında private key'in gerçek dosya yolu kullanılmalıdır.

Örnek bağlantı:

```bash
ssh -i ~/.ssh/task-manager-key.pem ubuntu@EC2_PUBLIC_IP
```

---

## 5. Problem: `docker compose` Komutunun Bulunamaması

### Belirti

EC2 üzerinde Docker kurulduktan sonra:

```bash
docker compose version
```

komutu çalıştırıldığında:

```text
docker: unknown command: docker compose
```

hatası alındı.

Ayrıca eski Compose komutu da bulunamadı:

```bash
docker-compose
```

Ardından:

```bash
sudo apt install docker-compose-plugin -y
```

komutu denendi ancak:

```text
E: Unable to locate package docker-compose-plugin
```

hatası alındı.

### Sebep

EC2 üzerinde kurulan `docker.io` paketi Docker Compose v2 plugin'ini içermiyordu.

Ayrıca mevcut Ubuntu paket kaynaklarında `docker-compose-plugin` paketi bulunmuyordu.

### Çözüm

Docker'ın resmi paket deposu eklendi ve Docker Compose plugin'i kuruldu.

Kurulum sonrasında:

```bash
docker compose version
```

komutu başarıyla çalıştı.

Örnek çıktı:

```text
Docker Compose version v5.5.0
```

### Öğrenilen Ders

Docker'ın Ubuntu paket deposundan gelen sürümü ile Docker'ın resmi repository'sinden gelen paketler farklı olabilir.

Bir paketin bulunamaması, paketin mevcut olmadığı anlamına gelmez. Kullanılan paket repository'leri de kontrol edilmelidir.

---

## 6. Problem: Private GitHub Repository'yi Clone Ederken Kimlik Doğrulama Hatası

### Belirti

EC2 üzerinde private GitHub repository klonlanmak istendi:

```bash
git clone https://github.com/yagmurraydar/summer_practiceII_staj_project.git
```

İlk denemede normal GitHub şifresi kullanıldığında:

```text
remote: Invalid username or token.
Password authentication is not supported for Git operations.
```

hatası alındı.

Daha sonraki bir denemede ise:

```text
remote: Write access to repository not granted.
fatal: unable to access repository: The requested URL returned error: 403
```

hatası alındı.

### Sebep

Repository private olduğu için kimlik doğrulaması gerekiyordu.

GitHub, HTTPS üzerinden Git işlemlerinde hesap şifresi kullanımını desteklemez.

Ayrıca kullanılan Personal Access Token'ın repository için gerekli erişim izinlerine sahip olması gerekiyordu.

### Çözüm

Repository erişim yetkisine sahip doğru GitHub Personal Access Token kullanıldı.

Aynı `git clone` komutu tekrar çalıştırıldı:

```bash
git clone https://github.com/yagmurraydar/summer_practiceII_staj_project.git
```

GitHub kullanıcı adı girildi.

Password istendiğinde GitHub hesap şifresi yerine Personal Access Token kullanıldı.

Repository başarıyla EC2 instance'a klonlandı.

### Öğrenilen Ders

- Public repository'ler HTTPS üzerinden genellikle doğrudan klonlanabilir.
- Private repository'lerde kimlik doğrulaması gerekir.
- GitHub şifresi yerine Personal Access Token kullanılabilir.
- Token'ın gerekli repository izinlerine sahip olması gerekir.
- Bu konu CI/CD ve otomatik deployment süreçlerinde de önemlidir.

---

## 7. Problem: Port 8000 Açık Görünmesine Rağmen EC2'ye Dışarıdan Erişilememesi

### Belirti

Docker container'ı çalışıyordu:

```text
0.0.0.0:8000->8000/tcp
```

Ancak kendi Windows bilgisayarımdan:

```bash
curl http://EC2_PUBLIC_IP:8000/tasks
```

isteği gönderildiğinde:

```text
curl: (28) Failed to connect to EC2_PUBLIC_IP:8000
```

hatası alındı.

### Sebep

Docker port mapping doğru olmasına rağmen AWS Security Group üzerinde port `8000` için gelen trafik doğru şekilde izinli değildi.

İlk olarak port `8000` için yalnızca belirli bir IP adresine izin verilmişti:

```text
31.155.229.147/32
```

Bu IP mevcut bağlantının public IP adresiyle eşleşmediği veya IP adresi değiştiği için bağlantı başarısız oldu.

### Çözüm

Test amacıyla Security Group inbound rule şu şekilde değiştirildi:

```text
Type: Custom TCP
Protocol: TCP
Port: 8000
Source: 0.0.0.0/0
```

Daha sonra Windows bilgisayarından tekrar test yapıldı:

```bash
curl http://EC2_PUBLIC_IP:8000/tasks
```

Bu kez başarılı cevap alındı:

```json
[]
```

Daha sonra API üzerinden bir task oluşturuldu ve tekrar GET isteği ile başarıyla görüntülendi.

### Öğrenilen Ders

Bir uygulamanın Docker container içerisinde çalışması, uygulamanın otomatik olarak internet üzerinden erişilebilir olduğu anlamına gelmez.

Dış erişimin çalışabilmesi için tüm zincirin doğru yapılandırılması gerekir:

```text
Application
    ↓
Container Port
    ↓
Docker Port Mapping
    ↓
EC2 Instance
    ↓
Security Group
    ↓
Route Table
    ↓
Internet Gateway
    ↓
Internet
```

Bağlantı problemi yaşandığında yalnızca Docker veya uygulama değil, tüm network zinciri kontrol edilmelidir.

---

## 8. Problem: CMD ve PowerShell `curl` Sözdizimi Farkı

### Belirti

Windows CMD üzerinde API'ye POST isteği gönderilirken PowerShell sözdizimi kullanıldı:

```powershell
curl -Method POST http://EC2_PUBLIC_IP:8000/tasks -ContentType "application/json" -Body '{"title":"AWS EC2 Test","description":"EC2 üzerinden oluşturuldu"}'
```

Komut beklenen şekilde çalışmadı ve:

```text
Warning: built-in manual was disabled at build-time
```

uyarısı görüldü.

### Sebep

CMD ortamında kullanılan `curl`, PowerShell'e ait parametreleri desteklemez.

Aşağıdaki parametreler PowerShell sözdizimine aittir:

```text
-Method
-ContentType
-Body
```

### Çözüm

Windows CMD üzerinde standart `curl` sözdizimi kullanıldı:

```bash
curl -X POST "http://EC2_PUBLIC_IP:8000/tasks" -H "Content-Type: application/json" -d "{\"title\":\"AWS EC2 Test\",\"description\":\"EC2 üzerinden oluşturuldu\"}"
```

Daha sonra oluşturulan task kontrol edildi:

```bash
curl http://EC2_PUBLIC_IP:8000/tasks
```

Başarılı cevap:

```json
[
  {
    "title": "AWS EC2 Test",
    "description": "EC2 üzerinden oluşturuldu",
    "completed": false,
    "id": 1
  }
]
```

### Öğrenilen Ders

Aynı komut farklı terminal ortamlarında farklı şekilde çalışabilir.

Komut kullanmadan önce hangi shell ortamında çalışıldığı kontrol edilmelidir:

- CMD
- PowerShell
- Bash
- Zsh

Bir ortam için geçerli olan parametreler başka bir terminalde çalışmayabilir.

---

## 9. Problem: EC2 Public IP ile Private IP'nin Karıştırılması

### Belirti

EC2 terminalinde görünen:

```text
ubuntu@ip-172-31-18-163
```

adresindeki IP'nin dış erişim için kullanılabileceği düşünülebilir.

### Sebep

`172.31.x.x` adresi EC2 instance'ın VPC içerisindeki private IP adresidir.

Bu IP adresi internet üzerinden doğrudan erişilemez.

### Çözüm

AWS Console üzerinden instance'ın güncel Public IPv4 adresi kontrol edildi.

Dış erişim testleri Public IPv4 kullanılarak yapıldı:

```bash
curl http://EC2_PUBLIC_IP:8000/tasks
```

### Öğrenilen Ders

AWS üzerinde:

- Private IP, VPC içerisindeki iletişim için kullanılır.
- Public IPv4, internet üzerinden erişim için kullanılır.

EC2 instance stop/start işleminden sonra Elastic IP kullanılmıyorsa Public IPv4 adresi değişebilir.

Bu nedenle bağlantı sorunu yaşandığında kullanılan IP adresinin güncel ve doğru olduğu kontrol edilmelidir.