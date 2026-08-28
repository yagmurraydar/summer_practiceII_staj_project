# 03 - Runbook ve Sorun Giderme

Bu doküman, proje geliştirme, Docker, AWS EC2, ECR ve CI/CD süreçlerinde karşılaşılan sorunları, nedenlerini ve çözümlerini içermektedir.

---

# 1. Docker Port Çakışması

## Problem

Docker Compose çalıştırılırken aşağıdaki benzeri bir hata alınmıştır:

```text
failed to bind host port 0.0.0.0:5432/tcp: address already in use
```

veya:

```text
Bind for 0.0.0.0:8000 failed: port is already allocated
```

## Sebep

İlgili port başka bir uygulama veya Docker container tarafından kullanılmaktadır.

Örneğin:

* PostgreSQL başka bir container tarafından `5432` portunda çalışıyor olabilir.
* FastAPI uygulaması başka bir container tarafından `8000` portunda çalışıyor olabilir.

## Çözüm

Çalışan container'ları kontrol etmek için:

```bash
docker ps
```

Tüm container'ları görmek için:

```bash
docker ps -a
```

Gerekli container durdurulabilir:

```bash
docker stop CONTAINER_ID
```

Daha sonra Docker Compose tekrar çalıştırılabilir:

```bash
docker compose up -d
```

---

# 2. API Container'ın Başlamaması

## Problem

`docker compose up` komutundan sonra API container başlamış ancak kısa süre sonra kapanmıştır.

Loglarda aşağıdaki hata görülmüştür:

```text
sqlalchemy.exc.ArgumentError:
Expected string or URL object, got None
```

## Sebep

Uygulama içerisinde veritabanı bağlantı adresi environment variable üzerinden alınmaktadır:

```python
DATABASE_URL = os.getenv("DATABASE_URL")
```

Ancak container'a `DATABASE_URL` değeri verilmediğinde değer `None` olmaktadır.

Bu nedenle SQLAlchemy bağlantı oluşturamamaktadır.

## Çözüm

`docker-compose.yml` içerisinde API servisine environment variable eklenmiştir:

```yaml
api:
  environment:
    DATABASE_URL: postgresql://myuser:mysecurepassword@postgres:5432/mydatabase
```

Daha sonra container yeniden oluşturulmuştur:

```bash
docker compose up -d
```

---

# 3. PostgreSQL Hazır Olmadan API'nin Başlaması

## Problem

API container, PostgreSQL tamamen başlamadan çalışmaya çalışabilir.

Bu durum veritabanı bağlantı hatalarına neden olabilir.

## Çözüm

PostgreSQL servisine healthcheck eklenmiştir:

```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U myuser -d mydatabase"]
  interval: 5s
  timeout: 5s
  retries: 5
```

API servisi PostgreSQL'in sağlıklı olmasını beklemektedir:

```yaml
depends_on:
  postgres:
    condition: service_healthy
```

Kontrol için:

```bash
docker compose ps
```

PostgreSQL container'ının aşağıdaki durumda olması beklenir:

```text
healthy
```

---

# 4. EC2'ye SSH ile Bağlanamama

## Problem

Windows üzerinden EC2'ye SSH bağlantısı kurulurken hata alınmıştır.

Örneğin:

```text
Could not resolve hostname i
```

## Sebep

SSH komutunda `-i` parametresinin başındaki tire unutulmuştur.

Yanlış kullanım:

```bash
ssh i "C:\Users\Huawei\modules\Downloads\task-manager-key.pem" ubuntu@PUBLIC_IP
```

Burada `i`, hostname olarak yorumlanmaktadır.

## Çözüm

Doğru kullanım:

```bash
ssh -i "C:\Users\Huawei\modules\Downloads\task-manager-key.pem" ubuntu@PUBLIC_IP
```

Örnek:

```bash
ssh -i "C:\Users\Huawei\modules\Downloads\task-manager-key.pem" ubuntu@13.51.48.167
```

EC2 durdurulup tekrar başlatıldığında Public IPv4 adresi değişebilir. Bu durumda AWS Console üzerinden yeni Public IPv4 adresi alınmalıdır.

---

# 5. AWS CLI Bulunamadı

## Problem

EC2 üzerinde aşağıdaki komut çalıştırıldığında:

```bash
aws --version
```

şu hata alınmıştır:

```text
Command 'aws' not found
```

## Sebep

AWS CLI EC2 üzerinde kurulu değildir.

## Çözüm

AWS CLI kurulduktan sonra aşağıdaki komut ile doğrulama yapılmıştır:

```bash
aws --version
```

Başarılı durumda AWS CLI sürüm bilgisi görüntülenmiştir.

---

# 6. AWS Credentials Bulunamadı

## Problem

EC2 üzerinde aşağıdaki komut çalıştırıldığında:

```bash
aws sts get-caller-identity
```

şu hata alınmıştır:

```text
NoCredentials
Unable to locate credentials
```

## Sebep

EC2 instance üzerinde AWS credentials bulunmamaktadır.

## Çözüm

EC2 instance'a IAM Role bağlanmıştır.

Oluşturulan role:

```text
EC2-ECR-ReadOnly-Role
```

Role aşağıdaki policy eklenmiştir:

```text
AmazonEC2ContainerRegistryReadOnly
```

Daha sonra tekrar:

```bash
aws sts get-caller-identity
```

komutu çalıştırılmıştır.

Başarılı sonuçta EC2'nin IAM Role kullandığı doğrulanmıştır.

---

# 7. ECR Image Bulunamadı

## Problem

EC2 üzerinde:

```bash
docker compose pull api
```

komutu çalıştırıldığında image bulunamadığı görülmüştür.

Örnek hata:

```text
failed to resolve reference
image not found
```

## Sebep

Docker Compose içerisinde belirtilen image henüz Amazon ECR'a gönderilmemiş olabilir.

Ayrıca yanlış image tag kullanılmış olabilir.

## Çözüm

GitHub Actions workflow'unun image'ı başarıyla ECR'a gönderdiği kontrol edilmiştir.

Daha sonra:

```bash
docker compose pull api
```

komutu tekrar çalıştırılmıştır.

---

# 8. ECR `latest` Tag Problemi

## Problem

GitHub Actions üzerinden image ECR'a gönderilirken aşağıdaki hata alınmıştır:

```text
The image tag 'latest' already exists in the
'task-manager-api' repository and cannot be overwritten
because the tag is immutable.
```

## Sebep

ECR repository'sinde immutable tag yapılandırması aktiftir.

Bu nedenle mevcut `latest` tag'i tekrar yazılamamaktadır.

## Çözüm

`latest` yerine GitHub commit SHA değeri kullanılmaya başlanmıştır.

Örneğin:

```yaml
docker build -t task-manager-api:${{ github.sha }} .
```

Daha sonra:

```yaml
docker push 274197531864.dkr.ecr.eu-north-1.amazonaws.com/task-manager-api:${{ github.sha }}
```

Bu sayede her commit için benzersiz bir Docker image oluşturulmuştur.

---

# 9. GitHub Actions Workflow'un Çalışmaması

## Problem

GitHub üzerinde yeni workflow'un görünmediği veya beklenen workflow'un çalışmadığı görülmüştür.

## Sebep

Workflow dosyasındaki değişiklik henüz doğru branch'e push edilmemiş olabilir.

Özellikle CD workflow'u yalnızca `main` branch'ine yapılan push işlemlerinde çalışmaktadır:

```yaml
on:
  push:
    branches:
      - main
```

Bu nedenle `test-ci` branch'ine yapılan push işlemleri CD deployment workflow'unu tetiklemez.

## Çözüm

Değişiklikler commit edilmiştir:

```bash
git add .
git commit -m "Add automatic EC2 deployment"
git push
```

Daha sonra Pull Request oluşturulmuş ve `main` branch'ine merge edilmiştir.

Merge işleminden sonra CD workflow'u otomatik olarak çalışmıştır.

---

# 10. Docker Compose'da Eski Image Kullanılması

## Problem

EC2 üzerinde yeni deployment yapılmasına rağmen eski Docker image'ın kullanıldığı görülmüştür.

Kontrol sırasında:

```bash
docker compose config
```

komutu image'ın beklenen tag yerine eski bir tag kullandığını göstermiştir.

## Sebep

`IMAGE_TAG` environment variable değeri doğru şekilde ayarlanmamış olabilir.

Docker Compose dosyasında image şu şekilde tanımlanmıştır:

```yaml
image: 274197531864.dkr.ecr.eu-north-1.amazonaws.com/task-manager-api:${IMAGE_TAG}
```

Ancak `IMAGE_TAG` boş olduğunda veya yanlış olduğunda beklenen image çekilemez.

## Çözüm

Deployment sırasında commit SHA değeri environment variable olarak ayarlanmıştır:

```bash
export IMAGE_TAG=COMMIT_SHA
```

GitHub Actions içerisinde:

```bash
export IMAGE_TAG=${{ github.sha }}
```

kullanılmıştır.

Kontrol için:

```bash
docker compose config
```

komutu kullanılabilir.

---

# 11. Deployment Sonrası API'nin Görünmemesi

## Problem

Deployment sonrasında:

```bash
docker compose ps
```

komutunda yalnızca PostgreSQL container'ı görünmüştür.

API container çalışmamaktadır.

## Sebep

API container başlatılırken hata almış ve kapanmıştır.

## Çözüm

Container logları kontrol edilmiştir:

```bash
docker compose logs api
```

veya:

```bash
docker logs task_manager_api
```

Loglarda `DATABASE_URL` değerinin bulunamadığı görülmüş ve environment variable eklenerek sorun çözülmüştür.

Daha sonra:

```bash
docker compose pull api
docker compose up -d
```

komutları çalıştırılmıştır.

---

# 12. API'nin `/` Endpoint'inde 404 Dönmesi

## Problem

Aşağıdaki komut çalıştırıldığında:

```bash
curl http://localhost:8000
```

şu cevap alınmıştır:

```json
{"detail":"Not Found"}
```

## Sebep

FastAPI uygulamasında `/` endpoint'i tanımlanmamıştır.

Bu durum API'nin çalışmadığı anlamına gelmez.

## Çözüm

Mevcut endpoint kullanılarak test yapılmıştır:

```bash
curl http://localhost:8000/tasks
```

Başarılı durumda görev listesi JSON formatında döndürülmüştür.

---

# 13. EC2 Üzerinde Deployment Kontrol Komutları

## Container durumlarını kontrol etmek

```bash
docker compose ps
```

## API loglarını görmek

```bash
docker compose logs api
```

Canlı logları görmek için:

```bash
docker compose logs -f api
```

## Yeni API image'ını ECR'dan çekmek

```bash
docker compose pull api
```

## Container'ları yeniden başlatmak

```bash
docker compose up -d
```

## API'yi test etmek

```bash
curl http://localhost:8000/tasks
```

---

# 14. GitHub Actions Deployment Akışı

Başarılı deployment süreci aşağıdaki şekilde çalışmaktadır:

```text
Kod değişikliği
      │
      ▼
test-ci
      │
      ▼
CI Kontrolleri
      │
      ▼
Pull Request
      │
      ▼
main
      │
      ▼
GitHub Actions CD
      │
      ├── Docker Build
      │
      ├── Amazon ECR Push
      │
      └── SSH
            │
            ▼
           EC2
            │
            ├── git pull
            │
            ├── IMAGE_TAG ayarla
            │
            ├── docker compose pull
            │
            └── docker compose up -d
```

---

# 15. Son Kontrol Listesi

Deployment sonrasında aşağıdaki kontroller yapılmalıdır.

EC2'ye bağlan:

```bash
ssh -i "PRIVATE_KEY_PATH" ubuntu@PUBLIC_IP
```

Proje dizinine git:

```bash
cd ~/summer_practiceII_staj_project
```

Container durumlarını kontrol et:

```bash
docker compose ps
```

API container çalışmıyorsa logları kontrol et:

```bash
docker compose logs api
```

API'yi test et:

```bash
curl http://localhost:8000/tasks
```

Başarılı durumda FastAPI ve PostgreSQL servislerinin birlikte çalıştığı doğrulanmış olur.

---

# Sonuç

Bu Runbook, proje boyunca Docker, PostgreSQL, AWS EC2, IAM, ECR ve GitHub Actions süreçlerinde karşılaşılan gerçek sorunları ve uygulanan çözümleri içermektedir.

En sık kullanılan kontrol akışı:

```text
SSH ile EC2'ye bağlan
        │
        ▼
docker compose ps
        │
        ▼
Container çalışmıyorsa logs kontrol et
        │
        ▼
docker compose pull api
        │
        ▼
docker compose up -d
        │
        ▼
curl ile API test et
```

Bu adımlar sayesinde deployment ve container problemleri sistematik olarak kontrol edilip çözülebilir.
