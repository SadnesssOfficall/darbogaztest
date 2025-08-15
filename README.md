
# Darboğaz Test Aracı

Bu Python betiği, sisteminizde işlemci (CPU) ve ekran kartı (GPU) kullanımlarını izleyerek darboğaz (bottleneck) olup olmadığını tespit eder.
Test süresi boyunca veriler kaydedilir ve test sonunda yüzdesel bir darboğaz analizi yapılır.

## Özellikler
- CPU ve GPU kullanımını belirli aralıklarla ölçer.
- Test süresi ve ölçüm aralığı komut satırından ayarlanabilir.
- Test bitiminde renkli konsol çıktısı ile sonuç verir.
- Logları `.csv` formatında kaydeder.
- Darboğaz yüzdesini hesaplar ve test sonunda gösterir.

## Kullanım

```bash
python main.py --duration 60 --interval 1 --log logs.csv
```

- `--duration`: Test süresi (saniye cinsinden)
- `--interval`: Ölçüm aralığı (saniye cinsinden)
- `--log`: Kaydedilecek log dosyası adı

## Gereksinimler
- Python 3.8+
- psutil
- GPUtil
- colorama

Gerekli kütüphaneleri yüklemek için:
```bash
pip install psutil gputil colorama
```

## Örnek Çıktı
```
[CPU] %75.3
[GPU] %52.1
Darboğaz: CPU ağırlıklı (%62)
Log kaydedildi: logs.csv
```

## Lisans
Bu proje açık kaynaklıdır ve MIT lisansı ile lisanslanmıştır.
