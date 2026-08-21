# AWS EC2 Üzerinde Docker Deployment

## 1. Amaç

Bu aşamada daha önce Docker ile containerlaştırılmış FastAPI Task Manager uygulaması AWS EC2 üzerinde çalıştırıldı.

Amaç, yerel ortamda Docker Compose ile çalışan uygulamayı AWS EC2 sunucusuna taşıyarak internet üzerinden erişilebilir hale getirmekti.

Bu deployment sürecinde daha önce öğrenilen Docker ve AWS networking konuları birlikte kullanıldı.

Kullanılan temel teknolojiler ve servisler:

- AWS EC2
- VPC
- Public Subnet
- Internet Gateway
- Route Table
- Security Group
- SSH
- Docker
- Docker Compose
- FastAPI
- PostgreSQL
- GitHub

---

## 2. EC2 Instance'ın Başlatılması

Daha önce oluşturulan EC2 instance durdurulmuştu.

AWS Console üzerinden aşağıdaki adımlar uygulanarak instance tekrar başlatıldı:

```text
EC2 → Instances → Instance state → Start instance
```

Instance yeniden başlatıldığında Public IPv4 adresinin değişebileceği dikkate alındı.

Bu nedenle SSH bağlantısı ve dış erişim testlerinde instance'ın güncel Public IPv4 adresi kullanıldı.

---

## 3. EC2'ye SSH ile Bağlanma

Windows bilgisayarından EC2 instance'a SSH ile bağlanıldı.

Genel bağlantı formatı:

```bash
ssh -i "key.pem" ubuntu@EC2_PUBLIC_IP
```

Bağlantı başarılı olduğunda EC2 üzerinde Ubuntu terminaline erişildi.

Örnek terminal görünümü:

```text
ubuntu@ip-172-31-18-163:~$
```

Buradaki `172.31.x.x` adresi instance'ın VPC içerisindeki private IP adresidir.

İnternet üzerinden erişim ve SSH bağlantısı için AWS Console üzerinde bulunan Public IPv4 adresi kullanıldı.

---

## 4. EC2 Üzerinde Docker Kurulumu

Önce paket listesi güncellendi:

```bash
sudo apt update
sudo apt upgrade -y
```

Ardından Docker kuruldu:

```bash
sudo apt install docker.io -y
```

Docker servisinin sistem başladığında otomatik olarak çalışması sağlandı:

```bash
sudo systemctl enable --now docker
```

Docker kurulumu kontrol edildi:

```bash
docker --version
```

---

## 5. Kullanıcının Docker Grubuna Eklenmesi

Docker komutlarını sürekli `sudo` kullanmadan çalıştırabilmek için mevcut kullanıcı Docker grubuna eklendi:

```bash
sudo usermod -aG docker $USER
```

Bu değişikliğin aktif olması için SSH oturumundan çıkılıp tekrar bağlanıldı.

Daha sonra aşağıdaki komut `sudo` kullanmadan çalıştırılarak yapılandırma doğrulandı:

```bash
docker ps
```

---

## 6. Docker Compose Kurulumu

Başlangıçta Docker Compose kontrol edildi:

```bash
docker compose version
```

Ancak aşağıdaki hata alındı:

```text
docker: unknown command: docker compose
```

Ardından Docker Compose plugin'i Ubuntu'nun mevcut paket kaynaklarından kurulmaya çalışıldı:

```bash
sudo apt install docker-compose-plugin -y
```

Ancak paket bulunamadı:

```text
E: Unable to locate package docker-compose-plugin
```

Çözüm olarak Docker'ın resmi paket deposu eklendi.

Önce gerekli paketler kuruldu:

```bash
sudo apt update
sudo apt install ca-certificates curl -y
```

Docker GPG anahtarı eklendi:

```bash
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
```

Docker'ın resmi repository'si eklendi:

```bash
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

Paket listesi tekrar güncellendi:

```bash
sudo apt update
```

Docker Compose plugin'i kuruldu:

```bash
sudo apt install docker-compose-plugin -y
```

Kurulum kontrol edildi:

```bash
docker compose version
```

Docker Compose başarıyla çalıştı.

---

## 7. Private GitHub Repository'nin EC2'ye Çekilmesi

Proje GitHub üzerinde private repository olarak bulunuyordu.

EC2 üzerinde home dizinine geçildi:

```bash
cd ~
```

Repository şu komutla klonlanmaya çalışıldı:

```bash
git clone https://github.com/yagmurraydar/summer_practiceII_staj_project.git
```

Repository private olduğu için GitHub kullanıcı adı ve kimlik doğrulaması istendi.

İlk denemede kullanılan kimlik bilgileri gerekli repository erişimine sahip olmadığı için aşağıdaki hata alındı:

```text
remote: Write access to repository not granted.

fatal: unable to access repository: The requested URL returned error: 403
```

Daha sonra uygun erişime sahip GitHub Personal Access Token kullanılarak işlem tekrarlandı.

Repository başarıyla EC2 instance'a klonlandı.

---

## 8. Docker Compose ile Uygulamanın Çalıştırılması

Proje klasörüne girildi:

```bash
cd ~/summer_practiceII_staj_project
```

Uygulama build edilerek arka planda çalıştırıldı:

```bash
docker compose up --build -d
```

Container durumları kontrol edildi:

```bash
docker ps
```

Çıktıda iki container'ın çalıştığı görüldü:

- `task_manager_api`
- `postgres_db`

FastAPI uygulamasının port mapping'i şu şekildeydi:

```text
0.0.0.0:8000->8000/tcp
```

Bu yapı şu anlama gelir:

```text
EC2 Host :8000
        ↓
Docker Port Mapping
        ↓
FastAPI Container :8000
```

PostgreSQL container'ı Docker ağı içerisinde çalışmaktadır.

PostgreSQL için host üzerinde public bir port mapping yapılmadı. Bu nedenle veritabanı doğrudan internet üzerinden erişilebilir değildir.

---

## 9. Security Group ve Port 8000

Başlangıçta Security Group üzerinde aşağıdaki portlar açıktı:

```text
22   SSH
80   HTTP
443  HTTPS
```

FastAPI uygulaması ise `8000` portunda çalışıyordu.

Bu nedenle Docker container çalışmasına rağmen uygulamaya dışarıdan erişebilmek için Security Group üzerinde `8000` portuna izin verilmesi gerekiyordu.

Security Group'a port `8000` için yeni bir inbound rule eklendi.

İlk olarak erişim yalnızca belirli bir IP adresi ile sınırlandırıldı:

```text
31.155.229.147/32
```

Ancak kendi bilgisayarımdan yapılan bağlantı başarısız oldu.

Test amacıyla Security Group kuralı şu şekilde değiştirildi:

```text
Type: Custom TCP
Protocol: TCP
Port: 8000
Source: 0.0.0.0/0
```

Bu işlemden sonra uygulamaya internet üzerinden erişilebildi.

Production ortamında uygulama portunu doğrudan `0.0.0.0/0` ile açmak genellikle tercih edilmez.

Daha standart bir web uygulaması yapısı şu şekildedir:

```text
Internet
   ↓
80 / 443
   ↓
Nginx / Reverse Proxy veya Load Balancer
   ↓
Application :8000
```

Bu aşamada ise Docker ve AWS networking zincirini doğrudan test etmek amacıyla `8000` portu açıldı.

---

## 10. Uygulamanın Dışarıdan Test Edilmesi

Uygulama yalnızca EC2 instance içerisinden değil, kendi Windows bilgisayarımdan da test edildi.

EC2'nin Public IPv4 adresine aşağıdaki istek gönderildi:

```bash
curl http://EC2_PUBLIC_IP:8000/tasks
```

Başarılı cevap:

```json
[]
```

Bu sonuç, isteğin kendi bilgisayarımdan internete çıkıp AWS altyapısı üzerinden EC2 içerisindeki Docker container'a ulaştığını gösterdi.

Bağlantı zinciri şu şekildedir:

```text
Kullanıcının Bilgisayarı
        ↓
      Internet
        ↓
EC2 Public IPv4
        ↓
Internet Gateway
        ↓
Route Table
        ↓
Security Group :8000
        ↓
EC2 Instance
        ↓
Docker Port Mapping
        ↓
FastAPI Container :8000
```

Bu test, VPC, public subnet, Internet Gateway, Route Table, Security Group ve Docker port mapping yapılandırmasının uçtan uca çalıştığını doğruladı.

---

## 11. API Üzerinden Task Oluşturulması

Dışarıdan yalnızca GET isteği değil, POST isteği de test edildi.

Windows CMD kullanıldığı için standart `curl` sözdizimi kullanıldı:

```bash
curl -X POST "http://EC2_PUBLIC_IP:8000/tasks" -H "Content-Type: application/json" -d "{\"title\":\"AWS EC2 Test\",\"description\":\"EC2 üzerinden oluşturuldu\"}"
```

Daha sonra oluşturulan task'ı kontrol etmek için tekrar GET isteği gönderildi:

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

Bu test ile aşağıdaki zincirin çalıştığı doğrulandı:

```text
Windows Client
      ↓
Internet
      ↓
EC2 Public IP
      ↓
Security Group
      ↓
FastAPI Container
      ↓
PostgreSQL Container
```

Task, FastAPI üzerinden PostgreSQL veritabanına kaydedildi ve daha sonra tekrar okunabildi.

---

## 12. Öğrenilenler

Bu deployment aşamasında aşağıdaki konular birlikte kullanıldı:

- AWS EC2
- Public ve Private IP
- SSH bağlantısı
- Docker kurulumu
- Docker kullanıcı grubu
- Docker Compose
- Docker port mapping
- GitHub private repository
- Personal Access Token
- AWS Security Group
- Inbound rules
- TCP portları
- VPC
- Public Subnet
- Internet Gateway
- Route Table
- FastAPI deployment
- PostgreSQL container
- Docker network
- Public internet üzerinden API erişimi

---

## 13. Sonuç

FastAPI ve PostgreSQL kullanılarak oluşturulan Task Manager uygulaması Docker Compose ile AWS EC2 üzerinde başarıyla çalıştırıldı.

Uygulama private GitHub repository'den EC2 instance'a çekildi, Docker Compose ile build edilerek çalıştırıldı ve Security Group yapılandırması sayesinde internet üzerinden erişilebilir hale getirildi.

Uygulama kendi bilgisayarımdan EC2 Public IPv4 adresi kullanılarak test edildi.

GET isteği ile API erişimi doğrulandı.

POST isteği ile yeni bir task oluşturuldu ve PostgreSQL veritabanına başarıyla kaydedildi.

Sonrasında GET isteği ile oluşturulan veri tekrar görüntülendi.

Başarılı erişim zinciri:

```text
Client
   ↓
Internet
   ↓
AWS Internet Gateway
   ↓
Public Subnet
   ↓
Security Group
   ↓
EC2
   ↓
Docker
   ↓
FastAPI
   ↓
PostgreSQL
```

Bu aşama ile yerel ortamda containerlaştırılan uygulama gerçek bir AWS EC2 sunucusuna deploy edilmiş ve internet üzerinden erişilebilir hale getirilmiştir.