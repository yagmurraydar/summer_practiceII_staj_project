# Ubuntu 22.04 Sunucu Güvenlik Yapılandırması

## 1. Sunucunun Ayağa Kaldırılması

Yerel Ubuntu 22.04 ortamında sunucu kurulumu tamamlandı ve sistem çalışır duruma getirildi.

Sunucu, Oracle VirtualBox üzerinde çalışan eğitim amaçlı bir sanal makine olarak yapılandırıldı.

---

## 2. SSH Anahtarlarının Oluşturulması

SSH ile güvenli bağlantı kurabilmek için **Ed25519** algoritması kullanılarak public/private anahtar çifti oluşturuldu.

SSH anahtarı, sunucuya bağlanılacak olan **host makine üzerinde** oluşturuldu:

```bash
ssh-keygen -t ed25519
```

Host makinede oluşturulan anahtarlar:

```text
C:\Users\Huawei\.ssh\id_ed25519
C:\Users\Huawei\.ssh\id_ed25519.pub
```

Burada:

* `id_ed25519` → **Private Key**
* `id_ed25519.pub` → **Public Key**

Private key yalnızca host makinede tutuldu ve sanal makineye kopyalanmadı.

Public key'in içeriği Windows üzerinde aşağıdaki komut ile görüntülendi:

```cmd
type %USERPROFILE%\.ssh\id_ed25519.pub
```

> **Güvenlik notu:** Private key (`id_ed25519`) hiçbir zaman paylaşılmamalı veya sunucuya kopyalanmamalıdır. Yalnızca public key (`id_ed25519.pub`) sunucuya eklenmelidir.

---

## 3. `rain` Kullanıcısı İçin SSH Yetkilendirmesi

Ubuntu sanal makinesinde `rain` kullanıcısının SSH yapılandırması kontrol edildi.

Kullanıcının SSH klasörü:

```bash
sudo ls -la /home/rain/.ssh
```

SSH anahtar doğrulaması için `authorized_keys` dosyası kullanıldı:

```text
/home/rain/.ssh/authorized_keys
```

Host makinede oluşturulan yeni public key, mevcut `authorized_keys` dosyasının üzerine yazılmadan **yeni bir satır olarak** eklendi.

Dosya içerisinde public key'ler ayrı satırlarda tutulmaktadır:

```text
ssh-ed25519 AAAA... eski-public-key
ssh-ed25519 AAAA... yeni-public-key
```

SSH dizini ve dosya izinleri güvenli olacak şekilde yapılandırıldı:

```bash
sudo chmod 700 /home/rain/.ssh
sudo chmod 600 /home/rain/.ssh/authorized_keys
sudo chown -R rain:rain /home/rain/.ssh
```

---

## 4. SSH Servisinin Kontrol Edilmesi

SSH servisinin çalışır durumda olduğu kontrol edildi:

```bash
sudo systemctl status ssh --no-pager
```

Servisin aktif olduğu doğrulandı:

```text
Active: active (running)
```

SSH sunucusu 22 numaralı port üzerinden bağlantı kabul edecek şekilde çalışmaktadır.

---

## 5. SSH Bağlantısının Test Edilmesi

Host makineden Ubuntu sanal makinesine `rain` kullanıcısı ile SSH bağlantısı gerçekleştirildi.

Bağlantı komutu:

```bash
ssh rain@<VM_IP>
```

Bağlantı başarıyla gerçekleştirildi ve aşağıdaki kullanıcı istemi elde edildi:

```text
rain@yagmuraydar-VirtualBox:~$
```

Bu test sonucunda:

* Host makinedeki private key'in kullanılabildiği,
* VM üzerinde karşılık gelen public key'in `authorized_keys` içerisinde bulunduğu,
* SSH servisinin çalıştığı,
* `rain` kullanıcısı ile SSH bağlantısının başarılı olduğu

doğrulandı.

---

## 6. VM İçindeki Eski SSH Anahtarlarının Temizlenmesi

Daha önce VM içerisinde `rain` kullanıcısı için oluşturulmuş olan eski SSH key-pair tespit edildi:

```text
/home/rain/.ssh/id_ed25519
/home/rain/.ssh/id_ed25519.pub
```

Yeni yapılandırmada private key'in yalnızca host makinede tutulması amaçlandığından, VM içerisindeki eski key-pair gereksiz hale geldi.

Başarılı SSH bağlantısı doğrulandıktan sonra eski key-pair aşağıdaki komutlarla silindi:

```bash
rm ~/.ssh/id_ed25519 ~/.ssh/id_ed25519.pub
```

> `authorized_keys` dosyası silinmemelidir. SSH public key doğrulaması bu dosya üzerinden gerçekleştirilmektedir.

Son durumda VM içerisinde private key bulunmaması ve yalnızca gerekli public key bilgilerinin `authorized_keys` içerisinde tutulması hedeflenmiştir.

---

## 7. SSH Yapılandırmasında Parola ile Girişin Kapatılması

SSH üzerinden parola ile giriş yapılmasını engellemek amacıyla SSH yapılandırma dosyası düzenlenebilir:

```bash
sudo nano /etc/ssh/sshd_config
```

Aşağıdaki ayarın kullanılması planlanmaktadır:

```text
PasswordAuthentication no
```

Bu ayar etkinleştirildiğinde SSH üzerinden kullanıcı doğrulaması için parola yerine SSH anahtarı kullanılması sağlanır.

> Bu ayar etkinleştirilmeden önce public key ile SSH bağlantısının başarıyla çalıştığından emin olunmalıdır. Aksi durumda sunucuya uzaktan erişim kaybedilebilir.

---

## 8. Root Girişinin Kapatılması

Sunucu güvenliğini artırmak amacıyla root kullanıcısının SSH üzerinden doğrudan girişinin engellenmesi planlanmaktadır.

SSH yapılandırma dosyasında:

```bash
sudo nano /etc/ssh/sshd_config
```

aşağıdaki ayar kullanılabilir:

```text
PermitRootLogin no
```

Bu ayarın amacı:

* Root hesabının doğrudan hedef alınmasını engellemek,
* Brute-force saldırılarının etkisini azaltmak,
* SSH üzerinden yetkisiz root erişimini önlemektir.

---

## 9. UFW (Uncomplicated Firewall) Yapılandırması

Sunucu güvenliğini artırmak amacıyla UFW firewall yapılandırması kullanılabilir.

Kurulum:

```bash
sudo apt install ufw
```

SSH bağlantısının kesilmemesi için öncelikle SSH portu açılmalıdır:

```bash
sudo ufw allow 22/tcp
```

Web sunucusu kullanılacaksa gerekli portlar:

```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
```

Açık bırakılan portlar:

| Port | Açıklama                            |
| ---- | ----------------------------------- |
| 22   | SSH ile uzaktan güvenli bağlantı    |
| 80   | HTTP üzerinden web erişimi          |
| 443  | HTTPS üzerinden güvenli web erişimi |

Firewall etkinleştirilmeden önce mevcut kurallar kontrol edilmelidir:

```bash
sudo ufw status
```

Gerekli kurallar tanımlandıktan sonra:

```bash
sudo ufw enable
```

> SSH ile uzaktan bağlıyken UFW etkinleştirilmeden önce 22 numaralı SSH portunun izinli olduğundan mutlaka emin olunmalıdır.

---

## Sonuç

Bu çalışma kapsamında Ubuntu 22.04 sanal sunucusunda temel SSH güvenlik yapılandırması gerçekleştirilmiştir.

Gerçekleştirilen işlemler:

* Ed25519 algoritması ile SSH anahtar çifti oluşturuldu.
* Private key **host makinede tutuldu**.
* Private key VM'e kopyalanmadı.
* Host makinedeki public key, VM'deki `rain` kullanıcısının `authorized_keys` dosyasına eklendi.
* `~/.ssh` ve `authorized_keys` dosyalarının izinleri güvenli şekilde yapılandırıldı.
* SSH servisinin aktif ve çalışır durumda olduğu doğrulandı.
* Host makineden `rain` kullanıcısına SSH bağlantısı başarıyla gerçekleştirildi.
* VM içerisinde bulunan eski SSH key-pair'in kaldırılmasıyla private key'in yalnızca host makinede tutulması sağlandı.
* Parola ile SSH girişinin kapatılması ve root SSH erişiminin engellenmesi güvenlik yapılandırmasının sonraki adımları olarak belirlendi.
* UFW firewall yapılandırması için gerekli portlar belirlendi.

### Son SSH mimarisi

```text
HOST MAKİNE
│
└── C:\Users\Huawei\.ssh\
    ├── id_ed25519       ← PRIVATE KEY
    └── id_ed25519.pub   ← PUBLIC KEY
             │
             │ SSH
             ▼
UBUNTU 22.04 VM
│
└── /home/rain/.ssh/
    └── authorized_keys  ← PUBLIC KEY
```

Bu yapı sayesinde **private key host makineden dışarı çıkarılmadan**, SSH public-key authentication kullanılarak Ubuntu sanal makinesine güvenli bağlantı sağlanmıştır.

## 10. Networking Temelleri

### IPv4 ve CIDR Notasyonu

Bir IPv4 adresi toplam **32 bit**'ten oluşur. Bu 32 bit, 4 grup halinde gösterilir ve her grup **8 bit (1 octet)** içerir.

Örneğin:

```text
192.168.1.122
```

Her octet 0–255 arasında bir değer alabilir.

### `/24` Ne Anlama Geliyor?

`/24`, IPv4 adresindeki **ilk 24 bitin network kısmı**, kalan **8 bitin ise host kısmı** olduğunu belirtir.

```text
32 bit = 24 bit network + 8 bit host
```

24 bit = 3 × 8 bit olduğundan:

```text
192.168.1.122
│       │   │
└───────┴───┴── Network
            └── Host
```

Daha basit şekilde:

```text
192.168.1 | 122
 Network  | Host
```

Bu nedenle `192.168.1.0/24` ağı:

```text
192.168.1.0
     ↓
192.168.1.255
```

aralığındaki toplam **256 adresi** kapsar.

Ancak bu 256 adresin tamamı cihazlara atanamaz.

* `192.168.1.0` → **Network adresi**
* `192.168.1.1` – `192.168.1.254` → **Kullanılabilir host adresleri**
* `192.168.1.255` → **Broadcast adresi**

Dolayısıyla:

```text
256 toplam adres - 2 özel adres = 254 kullanılabilir host
```

### Network Adresi

Network adresi, subnet'i tanımlayan **ilk adrestir**.

Örneğin:

```text
192.168.1.0/24
```

için:

```text
Network adresi = 192.168.1.0
```

Bu adres normal bir cihaza atanmaz; ağı temsil eder.

### Broadcast Adresi

Broadcast adresi, aynı subnet içerisindeki **tüm cihazlara aynı anda mesaj göndermek** için kullanılır.

`192.168.1.0/24` için broadcast adresi:

```text
192.168.1.255
```

Bu adres de normal bir cihaza atanamaz.

Örneğin bir cihaz broadcast mesajı gönderdiğinde mesaj subnet içerisindeki tüm cihazlara ulaşabilir.

> **Not:** DHCP'nin ilk aşamasında istemci henüz kendi IP adresini bilmediği için DHCP Discover mesajını broadcast olarak gönderebilir. DHCP sunucusu veya router bu isteği alarak istemciye IP adresi sağlayabilir.

### Router'ın IP Adresi

Router da subnet içerisinde normal bir cihaz gibi kendisine ait bir IP adresine sahip olabilir.

Örneğin:

```text
Network:   192.168.1.0/24
Router:    192.168.1.1
```

`192.168.1.1` adresinin router'a verilmesi **zorunlu değildir**. Ancak ilk kullanılabilir adresin gateway/router için kullanılması oldukça yaygın bir uygulamadır.

---

## `/25` Subnet Örneği

`/24` yerine `/25` kullanıldığında network kısmı büyür ve host kısmı küçülür.

```text
32 bit = 25 bit network + 7 bit host
```

Host kısmında **7 bit** kaldığı için toplam adres sayısı:

```text
2⁷ = 128
```

olur.

Bu 128 adresin:

* 1 tanesi network adresi
* 1 tanesi broadcast adresi
* 126 tanesi kullanılabilir host adresidir.

Dolayısıyla:

```text
128 - 2 = 126 kullanılabilir host
```

### CIDR Sayısı Arttıkça Ne Olur?

CIDR değeri arttıkça network kısmı büyür, host kısmı küçülür.

Örneğin:

```text
/24 → 8 host biti
/25 → 7 host biti
/26 → 6 host biti
```

Host biti azaldıkça subnet içerisinde bulunabilecek cihaz sayısı da azalır.

Genel formül:

```text
Toplam adres sayısı = 2^(host bit sayısı)

Kullanılabilir host sayısı = 2^(host bit sayısı) - 2
```

Buradaki `-2`, network ve broadcast adresleri içindir.

### CIDR Karşılaştırması

| CIDR  | Network Bit Sayısı | Host Bit Sayısı | Toplam Adres | Kullanılabilir Host |
| ----- | ------------------ | --------------- | ------------ | ------------------- |
| `/24` | 24                 | 8               | 256          | 254                 |
| `/25` | 25                 | 7               | 128          | 126                 |
| `/26` | 26                 | 6               | 64           | 62                  |
| `/27` | 27                 | 5               | 32           | 30                  |
| `/28` | 28                 | 4               | 16           | 14                  |

> **Önemli:** CIDR sayısının artması subnet'in küçülmesi anlamına gelir. Örneğin `/28`, `/24`'ten daha küçük bir subnet'tir.

### AWS VPC ile İlişkisi

Bu subnet mantığı AWS VPC tasarımında da kullanılır.

Örneğin:

```text
VPC
│
├── Public Subnet
│   └── Web Server
│
├── Private Subnet
│   └── Application Server
│
└── Database Subnet
    └── Database Server
```

Her subnet için uygun bir CIDR aralığı belirlenir.

Küçük bir subnet az sayıda kaynak barındırmak için yeterli olabilirken, daha fazla kaynak barındıracak bir subnet için daha geniş bir adres aralığı gerekir.

Bu nedenle subnet tasarımında **kaç cihaz veya kaynak barındırılacağı** dikkate alınarak uygun CIDR değeri seçilir.
