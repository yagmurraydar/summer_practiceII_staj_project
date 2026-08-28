# 07 - CI/CD ve Otomatik Deployment

## 1. Amaç

Bu projenin amacı, FastAPI ve PostgreSQL kullanılarak oluşturulan Task Manager uygulamasının AWS üzerinde çalıştırılması ve uygulamanın güncelleme sürecinin CI/CD yaklaşımıyla otomatik hale getirilmesidir.

Projenin genel çalışma yapısı aşağıdaki gibidir:

```text
Geliştirme
    │
    ▼
test-ci Branch
    │
    ▼
GitHub Actions - CI
    │
    ▼
Pull Request
    │
    ▼
main Branch
    │
    ▼
GitHub Actions - CD
    │
    ▼
Docker Image Build
    │
    ▼
Amazon ECR
    │
    ▼
SSH ile EC2'ye Bağlantı
    │
    ▼
Docker Compose
    │
    ├── FastAPI
    │
    └── PostgreSQL
```

Bu yapı sayesinde uygulamada yapılan değişiklikler GitHub üzerinden kontrol edilmekte ve `main` branch'ine gönderilen güncel kod otomatik olarak AWS EC2 ortamına deploy edilmektedir.

---

# 2. Kullanılan Teknolojiler

Projede aşağıdaki teknolojiler kullanılmıştır:

* Python
* FastAPI
* PostgreSQL
* SQLAlchemy
* Docker
* Docker Compose
* GitHub
* GitHub Actions
* AWS EC2
* AWS ECR
* AWS IAM
* AWS CLI
* SSH

---

# 3. Docker ile Containerlaştırma

Uygulama iki temel servisten oluşmaktadır:

1. FastAPI uygulaması
2. PostgreSQL veritabanı

Bu servisler Docker Compose ile birlikte çalıştırılmıştır.

Temel yapı:

```text
Docker Compose
      │
      ├── postgres
      │      │
      │      └── PostgreSQL Database
      │
      └── api
             │
             └── FastAPI Application
```

PostgreSQL servisi aşağıdaki image kullanılarak oluşturulmuştur:

```text
postgres:16-alpine
```

API servisi ise FastAPI uygulamasını çalıştırmaktadır.

---

# 4. PostgreSQL Healthcheck

API'nin veritabanı tamamen hazır olmadan başlamasını engellemek için PostgreSQL servisine healthcheck eklenmiştir.

```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U myuser -d mydatabase"]
  interval: 5s
  timeout: 5s
  retries: 5
```

API servisinde ise PostgreSQL'in sağlıklı durumda olması beklenmektedir.

```yaml
depends_on:
  postgres:
    condition: service_healthy
```

Bu sayede çalışma sırası şu şekilde olmaktadır:

```text
PostgreSQL başlar
        │
        ▼
Healthcheck çalışır
        │
        ▼
PostgreSQL Healthy olur
        │
        ▼
FastAPI başlar
```

Bu yapı, API'nin veritabanı henüz hazır değilken başlaması sonucu oluşabilecek bağlantı hatalarını azaltmaktadır.

---

# 5. AWS EC2 Üzerinde Deployment

Uygulama AWS EC2 üzerinde Ubuntu işletim sistemi kullanılarak çalıştırılmıştır.

EC2 instance üzerinde:

* Docker kurulmuştur.
* Docker Compose kullanılmıştır.
* AWS CLI kurulmuştur.
* GitHub repository'si clone edilmiştir.

Proje EC2 üzerinde aşağıdaki dizinde bulunmaktadır:

```text
~/summer_practiceII_staj_project
```

İlk deployment testlerinde uygulama aşağıdaki komut ile çalıştırılmıştır:

```bash
docker compose up -d
```

Container durumları şu komut ile kontrol edilmiştir:

```bash
docker compose ps
```

Başarılı çalışmada aşağıdaki servisler görülmüştür:

```text
postgres_db
task_manager_api
```

---

# 6. API'nin Test Edilmesi

EC2 üzerinde çalışan FastAPI uygulaması `curl` kullanılarak test edilmiştir.

Örneğin:

```bash
curl http://localhost:8000/tasks
```

Başarılı durumda uygulama veritabanındaki görevleri JSON formatında döndürmüştür.

Örnek çıktı:

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

Bu test ile aşağıdaki yapı doğrulanmıştır:

```text
FastAPI
   │
   ▼
SQLAlchemy
   │
   ▼
PostgreSQL
```

---

# 7. CI Süreci

CI sürecinde GitHub Actions kullanılmıştır.

Geliştirme işlemleri doğrudan `main` branch'i üzerinde yapılmamıştır.

Bunun yerine:

```text
test-ci
```

branch'i kullanılmıştır.

Çalışma süreci:

```text
Kod değişikliği
      │
      ▼
test-ci branch
      │
      ▼
GitHub'a push
      │
      ▼
GitHub Actions CI
      │
      ▼
Pull Request
      │
      ▼
main
```

Değişiklikler GitHub'a aşağıdaki Git komutları ile gönderilmiştir:

```bash
git add .
git commit -m "Commit message"
git push
```

GitHub üzerinde Pull Request oluşturulmuş ve CI kontrollerinin başarılı olduğu görülmüştür.

Başarılı CI sonucunda:

```text
All checks have passed
```

veya:

```text
1 / 1 checks OK
```

durumu görülmüştür.

---

# 8. Amazon ECR Kullanımı

Docker image'larının saklanması için Amazon Elastic Container Registry (ECR) kullanılmıştır.

Oluşturulan repository:

```text
task-manager-api
```

ECR repository adresi:

```text
274197531864.dkr.ecr.eu-north-1.amazonaws.com/task-manager-api
```

CD sürecinde GitHub Actions tarafından oluşturulan Docker image bu repository'ye gönderilmektedir.

Genel yapı:

```text
GitHub Actions
       │
       ▼
Docker Build
       │
       ▼
Amazon ECR
       │
       ▼
EC2 Docker Pull
```

---

# 9. GitHub Secrets Kullanımı

AWS erişim bilgilerinin workflow dosyası içerisinde açık olarak yazılmaması için GitHub Secrets kullanılmıştır.

AWS için aşağıdaki secret'lar eklenmiştir:

```text
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
```

EC2'ye SSH bağlantısı için ise:

```text
EC2_HOST
EC2_USER
EC2_SSH_KEY
```

secret'ları kullanılmıştır.

Workflow içerisinde AWS credentials şu şekilde kullanılmaktadır:

```yaml
aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
```

EC2 bağlantısı için:

```yaml
host: ${{ secrets.EC2_HOST }}
username: ${{ secrets.EC2_USER }}
key: ${{ secrets.EC2_SSH_KEY }}
```

Bu yöntem sayesinde hassas bilgiler repository içerisine doğrudan yazılmamıştır.

---

# 10. EC2'nin ECR'a Erişimi

EC2 instance'ın ECR'dan Docker image çekebilmesi için IAM Role oluşturulmuştur.

Oluşturulan role:

```text
EC2-ECR-ReadOnly-Role
```

Role aşağıdaki AWS managed policy eklenmiştir:

```text
AmazonEC2ContainerRegistryReadOnly
```

Bu sayede EC2 üzerinde AWS Access Key ve Secret Key saklamadan ECR repository'sine erişim sağlanmıştır.

Role bağlantısını kontrol etmek için:

```bash
aws sts get-caller-identity
```

komutu kullanılmıştır.

Başarılı sonuçta EC2'nin aşağıdaki role üzerinden çalıştığı görülmüştür:

```text
assumed-role/EC2-ECR-ReadOnly-Role
```

Bu yöntem, uzun süreli AWS erişim anahtarlarını EC2 içerisinde saklamamak açısından daha güvenli bir yaklaşımdır.

---

# 11. İlk Karşılaşılan Sorun: AWS CLI

EC2 üzerinde ilk başta AWS CLI bulunmamaktaydı.

Aşağıdaki komut çalıştırıldığında:

```bash
aws --version
```

AWS CLI'ın bulunamadığı görülmüştür.

İlk olarak:

```bash
sudo apt install awscli -y
```

komutu denenmiştir ancak uygun paket bulunamadığı için kurulum gerçekleştirilememiştir.

Daha sonra AWS CLI başarıyla kurulmuş ve:

```bash
aws --version
```

komutu ile doğrulanmıştır.

---

# 12. İlk Karşılaşılan Sorun: EC2'de AWS Credentials Bulunamaması

AWS CLI kurulduktan sonra aşağıdaki komut çalıştırılmıştır:

```bash
aws sts get-caller-identity
```

Ancak başlangıçta:

```text
NoCredentials
Unable to locate credentials
```

hatası alınmıştır.

Bu sorun, EC2 instance'a IAM Role atanarak çözülmüştür.

`EC2-ECR-ReadOnly-Role` instance'a bağlandıktan sonra aynı komut başarılı şekilde çalışmıştır.

---

# 13. İlk ECR Problemi: Immutable latest Tag

İlk CD workflow'unda Docker image aşağıdaki tag ile ECR'a gönderilmeye çalışılmıştır:

```text
latest
```

Ancak ECR repository'sinde tag immutability aktif olduğu için aynı `latest` tag'i ikinci kez gönderilememiştir.

Alınan hata:

```text
The image tag 'latest' already exists in the
'task-manager-api' repository and cannot be overwritten
because the tag is immutable.
```

Bu sorunu çözmek için `latest` yerine GitHub commit SHA değeri kullanılmaya başlanmıştır.

---

# 14. Commit SHA ile Docker Image Tag Kullanımı

Her deployment için benzersiz bir Docker image oluşturmak amacıyla:

```text
${{ github.sha }}
```

kullanılmıştır.

Docker image build işlemi:

```yaml
docker build -t task-manager-api:${{ github.sha }} .
```

Image ECR adresi ile tag'lenmektedir:

```yaml
docker tag task-manager-api:${{ github.sha }} 274197531864.dkr.ecr.eu-north-1.amazonaws.com/task-manager-api:${{ github.sha }}
```

Daha sonra image ECR'a gönderilmektedir:

```yaml
docker push 274197531864.dkr.ecr.eu-north-1.amazonaws.com/task-manager-api:${{ github.sha }}
```

Bu sayede her commit için farklı bir Docker image oluşmaktadır.

```text
Commit A
   │
   ▼
Image: SHA-A

Commit B
   │
   ▼
Image: SHA-B

Commit C
   │
   ▼
Image: SHA-C
```

Bu yöntem deployment geçmişinin takip edilmesini kolaylaştırmaktadır.

---

# 15. DATABASE_URL Problemi

Deployment sırasında API container'ı başlatıldığında aşağıdaki hata alınmıştır:

```text
sqlalchemy.exc.ArgumentError:
Expected string or URL object, got None
```

Sorunun nedeni container içerisindeki uygulamanın:

```python
DATABASE_URL = os.getenv("DATABASE_URL")
```

şeklinde environment variable beklemesiydi.

Ancak Docker Compose yapılandırmasında bu değer tanımlanmamıştı.

Çözüm olarak API servisine aşağıdaki environment variable eklenmiştir:

```yaml
environment:
  DATABASE_URL: postgresql://myuser:mysecurepassword@postgres:5432/mydatabase
```

Böylece FastAPI uygulaması PostgreSQL bağlantı adresini environment variable üzerinden alabilmiştir.

---

# 16. Docker Compose'un ECR Image Kullanacak Şekilde Güncellenmesi

İlk yapılandırmada API servisi lokal olarak build ediliyordu:

```yaml
build: .
```

CI/CD yapısında ise amaç EC2 üzerinde tekrar image build etmek yerine GitHub Actions tarafından oluşturulan image'ın ECR'dan çekilmesidir.

Bu nedenle API servisi aşağıdaki şekilde değiştirilmiştir:

```yaml
api:
  image: 274197531864.dkr.ecr.eu-north-1.amazonaws.com/task-manager-api:${IMAGE_TAG}

  container_name: task_manager_api

  environment:
    DATABASE_URL: postgresql://myuser:mysecurepassword@postgres:5432/mydatabase

  ports:
    - "8000:8000"

  depends_on:
    postgres:
      condition: service_healthy
```

Bu yapı sayesinde EC2:

```text
Docker Build yapmaz
        │
        ▼
ECR'dan hazır image çeker
        │
        ▼
Container'ı başlatır
```

---

# 17. IMAGE_TAG Kullanımı

Docker Compose dosyasında image tag değeri:

```text
${IMAGE_TAG}
```

ile alınmaktadır.

Deployment sırasında GitHub Actions tarafından EC2 üzerinde aşağıdaki komut çalıştırılmaktadır:

```bash
export IMAGE_TAG=${{ github.sha }}
```

Böylece süreç şu şekilde çalışmaktadır:

```text
GitHub Commit
      │
      ▼
github.sha
      │
      ▼
Docker Image Tag
      │
      ▼
IMAGE_TAG
      │
      ▼
docker-compose.yml
      │
      ▼
Doğru ECR Image
```

---

# 18. CD Workflow

CD workflow dosyası:

```text
.github/workflows/cd.yml
```

konumunda bulunmaktadır.

Workflow sadece `main` branch'ine yapılan push işlemlerinde çalışmaktadır:

```yaml
on:
  push:
    branches:
      - main
```

CD sürecinin temel aşamaları:

1. Repository checkout
2. AWS credentials yapılandırması
3. Amazon ECR login
4. Docker image build
5. Docker image'ı ECR'a push
6. SSH ile EC2'ye bağlanma
7. EC2 repository'sini güncelleme
8. ECR'dan yeni image'ı çekme
9. Docker Compose ile yeni container'ı başlatma

Genel CD akışı:

```text
main'e Push
     │
     ▼
GitHub Actions
     │
     ├── AWS Authentication
     │
     ├── Docker Build
     │
     ├── ECR Push
     │
     └── SSH
           │
           ▼
          EC2
           │
           ├── git pull
           │
           ├── docker compose pull
           │
           └── docker compose up -d
```

---

# 19. SSH ile EC2 Deployment

GitHub Actions'ın EC2'ye bağlanması için SSH Action kullanılmıştır.

Workflow içerisinde:

```yaml
- name: Deploy to EC2
  uses: appleboy/ssh-action@v1.2.0
  with:
    host: ${{ secrets.EC2_HOST }}
    username: ${{ secrets.EC2_USER }}
    key: ${{ secrets.EC2_SSH_KEY }}
```

EC2 üzerinde çalıştırılan temel deployment komutları:

```bash
cd ~/summer_practiceII_staj_project
git pull origin main
export IMAGE_TAG=${{ github.sha }}
docker compose pull api
docker compose up -d
```

Bu işlem aşağıdaki sırayla çalışmaktadır:

```text
GitHub Actions
      │
      ▼
SSH ile EC2'ye bağlanır
      │
      ▼
Repository güncellenir
      │
      ▼
IMAGE_TAG ayarlanır
      │
      ▼
Yeni image ECR'dan çekilir
      │
      ▼
Docker Compose çalıştırılır
      │
      ▼
Yeni API container başlatılır
```

---

# 20. Son CI/CD Yapısı

Projenin son CI/CD mimarisi aşağıdaki gibidir:

```text
                ┌─────────────────┐
                │   Developer     │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │     GitHub      │
                │    test-ci      │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │ GitHub Actions  │
                │       CI        │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │  Pull Request   │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │      main       │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │ GitHub Actions  │
                │       CD        │
                └────────┬────────┘
                         │
              ┌──────────┴──────────┐
              │                     │
              ▼                     ▼
     ┌─────────────────┐   ┌─────────────────┐
     │ Docker Build    │   │   SSH to EC2    │
     └────────┬────────┘   └────────┬────────┘
              │                     │
              ▼                     │
     ┌─────────────────┐            │
     │   Amazon ECR    │◄───────────┘
     └────────┬────────┘
              │
              ▼
     ┌─────────────────┐
     │ Docker Compose  │
     │      EC2        │
     └────────┬────────┘
              │
        ┌─────┴─────┐
        ▼           ▼
    FastAPI     PostgreSQL
```

---

# 21. Deployment Sonrası Kontrol

Deployment işlemi tamamlandıktan sonra EC2 üzerinde container durumları kontrol edilmiştir:

```bash
docker compose ps
```

Başarılı durumda aşağıdaki servislerin çalıştığı görülmüştür:

```text
postgres_db
task_manager_api
```

API container'ın 8000 portunu dinlediği görülmüştür:

```text
0.0.0.0:8000->8000/tcp
```

Uygulama aşağıdaki komut ile test edilmiştir:

```bash
curl http://localhost:8000/tasks
```

API'nin PostgreSQL'deki görevleri başarıyla döndürdüğü görülmüştür.

---

# 22. Sonuç

Bu projede FastAPI tabanlı Task Manager uygulaması PostgreSQL ile birlikte Docker kullanılarak containerlaştırılmıştır.

Uygulama AWS EC2 üzerinde çalıştırılmış ve Docker image'larının saklanması için Amazon ECR kullanılmıştır.

GitHub Actions ile CI/CD süreci oluşturulmuştur.

CI sürecinde geliştirme branch'i üzerinden yapılan değişiklikler kontrol edilmiş ve Pull Request kullanılarak `main` branch'ine aktarılmıştır.

CD sürecinde ise:

```text
main'e push
      │
      ▼
GitHub Actions çalışır
      │
      ▼
Docker image build edilir
      │
      ▼
Amazon ECR'a gönderilir
      │
      ▼
SSH ile EC2'ye bağlanılır
      │
      ▼
Yeni image ECR'dan çekilir
      │
      ▼
Docker Compose ile uygulama güncellenir
```

Bu yapı sayesinde uygulamanın deployment süreci manuel işlem gerektirmeden büyük ölçüde otomatik hale getirilmiştir.

Ayrıca deployment sırasında karşılaşılan sorunlar çözülerek:

* AWS CLI eksikliği
* EC2 credentials problemi
* ECR immutable tag problemi
* `DATABASE_URL` environment variable problemi
* ECR image kullanımına geçiş
* Commit SHA ile benzersiz image tag kullanımı
* GitHub Actions üzerinden SSH ile otomatik EC2 deployment

başarıyla tamamlanmıştır.

Son durumda proje:

```text
GitHub
   ↓
CI
   ↓
Pull Request
   ↓
main
   ↓
CD
   ↓
Docker Build
   ↓
Amazon ECR
   ↓
EC2
   ↓
Docker Compose
   ↓
FastAPI + PostgreSQL
```

şeklinde çalışan bir CI/CD mimarisine sahiptir.
