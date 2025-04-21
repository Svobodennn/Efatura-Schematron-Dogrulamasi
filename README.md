# Fatura Schematron Doğrulayıcı

XML faturalarını Schematron kurallarına göre doğrulamak için Python tabanlı bir araç. UBL-TR (Universal Business Language - Türkçe) e-fatura formatını destekler.

## Özellikler

- XML faturalarını özel Schematron kurallarına göre doğrular
- UBL-TR e-fatura formatını destekler
- Detaylı doğrulama hata mesajları sağlar
- Ek doğrulama kuralları ile kolayca genişletilebilir
- Türk e-fatura gereksinimlerine uygun doğrulama

## Kurulum

1. Bu depoyu klonlayın
2. Gerekli bağımlılıkları yükleyin:
```bash
pip install -r requirements.txt
```

## Kullanım

Doğrulayıcıyı şu şekilde çalıştırın:
```bash
python invoice_validator.py <schematron_dosyası> <xml_dosyası>
```

Örnek:
```bash
python invoice_validator.py UBL-TR_Main_Schematron.xml fatura.xml
```

## Schematron Kuralları

UBL-TR Schematron kuralları (`UBL-TR_Main_Schematron.xml`) şunları doğrular:
- Temel fatura yapısı ve zorunlu alanlar
- Vergi kimlik numarası (VKN) ve TC Kimlik numarası (TCKN) doğrulaması
- Tutar ve vergi hesaplamaları
- Tarih formatı ve geçerliliği
- İmza doğrulaması
- UBL-TR özel alanları ve kodları

## Kuralları Özelleştirme

İhtiyaçlarınıza göre UBL-TR Schematron dosyasını değiştirerek doğrulama kurallarını ekleyebilir veya değiştirebilirsiniz. Kurallar standart Schematron formatında yazılmıştır.

## Örnek Dosyalar

- `UBL-TR_Main_Schematron.xml`: UBL-TR e-fatura doğrulama kurallarını içerir
- `sample_invoice.xml`: Test için örnek bir UBL-TR XML fatura

## Gereksinimler

- Python 3.6+
- lxml
- pyschematron

## UBL-TR E-Fatura Gereksinimleri

Bu doğrulayıcı, Türkiye'deki e-fatura gereksinimlerini karşılamak için tasarlanmıştır:
- GİB (Gelir İdaresi Başkanlığı) e-fatura formatı desteği
- UBL-TR şema ve kod listeleri desteği
- Türk e-fatura yönetmeliğine uygun doğrulama kuralları 