# AWS Networking ve Güvenlik Notları

## 1. VPC ve CIDR Mantığı

AWS'de VPC (Virtual Private Cloud), AWS kaynaklarının çalışacağı izole sanal ağ ortamıdır.

VPC oluştururken bir IP adres aralığı belirlenir. Bu aralık CIDR gösterimi ile ifade edilir.

Örneğin:

```text
10.0.0.0/16
```

Buradaki `/16`, IPv4 adresinin ilk 16 bitinin network kısmı olduğunu belirtir.

Bir VPC içerisindeki IP adres alanı daha küçük subnet'lere bölünebilir.

Örneğin:

```text
VPC:           10.0.0.0/16
Public subnet: 10.0.1.0/24
Private subnet:10.0.2.0/24
```

`/24` subnet içerisinde 256 IP adreslik bir adres alanı oluşturur. AWS bazı IP adreslerini kendisi ayırdığı için kullanılabilir adres sayısı 256'dan daha azdır.

---

## 2. Public Subnet Neden Internet Gateway ve Route Table Gerektirir?

Bir subnet'in public olması yalnızca subnet'e "public" adının verilmesiyle gerçekleşmez.

Internet üzerinden erişim sağlayabilmek için ağ trafiğinin internete ulaşabileceği bir yol tanımlanmalıdır.

Temel yapı:

```text
Internet
   |
Internet Gateway (IGW)
   |
Route Table
   |
Public Subnet
   |
EC2
```

Route Table içerisinde internete giden trafik için bir route bulunur:

```text
0.0.0.0/0 → Internet Gateway
```

Buradaki `0.0.0.0/0`, hedefi belirtilmeyen tüm IPv4 trafiğini ifade eder.

Dolayısıyla public subnet için temel olarak:

* VPC
* Subnet
* Internet Gateway
* Route Table
* Route Table'ın subnet ile ilişkilendirilmesi

gibi bileşenlerin doğru şekilde yapılandırılması gerekir.

Ayrıca EC2'nin internete doğrudan erişebilmesi için public IPv4 adresi gibi ek koşullar da gerekir.

---

## 3. Security Group ve UFW

AWS Security Group ile Ubuntu'daki UFW benzer bir amaca hizmet eder: ağ trafiğini kontrol etmek.

### Security Group

Security Group AWS seviyesinde çalışır ve EC2 gibi kaynakların gelen/giden trafiğini kontrol eder.

Örneğin SSH için:

```text
TCP
Port: 22
Source: belirli IP veya IP aralığı
```

HTTP için:

```text
TCP
Port: 80
Source: 0.0.0.0/0
```

gibi kurallar tanımlanabilir.

### UFW

UFW ise Ubuntu işletim sistemi içerisindeki firewall yönetim aracıdır.

Örneğin:

```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw status
```

komutlarıyla işletim sistemi seviyesinde trafik kontrol edilir.

### Farkları

Security Group:

* AWS seviyesinde çalışır.
* EC2'nin ağ erişimini kontrol eder.
* AWS kaynağına bağlıdır.

UFW:

* Ubuntu işletim sistemi seviyesinde çalışır.
* İşletim sisteminin firewall kurallarını kontrol eder.

Bu nedenle ikisi birbirinin alternatifi değildir. Aynı sunucuda hem Security Group hem de UFW kullanılabilir.

Örneğin SSH bağlantısının çalışması için:

```text
Internet
   ↓
AWS Security Group → TCP 22 izinli
   ↓
EC2
   ↓
Ubuntu UFW → TCP 22 izinli
   ↓
SSH Server
```

zincirinin uygun olması gerekir.

---

## 4. IAM ve Root Kullanıcısı

AWS hesabının oluşturulmasıyla birlikte bir root kullanıcı bulunur.

Root kullanıcı AWS hesabındaki en yüksek yetkiye sahip hesaptır ve günlük işlemler için kullanılmaması önerilir.

IAM (Identity and Access Management) ise AWS kaynaklarına erişebilecek kullanıcıları, grupları, roller ve izin politikalarını yönetmek için kullanılır.

Örneğin bir IAM kullanıcısına yalnızca belirli AWS servislerine erişim verilebilir.

Temel yaklaşım:

```text
Root Account
     |
     └── IAM Users / Roles
              |
              └── Policies / Permissions
```

Root hesabı yerine günlük AWS işlemlerinde uygun yetkilere sahip IAM kullanıcılarının veya rollerin kullanılması daha güvenlidir.

Bu projede de AWS işlemleri için IAM kullanıcı ve MFA yapılandırması kullanılmıştır.

---

## 5. Öğrenilen Temel Yapı

Bu çalışmada AWS networking yapısının temel parçaları birlikte ele alınmıştır:

```text
VPC
 |
 +-- Subnet
 |     |
 |     +-- EC2
 |
 +-- Route Table
 |       |
 |       +-- 0.0.0.0/0 → Internet Gateway
 |
 +-- Internet Gateway
 |
 +-- Security Group
         |
         +-- TCP 22 → SSH
         +-- TCP 80 → HTTP
```

Bu yapı sayesinde AWS üzerindeki EC2 sunucusunun ağ bağlantısı ve erişim kuralları kontrol edilebilir.
