<img width="1024" height="1536" alt="portfolyo " src="https://github.com/user-attachments/assets/0cb389d7-94e7-4f41-86ad-347f9484160b" />#  Cloud-Native DevOps Capstone Project

## Task Manager API – CI/CD Pipeline with AWS, Docker and Kubernetes

Bu proje, FastAPI tabanlı bir **Task Manager API** uygulamasının Docker ile containerize edilmesini, Docker Compose ile PostgreSQL veritabanı ile birlikte çalıştırılmasını, Kubernetes üzerinde yerel olarak yönetilmesini ve AWS altyapısı üzerinde GitHub Actions kullanılarak CI/CD süreçlerinin uygulanmasını kapsamaktadır.

Proje boyunca **Linux, Networking, Git, Docker, Docker Compose, Kubernetes (kind), AWS IAM/VPC/EC2/ECR ve GitHub Actions** teknolojileri kullanılarak uçtan uca bir DevOps çalışma ortamı oluşturulmuştur.

---

# Mimari Diyagram

```text
GitHub
(Push / Pull Request)
        │
        ▼
GitHub Actions
CI Pipeline
        │
        ▼
main Branch'e Merge
        │
        ▼
GitHub Actions
CD Pipeline
(Docker Build)
        │
        ▼
Amazon ECR
(Commit SHA ile Image Push)
        │
        ▼
SSH
        │
        ▼
AWS EC2
(git pull + docker compose up)
        │
        ▼
Docker Compose
        │
        ├──────────────► FastAPI API
        │
        └──────────────► PostgreSQL
```

## CI/CD Akışı

Projedeki temel CI/CD akışı aşağıdaki şekildedir:

1. Geliştirici kod üzerinde değişiklik yapar ve GitHub'a push eder veya Pull Request açar.
2. GitHub Actions üzerinden CI süreci tetiklenir.
3. Test kontrolleri gerçekleştirilir.
4. Kod `main` branch'ine merge edilir.
5. GitHub Actions CD pipeline'ı çalışır.
6. Docker image oluşturulur.
7. Image, commit SHA kullanılarak tag edilir.
8. Docker image Amazon ECR'a push edilir.
9. AWS EC2 sunucusunda uygulama Docker Compose ile çalıştırılır.
10. FastAPI uygulaması ve PostgreSQL veritabanı Docker ağı üzerinde birlikte çalışır.

---

# 🛠️ Kullanılan Teknolojiler

| Teknoloji          | Kullanım Amacı                                              |
| ------------------ | ----------------------------------------------------------- |
| **Linux / Ubuntu** | Sunucu ve geliştirme ortamı                                 |
| **Networking**     | IP, subnet, route ve bağlantı kontrolleri                   |
| **SSH**            | Sunucuya güvenli bağlantı                                   |
| **UFW**            | Firewall yönetimi                                           |
| **Systemd**        | Servis yönetimi                                             |
| **Git & GitHub**   | Versiyon kontrolü ve kaynak kod yönetimi                    |
| **GitHub Actions** | CI/CD otomasyonu                                            |
| **Docker**         | Uygulamanın containerize edilmesi                           |
| **Docker Compose** | FastAPI ve PostgreSQL servislerinin birlikte çalıştırılması |
| **FastAPI**        | Backend REST API                                            |
| **PostgreSQL**     | İlişkisel veritabanı                                        |
| **Kubernetes**     | Container orchestration pratiği                             |
| **kind**           | Yerel Kubernetes cluster oluşturulması                      |
| **AWS IAM**        | Yetki ve erişim yönetimi                                    |
| **AWS VPC**        | Ağ altyapısının oluşturulması                               |
| **AWS EC2**        | Uygulamanın çalıştırıldığı bulut sunucusu                   |
| **Amazon ECR**     | Docker image registry                                       |

---


## IAM Role kullanımı

AWS üzerinde uzun süreli Access Key bilgilerini doğrudan sunucuda kullanmak yerine IAM Role yaklaşımı tercih edildi.

Bu kararın temel sebepleri şunlardır:

* Uzun süreli Access Key kullanımının güvenlik riskini azaltmak
* AWS kaynaklarına yalnızca gerekli yetkileri vermek
* Root kullanıcı ile işlem yapmamak
* Sunucu ile AWS servisleri arasındaki erişimi daha güvenli yönetmek

Bu yaklaşım, AWS güvenlik prensiplerinden biri olan **Least Privilege (En Az Yetki)** mantığına uygundur.

---

##  `latest` yerine Commit SHA Tagging

Docker image'larında yalnızca `latest` etiketi kullanmak yerine her image'ın belirli bir kod versiyonu ile ilişkilendirilebilmesi için Git Commit SHA kullanılması tercih edildi.

Örneğin:

```text
task-manager-api:latest
```

yerine:

```text
task-manager-api:a1b2c3d
```

şeklinde benzersiz bir tag kullanılabilir.

Bu yaklaşım sayesinde:

* Her deployment'ın hangi kod versiyonuna ait olduğu takip edilebilir.
* Docker image versiyonları birbirinden ayrılır.
* Hatalı bir deployment durumunda önceki image'a dönmek kolaylaşır.
* CI/CD sürecinde daha iyi izlenebilirlik sağlanır.

---

##  EKS yerine kind kullanımı

AWS EKS gerçek bir production Kubernetes çözümü olmasına rağmen maliyet oluşturabileceği için Kubernetes öğrenme ve geliştirme ortamında **kind** kullanıldı.

kind sayesinde:

* Yerel bilgisayarda Kubernetes cluster oluşturuldu.
* Deployment ve Service gibi Kubernetes kaynakları uygulandı.
* `kubectl` komutları ile pod ve servis yönetimi pratiği yapıldı.
* AWS üzerinde sürekli çalışan bir Kubernetes cluster maliyetinden kaçınıldı.

Bu proje için amaç Kubernetes kavramlarını öğrenmek ve uygulamak olduğu için kind, maliyet açısından uygun bir çözüm oldu.

---

##  Sadece Public Subnet kullanımı

AWS altyapısında NAT Gateway ek maliyet oluşturabileceği için proje kapsamında maliyetleri kontrol altında tutmak amacıyla public subnet yapısı kullanıldı.

Bu yapı sayesinde:

* EC2 instance internete erişebilir.
* SSH ile sunucuya bağlantı kurulabilir.
* Docker image ve uygulama deployment işlemleri gerçekleştirilebilir.

Production ortamlarında private subnet ve NAT Gateway mimarisi daha uygun olabilir. Ancak bu proje kapsamında AWS maliyetlerini düşük tutmak öncelikli olduğu için public subnet kullanıldı.

---

#  Kurulum ve Çalıştırma

## Gereksinimler

Projeyi çalıştırmak için aşağıdaki araçların yüklü olması gerekir:

* Git
* Docker
* Docker Compose
* kind
* kubectl

---

## 1. Repoyu Klonla

Terminal üzerinden aşağıdaki komutu çalıştır:

```bash
git clone https://github.com/yagmurraydar/summer_practiceII_staj_project.git
```

Ardından proje klasörüne gir:

```bash
cd summer_practiceII_staj_project
```

---

## 2. Docker Compose ile Uygulamayı Çalıştır

FastAPI uygulaması ve PostgreSQL veritabanını birlikte başlatmak için:

```bash
docker compose up --build
```

Container'ları arka planda çalıştırmak için:

```bash
docker compose up -d --build
```

Çalışan servisleri kontrol etmek için:

```bash
docker compose ps
```

Logları görüntülemek için:

```bash
docker compose logs -f
```

---

## 3. API'yi Test Et

FastAPI uygulaması çalıştıktan sonra Swagger arayüzüne aşağıdaki adres üzerinden erişilebilir:

```text
http://localhost:8000/docs
```

Ana endpoint'i test etmek için:

```bash
curl http://127.0.0.1:8000/
```

Task oluşturmak için örnek bir istek:

```bash
curl -X POST "http://127.0.0.1:8000/tasks" \
-H "Content-Type: application/json" \
-d '{"title":"DevOps Project","description":"Task Manager API test"}'
```

---

# Kubernetes ile Çalıştırma

Bu projede Kubernetes pratiği için **kind** kullanılmıştır.

Cluster oluşturmak için:

```bash
kind create cluster --name task-manager
```

Cluster durumunu kontrol etmek için:

```bash
kubectl get nodes
```

Çalışan pod'ları görüntülemek için:

```bash
kubectl get pods
```

Projede oluşturulan pod:

```text
task-manager-api-7d6b8c5965-h8gst
```

Pod detaylarını görüntülemek için:

```bash
kubectl describe pod task-manager-api-7d6b8c5965-h8gst
```

Pod loglarını görüntülemek için:

```bash
kubectl logs task-manager-api-7d6b8c5965-h8gst
```

Kubernetes servislerini kontrol etmek için:

```bash
kubectl get services
```

Deployment'ları görüntülemek için:

```bash
kubectl get deployments
```

---

#  CI/CD Pipeline

Projede Continuous Integration ve Continuous Deployment süreçleri **GitHub Actions** kullanılarak oluşturulmuştur.

## CI Süreci

Kod üzerinde yapılan değişiklikler ve Pull Request süreçlerinde otomatik kontroller çalıştırılır.

Temel CI adımları:

1. Repository checkout edilir.
2. Gerekli bağımlılıklar yüklenir.


Bu sürecin amacı, kod `main` branch'ine ulaşmadan önce temel kalite kontrollerinin otomatik olarak gerçekleştirilmesidir.

---

## CD Süreci

Kod `main` branch'ine merge edildiğinde deployment süreci başlatılır.

Temel CD akışı:

```text
main Branch
    │
    ▼
GitHub Actions
    │
    ▼
AWS Credentials
    │
    ▼
Amazon ECR Login
    │
    ▼
Docker Image Build
    │
    ▼
Commit SHA ile Tag
    │
    ▼
Amazon ECR Push
    │
    ▼
EC2 Deployment
```

Bu süreçte Docker image Amazon ECR'a gönderilir ve uygulamanın AWS üzerindeki deployment sürecinde Docker tabanlı çalışma ortamı kullanılır.

---

#  Docker Yapısı

Uygulama container ortamında çalışacak şekilde yapılandırılmıştır.

Docker Compose içerisinde iki temel servis bulunur:

```text
FastAPI Application
        │
        │ Docker Network
        ▼
PostgreSQL Database
```

Docker Compose sayesinde servisler aynı ağ üzerinde birbirleriyle iletişim kurabilir.

Uygulama, Docker ağı içerisinde PostgreSQL veritabanına `localhost` üzerinden değil, servis adı üzerinden bağlanmalıdır.

Örneğin:

```text
postgres
```

Docker Compose içerisinde servis adı olarak kullanılan `postgres`, FastAPI uygulamasının veritabanına ulaşmasını sağlar.

---

#  AWS Altyapısı

Proje kapsamında AWS üzerinde aşağıdaki servisler ve kavramlar kullanılmıştır.

## IAM

AWS kaynaklarına erişim için root kullanıcı yerine IAM kullanıcıları ve yetkilendirme yapıları kullanıldı.

IAM ile:

* Kullanıcı oluşturma
* Yetki yönetimi
* MFA kullanımı
* AWS CLI kimlik doğrulama
* Access Key yönetimi

konularında çalışma yapıldı.

---

## VPC

AWS üzerindeki ağ altyapısını anlamak için aşağıdaki kavramlar uygulamalı olarak çalışıldı:

* VPC
* CIDR
* Public Subnet
* Internet Gateway
* Route Table
* Security Group

Bu yapı sayesinde EC2 instance'ın internet erişimi ve dış bağlantıları yapılandırıldı.

---

## EC2

Ubuntu tabanlı bir EC2 instance oluşturularak uygulamanın AWS üzerinde çalıştırılması sağlandı.

EC2 üzerinde:

* SSH bağlantısı
* Docker kurulumu
* Docker Compose kurulumu
* Git ile repository yönetimi
* Container çalıştırma

işlemleri gerçekleştirildi.

---

## Amazon ECR

Docker image'larının merkezi bir registry üzerinde saklanması için Amazon ECR kullanıldı.

CI/CD sürecinde:

1. Docker image oluşturulur.
2. Image benzersiz bir tag ile etiketlenir.
3. Amazon ECR'a giriş yapılır.
4. Image ECR repository'sine push edilir.

Bu sayede uygulamanın container image'ları AWS üzerinde merkezi olarak saklanabilir.

---

SSH servis durumunu kontrol etmek için:

```bash
sudo systemctl status ssh
```

---



```

---

# Öğrenilen Konular

Bu proje boyunca aşağıdaki DevOps ve Cloud konularında uygulamalı çalışma yapıldı:

* Linux sistem yönetimi
* SSH key authentication
* UFW firewall yönetimi
* Networking ve IP/Subnet mantığı
* VPC ve CIDR
* Public Subnet
* Internet Gateway
* Route Table
* Security Group
* Git branch yönetimi
* GitHub Pull Request süreçleri
* Docker containerization
* Docker Compose
* Container networking
* PostgreSQL container kullanımı
* Kubernetes temel kaynakları
* kind ile local Kubernetes cluster
* Pod ve Service yönetimi
* AWS IAM
* AWS EC2
* Amazon ECR
* GitHub Actions
* CI/CD pipeline
* Docker image tagging
* Troubleshooting
* Runbook oluşturma

---

# Projenin Amacı

Bu projenin temel amacı basit bir Task Manager uygulaması geliştirmekten ziyade, bir uygulamanın geliştirme ortamından başlayarak containerize edilmesi, test edilmesi, Kubernetes ortamında çalıştırılması, AWS altyapısı üzerinde deploy edilmesi ve CI/CD süreçleri ile otomatikleştirilmesi sürecini uygulamalı olarak öğrenmektir.

Proje boyunca aşağıdaki sorulara uygulamalı olarak cevap aranmıştır:

* Bir uygulama nasıl containerize edilir?
* Birden fazla container nasıl birlikte çalışır?
* Docker Compose servisler arasındaki iletişimi nasıl yönetir?
* Kubernetes container'ları nasıl yönetir?
* Pod ve Service kavramları nasıl çalışır?
* AWS üzerinde ağ altyapısı nasıl oluşturulur?
* Docker image'ları Amazon ECR üzerinde nasıl saklanır?
* GitHub Actions ile CI/CD pipeline nasıl oluşturulur?
* Bir deployment veya bağlantı problemi oluştuğunda nasıl troubleshooting yapılır?

---

# Sonuç

Bu proje ile FastAPI tabanlı bir Task Manager API uygulaması; Docker, Docker Compose, Kubernetes, AWS servisleri ve GitHub Actions kullanılarak uçtan uca bir DevOps çalışma ortamında ele alındı.

Proje kapsamında Linux ve networking temellerinden başlayarak uygulamanın containerize edilmesi, PostgreSQL ile birlikte Docker Compose üzerinde çalıştırılması, Kubernetes üzerinde yönetilmesi, AWS VPC ve EC2 altyapısının oluşturulması, Docker image'larının Amazon ECR'a gönderilmesi ve GitHub Actions ile CI/CD süreçlerinin otomatikleştirilmesi üzerine çalışıldı.

Süreç boyunca yalnızca başarılı kurulumlar değil, gerçek geliştirme problemleri de dokümante edildi. SSH bağlantı problemleri, Docker port çakışmaları, PostgreSQL hostname sorunları, Kubernetes YAML hataları ve CI/CD süreçleri sırasında karşılaşılan durumlar Runbook içerisinde kayıt altına alındı.

Bu sayede proje, yalnızca çalışan bir uygulamadan ziyade; **uygulamanın geliştirilmesi, containerize edilmesi, test edilmesi, Kubernetes ortamında yönetilmesi, AWS üzerinde çalıştırılması ve CI/CD süreçlerinin uygulanmasını kapsayan uygulamalı bir Cloud-Native DevOps projesine** dönüştürüldü.

