# Smart System Monitor MVP

Modern, hafif ve AI gerektirmeyen bir sistem monitörü MVP'si. 

Özellikler:
- CPU, GPU, RAM, SSD/HD durum takibi
- Mini grafikler ve durum göstergeleri
- Temel uyarı sistemi
- Türkçe / İngilizce dil desteği
- Minimal taskbar benzeri compact widget
- Disk sağlık ve kullanım bilgileri
- Basit PC Health Score hesaplaması

## Kurulum

```bash
cd e:\SystemMonitorMVP
python -m pip install -r requirements.txt
python app.py
```

## Notlar

- Donanım sensörleri mevcut değilse uygulama otomatik olarak güvenli bir demo / fallback değerler üretir.
- GPU bilgisi için `nvidia-smi` varsa gerçek veriyi kullanır; yoksa demo değerler devreye girer.
- SSD sağlık bilgisi, `smartctl` veya benzeri araç varsa gerçek değerler okunur; yoksa güvenli tahminle gösterilir.

## Diller

Uygulamanın üst barındaki dil butonuyla Türkçe / English geçiş yapılabilir.
