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
# Runbook

## 1. Amaç

Bu doküman, proje geliştirme ve Kubernetes ortamına taşıma sürecinde karşılaşılan gerçek sorunları, belirtilerini, nedenlerini ve uygulanan çözümleri içermektedir.

Amaç, aynı sorunlarla tekrar karşılaşıldığında çözüm sürecini hızlandırmak ve yapılan hatalardan öğrenilen bilgileri kayıt altında tutmaktır.

---

# Kubernetes Sorunları

## Problem 1: PostgreSQL Pod'unun `ContainerCreating` Durumunda Kalması

### Belirti

PostgreSQL Deployment oluşturulduktan sonra Pod uzun süre çalışmaya başlamadı.

```text
NAME                                READY   STATUS              RESTARTS
postgres-5c467bb54b-f9q5c           0/1     ContainerCreating   0
```

Pod detayları kontrol edildiğinde aşağıdaki event görüldü:

```text
Normal  Pulling  kubelet  Pulling image "postgres:16-alpine"
```

### Sebep

Kubernetes cluster'ı `kind` kullanılarak oluşturulmuştu.

`kind`, Kubernetes node'larını Docker container'ları içerisinde çalıştırdığı için local Docker ortamındaki image doğrudan Kubernetes node'u içerisinde bulunmuyordu.

Bu nedenle PostgreSQL image'ının kind node'una yüklenmesi gerekiyordu.

### Çözüm

Önce PostgreSQL image'ı local Docker ortamında kontrol edildi:

```bash
docker images
```

Daha sonra image kind node'una yüklendi:

```bash
kind load docker-image postgres:16-alpine
```

Image'ın kind node'u içerisinde bulunduğu aşağıdaki komutla doğrulandı:

```bash
docker exec kind-control-plane crictl images | grep postgres
```

Son olarak eski Pod kaldırılarak Deployment yeniden oluşturuldu.

### Öğrenilen

Local Docker ortamında bulunan bir image, kind Kubernetes cluster'ı tarafından otomatik olarak kullanılamaz.

Gerekli durumlarda image şu komutla kind node'una aktarılmalıdır:

```bash
kind load docker-image <image-name>
```

---

## Problem 2: `ErrImageNeverPull` Hatası

### Belirti

PostgreSQL Pod'u aşağıdaki hatayı verdi:

```text
ErrImageNeverPull
```

### Sebep

Deployment içerisinde:

```yaml
imagePullPolicy: Never
```

kullanılmıştı.

Bu ayar Kubernetes'e image'ı internetten veya container registry'den indirmemesini ve yalnızca node üzerinde bulunan image'ı kullanmasını söyler.

Ancak image Kubernetes node'u tarafından kullanılabilir durumda değildi.

### Çözüm

Image'ın kind node'u içerisinde bulunduğu doğrulandı:

```bash
docker exec kind-control-plane crictl images | grep postgres
```

Daha sonra PostgreSQL Deployment YAML dosyası yeniden düzenlendi ve uygulanmadan önce doğrulandı:

```bash
kubectl apply --dry-run=client -f postgres-deployment.yaml
```

Ardından Deployment uygulandı:

```bash
kubectl apply -f postgres-deployment.yaml
```

Sonuç olarak PostgreSQL Pod'u başarıyla çalıştı:

```text
postgres-xxxxxxxxxx-xxxxx   1/1   Running
```

### Öğrenilen

`imagePullPolicy: Never` kullanılıyorsa image mutlaka Kubernetes node'u içerisinde bulunmalıdır.

---

## Problem 3: YAML Syntax Hatası

### Belirti

Deployment uygulanırken aşağıdaki hata alındı:

```text
error parsing postgres-deployment.yaml:
error converting YAML to JSON:
yaml: line 25: could not find expected ':'
```

Daha sonra API Deployment dosyasında da benzer bir hata oluştu:

```text
yaml: line 20: did not find expected key
```

### Sebep

YAML dosyalarında indentation yani girintileme çok önemlidir.

Bazı satırlarda:

* Girintiler yanlış yazılmıştı.
* `:` karakteri eksikti veya yanlış konumdaydı.
* YAML yapısındaki parent-child ilişkisi bozulmuştu.

### Çözüm

YAML dosyaları yeniden düzenlendi.

Uygulamadan önce syntax kontrolü yapmak için:

```bash
kubectl apply --dry-run=client -f deployment.yaml
```

komutu kullanıldı.

Hata alınmadığında gerçek uygulama gerçekleştirildi:

```bash
kubectl apply -f deployment.yaml
```

### Öğrenilen

Kubernetes YAML dosyaları uygulanmadan önce mümkünse aşağıdaki komutla kontrol edilmelidir:

```bash
kubectl apply --dry-run=client -f <dosya>.yaml
```

Bu yöntem YAML veya Kubernetes kaynak tanımındaki hataları gerçek değişiklik yapmadan tespit etmeyi sağlar.

---

## Problem 4: FastAPI Pod'unun `CrashLoopBackOff` Durumuna Girmesi

### Belirti

API Pod'u sürekli yeniden başlatılıyordu:

```text
task-manager-api-xxxxxxxxxx-xxxxx   0/1   CrashLoopBackOff
```

Restart sayısı zamanla arttı.

Örneğin:

```text
RESTARTS
20
```

### Sebep

API uygulaması PostgreSQL bağlantısına ihtiyaç duyuyordu ancak PostgreSQL Kubernetes ortamında henüz düzgün şekilde çalışmıyordu.

Başlangıçta `DATABASE_URL` bağlantı bilgisi doğrudan `app.py` içerisinde bulunuyordu.

PostgreSQL Pod ve Service yapısı tamamlanmadan API uygulaması veritabanına bağlanmaya çalıştığı için container hata vererek kapanıyordu.

Kubernetes ise Pod'un çalışması gerektiğini bildiği için container'ı tekrar başlatıyordu.

Bu durum sürekli tekrarlandığı için `CrashLoopBackOff` oluştu.

### Çözüm

Önce PostgreSQL Deployment ve Service düzgün şekilde oluşturuldu.

PostgreSQL Pod'unun çalıştığı doğrulandı:

```bash
kubectl get pods
```

PostgreSQL Service kontrol edildi:

```bash
kubectl get svc
```

Daha sonra API Deployment yeniden oluşturuldu.

Sonuç olarak hem PostgreSQL hem de API Pod'ları çalışır duruma geldi:

```text
postgres-xxxxxxxxxx-xxxxx           1/1   Running
task-manager-api-xxxxxxxxxx-xxxxx   1/1   Running
```

### Öğrenilen

Bir uygulama başka bir servise bağımlıysa bağımlı olduğu servis çalışmadan uygulama başlatılırsa hata oluşabilir.

`CrashLoopBackOff` durumunda şu komutlar kullanılmalıdır:

```bash
kubectl logs <pod-name>
```

ve:

```bash
kubectl describe pod <pod-name>
```

Bu komutlar hatanın container içerisinde mi yoksa Kubernetes tarafında mı olduğunu anlamaya yardımcı olur.

---

## Problem 5: Service YAML Dosyasının Bulunamaması

### Belirti

Aşağıdaki komut çalıştırıldığında hata alındı:

```bash
kubectl apply --dry-run=client -f task-manager-service.yaml
```

Hata:

```text
error: the path "task-manager-service.yaml" does not exist
```

### Sebep

Komut çalıştırılan dizinde `task-manager-service.yaml` dosyası bulunmuyordu.

Dosya başka bir dizinde oluşturulmuştu veya dosya adı farklıydı.

### Çözüm

Dosyanın bulunduğu klasör kontrol edildi ve doğru dosya yolu kullanıldı.

Örneğin:

```bash
kubectl apply --dry-run=client -f ~/Masaüstü/claude/k8s/task-manager-service.yaml
```

veya önce doğru dizine geçildi:

```bash
cd ~/Masaüstü/claude/k8s
```

Ardından komut tekrar çalıştırıldı.

### Öğrenilen

Linux terminalinde bir dosya ile çalışırken mevcut dizin ve dosya adı kontrol edilmelidir.

Kontrol için:

```bash
pwd
```

ve:

```bash
ls
```

komutları kullanılabilir.

---

## Problem 6: Local Docker Image'ın Kubernetes Tarafından Bulunamaması

### Belirti

API için local olarak oluşturulan Docker image'ı Kubernetes tarafından otomatik olarak bulunamadı.

### Sebep

Docker image'ı local Docker ortamında oluşturulmuştu:

```bash
docker build -t task-manager-api:latest .
```

Ancak Kubernetes `kind` node'u kendi container ortamında çalışıyordu.

Bu nedenle image'ın kind node'una ayrıca aktarılması gerekiyordu.

### Çözüm

Image kind node'una yüklendi:

```bash
kind load docker-image task-manager-api:latest
```

Daha sonra yeni sürüm için:

```bash
docker build -t task-manager-api:v2 .
kind load docker-image task-manager-api:v2
```

komutları kullanıldı.

### Öğrenilen

`kind` ortamında local olarak oluşturulan image'ların Kubernetes tarafından kullanılabilmesi için gerektiğinde `kind load docker-image` komutu kullanılmalıdır.

---

## Problem 7: API'nin PostgreSQL Bağlantı Bilgisinin Kod İçerisinde Bulunması

### Belirti

`app.py` dosyası kontrol edildiğinde veritabanı bağlantı bilgisinin doğrudan kod içerisinde bulunduğu görüldü:

```python
DATABASE_URL = "postgresql://myuser:mysecurepassword@postgres:5432/mydatabase"
```

### Sebep

Bağlantı bilgisinin hızlı bir şekilde çalıştırılması için değer doğrudan uygulama koduna yazılmıştı.

Ancak bu yöntem:

* Şifrenin kaynak kod içerisinde görünmesine
* Konfigürasyon değişikliklerinde kodun değiştirilmesine
* Kodun GitHub'a yüklenmesi durumunda hassas bilgilerin açığa çıkmasına

neden olabilir.

### Çözüm

`DATABASE_URL` environment variable üzerinden okunacak şekilde değiştirildi:

```python
import os

DATABASE_URL = os.getenv("DATABASE_URL")
```

Hassas bağlantı bilgisi Kubernetes Secret içerisine taşındı.

Secret kontrol edildi:

```bash
kubectl get secret postgres-secret
```

PostgreSQL ile ilgili hassas olmayan bilgiler ise ConfigMap içerisinde tutuldu:

```bash
kubectl get configmap
```

### Öğrenilen

Uygulama konfigürasyonları mümkün olduğunca kaynak koddan ayrılmalıdır.

Genel olarak:

```text
ConfigMap → Hassas olmayan bilgiler
Secret    → Hassas bilgiler
```

şeklinde bir ayrım yapılmalıdır.

---

## Problem 8: Secret'ın Gerçek Şifreleme Olduğunun Sanılması

### Belirti

Kubernetes Secret kullanıldığında bilgilerin tamamen şifrelendiği düşünülebilir.

### Sebep

Secret içerisindeki değerler genellikle Base64 formatında görüntülenir.

Ancak Base64:

```text
encoding işlemidir.
```

Şifreleme değildir.

### Çözüm

Secret'ın hassas bilgileri ConfigMap'ten ayırmak ve Kubernetes içerisinde yönetmek için kullanıldığı öğrenildi.

Daha güçlü güvenlik için production ortamlarında ek olarak:

* RBAC
* Encryption at rest
* Harici secret management sistemleri

kullanılabilir.

### Öğrenilen

```text
Base64 encoding ≠ Encryption
```

Secret kullanımı güvenlik açısından yararlıdır ancak tek başına verinin tamamen şifrelendiği anlamına gelmez.

---

## Problem 9: Yeni API Image Sürümünün Kubernetes'e Aktarılması

### Belirti

API'nin yeni `v2` sürümü oluşturuldu ancak Kubernetes'in yeni image'ı kullanabilmesi gerekiyordu.

### Sebep

Yeni image sadece local Docker ortamında bulunuyordu.

Kubernetes kind cluster'ı bu image'a doğrudan erişemiyordu.

### Çözüm

Yeni image oluşturuldu:

```bash
docker build -t task-manager-api:v2 .
```

Daha sonra kind node'una aktarıldı:

```bash
kind load docker-image task-manager-api:v2
```

Deployment image'ı güncellendi.

Sonuç kontrol edildi:

```bash
kubectl get deployment task-manager-api -o wide
```

Çıktıda:

```text
task-manager-api:v2
```

image'ının kullanıldığı görüldü.

### Öğrenilen

Yeni bir image sürümü oluşturulduğunda Kubernetes'in bu image'a erişebildiğinden emin olunmalıdır.

Local kind ortamında bu işlem:

```bash
kind load docker-image <image-name>
```

ile gerçekleştirilebilir.

---

## Problem 10: Rolling Update Sürecinin Canlı İzlenmemesi

### Belirti

API `v2` sürümüne başarıyla güncellendi ancak güncelleme sırasında eski ve yeni Pod'ların değişim süreci canlı olarak izlenmedi.

### Sebep

Güncelleme sırasında:

```bash
kubectl get pods -w
```

komutu kullanılmadı.

Bu nedenle yeni Pod oluşturulup eski Pod'un kaldırıldığı süreç anlık olarak gözlemlenmedi.

### Çözüm

Güncellemenin tamamlandığı aşağıdaki komutla kontrol edildi:

```bash
kubectl rollout status deployment/task-manager-api
```

Ayrıca:

```bash
kubectl get deployment task-manager-api -o wide
```

komutu ile yeni image sürümünün kullanıldığı doğrulandı.

### Öğrenilen

Rolling Update sürecini canlı takip etmek için:

```bash
kubectl get pods -w
```

kullanılabilir.

Deployment güncellemesinin tamamlanıp tamamlanmadığını kontrol etmek için:

```bash
kubectl rollout status deployment/<deployment-name>
```

kullanılabilir.

Birden fazla replica kullanıldığında Rolling Update sırasında uygulamanın kullanılabilirliği daha iyi korunabilir.

---

# Kubernetes Sorunlarında Genel Kontrol Komutları

Bir Pod çalışmıyorsa ilk olarak:

```bash
kubectl get pods
```

komutu çalıştırılmalıdır.

Pod detaylarını ve event'leri görmek için:

```bash
kubectl describe pod <pod-name>
```

Container loglarını görmek için:

```bash
kubectl logs <pod-name>
```

Service'leri kontrol etmek için:

```bash
kubectl get svc
```

Deployment durumunu kontrol etmek için:

```bash
kubectl get deployment
```

ConfigMap'leri kontrol etmek için:

```bash
kubectl get configmap
```

Secret'ları kontrol etmek için:

```bash
kubectl get secret
```

YAML dosyasını uygulamadan önce kontrol etmek için:

```bash
kubectl apply --dry-run=client -f <dosya>.yaml
```

kullanılabilir.

---

# Genel Öğrenilenler

Bu süreçte Kubernetes üzerinde bir uygulama çalıştırırken aşağıdaki noktalar öğrenildi:

1. Pod'lar Kubernetes'in temel çalışma birimleridir.
2. Deployment, Pod'ların istenen durumda çalışmasını yönetir.
3. Service, Pod'lara sabit bir erişim noktası sağlar.
4. Pod IP adresleri yerine Service isimleri kullanılmalıdır.
5. `kind` ortamında local Docker image'larının Kubernetes node'una yüklenmesi gerekebilir.
6. `imagePullPolicy: Never` kullanılıyorsa image node üzerinde bulunmalıdır.
7. YAML dosyalarında indentation ve syntax çok önemlidir.
8. YAML dosyaları `--dry-run=client` ile uygulanmadan önce kontrol edilebilir.
9. `CrashLoopBackOff` durumunda Pod logları ve event'ler incelenmelidir.
10. Hassas olmayan yapılandırmalar ConfigMap'te, hassas bilgiler Secret'ta tutulmalıdır.
11. Kubernetes Secret değerlerinin Base64 olması gerçek şifreleme anlamına gelmez.
12. Yeni image sürümleri Deployment üzerinden güncellenebilir.
13. Rolling Update işlemi Kubernetes'in uygulama güncelleme mekanizmalarından biridir.
14. `kubectl get pods`, `kubectl describe pod` ve `kubectl logs` hata ayıklamada en önemli komutlardandır.








